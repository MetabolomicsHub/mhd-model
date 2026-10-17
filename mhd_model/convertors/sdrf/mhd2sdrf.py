import json
import logging
from collections import OrderedDict
from pathlib import Path

from mhd_model.model.v1_0.dataset.profiles.base import graph_nodes
from mhd_model.model.v1_0.dataset.profiles.base.graph_nodes import CvTermValueObject
from mhd_model.model.v1_0.dataset.profiles.legacy.profile import (
    MhDatasetLegacyProfile_v1_0,
)
from mhd_model.model.v1_0.sdrf.model import (
    LegacySdrf,
    LegacySdrfRow,
    SdrfFile,
    SdrfKeyValue,
    SdrfSampleProtocolDefinition,
)
from mhd_model.shared.base import BasicValueModel, CvTerm
from mhd_model.shared.model import (
    IdentifiableMhdModel,
    MhdModelValidationContext,
    MhdNode,
    MhdRelationship,
)

logger = logging.getLogger(__name__)

REQUIRED_COLUMNS = [
    "source name",
    "assay name",
    "characteristics[organism]",
    "characteristics[organism part]",
    "characteristics[biological replicate]",
    "technology type",
    "comment[instrument]",
    "comment[ion source]",
    "comment[scan polarity]",
    "comment[acquisition method]",
    "comment[technical replicate]",
    "comment[data file]",
]
RECOMMENDED_COLUMNS = [
    "characteristics[cell type]",
    "characteristics[disease]",
    "comment[metabolite assignment file]",
    "comment[extraction method]",
    "comment[analyte class]",
    "comment[sample matrix]",
]

OPTIONAL_COLUMNS = [
    "characteristics[tissue supergroup]",
    "characteristics[pooled sample]",
    "characteristics[sample type]",
    "characteristics[material type]",
    "characteristics[tissue mass]",
    "characteristics[biosample accession number]",
    "characteristics[sampling time]",
    "characteristics[treatment]",
    "characteristics[synthetic peptide]",
    "characteristics[spiked compound]",
    "characteristics[enrichment process]",
    "comment[extraction solvent]",
    "comment[internal standard]",
    "comment[sample preparation batch]",
    "comment[lc batch]",
    "comment[acquisition date]",
    "comment[ms2 mass analyzer]",
    "comment[ms min mz]",
    "comment[ms max mz]",
    "comment[ms1 scan range]",
    "comment[ms2 scan range]",
    "comment[precursor mass tolerance]",
    "comment[fragment mass tolerance]",
    "comment[collision energy]",
    "comment[raw data file md5]",
    "comment[processed data file]",
    "comment[processed data file md5]",
    "comment[metabolite assignment file md5]",
]

ALL_MANAGED_HEADERS = REQUIRED_COLUMNS.copy()
ALL_MANAGED_HEADERS.extend(RECOMMENDED_COLUMNS)
ALL_MANAGED_HEADERS.extend(OPTIONAL_COLUMNS)


def create_sdrf_files(
    mhd_file_path: str,
    sdrf_file_root_path: str,
    assay_name: None | str = None,
    sdrf_output_filename: None | str = None,
):
    sdrf_files = []
    txt = Path(mhd_file_path).read_text()
    mhd_data_json = json.loads(txt)
    context = MhdModelValidationContext(
        dataset_configuration=MhDatasetLegacyProfile_v1_0.get_config()
    )

    mhd_dataset = MhDatasetLegacyProfile_v1_0.model_validate(
        mhd_data_json, context=context
    )
    nodes_map: dict[str, IdentifiableMhdModel] = {
        x.id_: x for x in mhd_dataset.graph.nodes
    }
    # relationships_map: dict[str, MhdRelationship] = {
    #     x.id_: x for x in mhd_dataset.graph.relationships
    # }

    all_nodes_map: dict[str, MhdNode] = {}
    type_map: dict[str, dict[str, MhdNode]] = {}
    for node in mhd_dataset.graph.nodes:
        if node.type_ not in type_map:
            type_map[node.type_] = {}
        type_map[node.type_][node.id_] = node
        all_nodes_map[node.id_] = node

    relationship_name_map: dict[str, dict[str, MhdRelationship]] = {}
    all_relationships: dict[str, dict[str, list[MhdRelationship]]] = {}
    node_relationships: dict[str, dict[str, list[str]]] = {}

    for rel in mhd_dataset.graph.relationships:
        if rel.relationship_name not in all_relationships:
            all_relationships[rel.relationship_name] = {}
        sources = all_relationships[rel.relationship_name]

        if rel.source_ref not in sources:
            sources[rel.source_ref] = {}
        targets = sources[rel.source_ref]

        if rel.target_ref not in targets:
            targets[rel.target_ref] = []
        targets[rel.target_ref].append(rel)

        if rel.relationship_name not in relationship_name_map:
            relationship_name_map[rel.relationship_name] = {}
        relationship_name_map[rel.relationship_name][rel.id_] = rel
        if rel.source_ref not in node_relationships:
            node_relationships[rel.source_ref] = {}
        if rel.relationship_name not in node_relationships[rel.source_ref]:
            node_relationships[rel.source_ref][rel.relationship_name] = []
        node_relationships[rel.source_ref][rel.relationship_name].append(rel.target_ref)

    if "study" not in type_map or not type_map["study"]:
        logger.error("Study is not found for in the input file")
        return False, sdrf_files
    study: graph_nodes.Study = next(iter(type_map["study"].values()))
    study_id = study.mhd_identifier or study.repository_identifier
    study_assays: list[graph_nodes.Assay] = []
    if "assay" in type_map:
        study_assays = list(type_map["assay"].values())
    if not study_assays:
        logger.error("Study %s has no assay", study_id)
        return False, sdrf_files
    selected_assays = [(idx, x) for idx, x in enumerate(study_assays, start=1)]
    if assay_name:
        selected_assays = [
            (idx, x)
            for idx, x in enumerate(study_assays, start=1)
            if x.name == assay_name
        ]
    if not selected_assays:
        logger.error("Study %s has no assay with name %s", study_id, assay_name)
        return False, sdrf_files
    assay_sample_runs = {}
    for idx, assay in selected_assays:
        sample_run_links = [
            v
            for k, v in relationship_name_map.get("has-sample-run", {}).items()
            if v.source_ref == assay.id_
        ]

        sample_run_links.sort(
            key=lambda x: x.tag_list[0].value if x.tag_list and x.tag_list[0] else -1
        )
        if sample_run_links:
            assay_sample_runs[assay.id_] = sample_run_links

    if not sample_run_links:
        sample_run_links = [
            v
            for k, v in relationship_name_map.get("has-sample-run", {}).items()
            if v.source_ref == assay.id_
        ]
        if sample_run_links and selected_assays:
            assay = selected_assays[0][1]
            assay_sample_runs[assay.id_] = sample_run_links

    for idx, assay in selected_assays:
        if assay.id_ not in assay_sample_runs:
            continue
        sample_run_links = assay_sample_runs[assay.id_]
        if not sample_run_links:
            logger.error("Study %s Assay '%s' has no sample run", study_id, assay.name)
            continue
        technology_type_node = nodes_map[assay.technology_type_ref]
        technology_type_node_str = (
            f"NT={technology_type_node.name};AC={technology_type_node.accession}"
            if technology_type_node.accession
            else technology_type_node.name
        )
        sdrf_file = LegacySdrf(
            study_identifier=study.repository_identifier,
            assay_identifier=assay.repository_identifier or str(idx),
        )
        parameter_type_cv_terms: dict[str, CvTerm] = {}

        for sample_run_link in sample_run_links:
            sample_run: graph_nodes.SampleRun = all_nodes_map[
                sample_run_link.target_ref
            ]
            sample: graph_nodes.Sample = all_nodes_map[sample_run.sample_ref]
            biosample_accession = sample.biosample_accession or None
            subjects = find_all_linked_nodes(
                all_nodes_map,
                node_relationships,
                sample.id_,
                "derived-from",
                "subject",
            )
            subject = subjects[0] if subjects else None
            if subject:
                values: list[IdentifiableMhdModel] = find_all_linked_nodes(
                    all_nodes_map,
                    node_relationships,
                    subject.id_,
                    "has-characteristic-value",
                    "characteristic-value",
                )
                characteristic_values = []
                if values:
                    for value in values:
                        characteristic_types = find_all_linked_nodes(
                            all_nodes_map,
                            node_relationships,
                            value.id_,
                            "has-type",
                            "characteristic-type",
                        )
                        characteristic_type = (
                            characteristic_types[0] if characteristic_types else None
                        )
                        if characteristic_type:
                            target_value = None
                            if (
                                isinstance(value, CvTermValueObject)
                                and value.value is not None
                                and value.name is None
                            ):
                                target_value = BasicValueModel.model_validate(
                                    value.model_dump(by_alias=True)
                                )
                            else:
                                target_value = CvTerm.model_validate(
                                    value.model_dump(by_alias=True)
                                )
                            characteristic_values.append(
                                SdrfKeyValue(
                                    key=CvTerm.model_validate(
                                        characteristic_type.model_dump(by_alias=True)
                                    ),
                                    value=target_value,
                                )
                            )
                values: list[IdentifiableMhdModel] = find_all_linked_nodes(
                    all_nodes_map,
                    node_relationships,
                    sample.id_,
                    "has-factor-value",
                    "factor-value",
                )
                factor_values = []
                if values:
                    for value in values:
                        # select only first type
                        factor_types = find_all_linked_nodes(
                            all_nodes_map,
                            node_relationships,
                            value.id_,
                            "has-type",
                            "factor-type",
                        )
                        factor_type = factor_types[0] if factor_types else None
                        if factor_type:
                            target_value = None
                            if (
                                isinstance(value, CvTermValueObject)
                                and value.value is not None
                                and value.name is None
                            ):
                                target_value = BasicValueModel.model_validate(
                                    value.model_dump(by_alias=True)
                                )
                            else:
                                target_value = CvTerm.model_validate(
                                    value.model_dump(by_alias=True)
                                )
                            factor_values.append(
                                SdrfKeyValue(
                                    key=CvTerm.model_validate(
                                        factor_type.model_dump(by_alias=True)
                                    ),
                                    value=target_value,
                                )
                            )
            raw_data_files = []
            derived_data_files = []
            result_files = []
            supplementary_files = []
            if sample_run.raw_data_file_refs:
                raw_data_file_nodes: graph_nodes.RawDataFile = [
                    nodes_map[x] for x in sample_run.raw_data_file_refs
                ]
                raw_data_files = [
                    SdrfFile(name=x.name, url_list=x.url_list if x.url_list else None)
                    for x in raw_data_file_nodes
                ]
            if sample_run.derived_data_file_refs:
                derived_data_file_nodes: graph_nodes.DerivedDataFile = [
                    nodes_map[x] for x in sample_run.derived_data_file_refs
                ]
                derived_data_files = [
                    SdrfFile(name=x.name, url_list=x.url_list if x.url_list else None)
                    for x in derived_data_file_nodes
                ]
            if sample_run.result_file_refs:
                result_file_nodes: graph_nodes.ResultFile = [
                    nodes_map[x] for x in sample_run.result_file_refs
                ]
                result_files = [
                    SdrfFile(name=x.name, url_list=x.url_list if x.url_list else None)
                    for x in result_file_nodes
                ]
            if sample_run.supplementary_file_refs:
                supplementary_file_nodes: graph_nodes.SupplementaryFile = [
                    nodes_map[x] for x in sample_run.supplementary_file_refs
                ]
                supplementary_files = [
                    SdrfFile(name=x.name, url_list=x.url_list if x.url_list else None)
                    for x in supplementary_file_nodes
                ]
            protocol_parameters = []

            if sample_run.sample_run_configuration_refs:
                run_configs: graph_nodes.SampleRunConfiguration = [
                    nodes_map[x] for x in sample_run.sample_run_configuration_refs
                ]
                for run_config in run_configs:
                    protocol = nodes_map[run_config.protocol_ref]
                    protocol_type = nodes_map[protocol.protocol_type_ref]
                    protocol_name = protocol.name
                    if run_config.parameter_value_refs:
                        parameter_value_nodes = [
                            nodes_map[x] for x in run_config.parameter_value_refs
                        ]
                        parameter_values = []
                        for value in parameter_value_nodes:
                            parameter_types: list[IdentifiableMhdModel] = (
                                find_all_linked_nodes(
                                    all_nodes_map,
                                    node_relationships,
                                    value.id_,
                                    "has-type",
                                    "parameter-type",
                                )
                            )
                            if parameter_types:
                                parameter_type = parameter_types[0]
                                if parameter_type.id_ not in parameter_type_cv_terms:
                                    parameter_type_cv_terms[parameter_type.id_] = (
                                        CvTerm.model_validate(
                                            parameter_type.model_dump(by_alias=True)
                                        )
                                    )
                                target_value = None
                                if (
                                    isinstance(value, CvTermValueObject)
                                    and value.value is not None
                                    and value.name is None
                                ):
                                    target_value = BasicValueModel.model_validate(
                                        value.model_dump(by_alias=True)
                                    )
                                else:
                                    target_value = CvTerm.model_validate(
                                        value.model_dump(by_alias=True)
                                    )
                                parameter_values.append(
                                    SdrfKeyValue(
                                        key=parameter_type_cv_terms[parameter_type.id_],
                                        value=target_value,
                                    )
                                )

                    protocol_parameters.append(
                        SdrfSampleProtocolDefinition(
                            protocol_name=protocol_name,
                            protocol_type=CvTerm.model_validate(
                                protocol_type.model_dump(by_alias=True)
                            ),
                            parameter_values=parameter_values,
                        )
                    )
            row = LegacySdrfRow(
                assay_name=sample_run.name or "",
                sample_name=sample.name or "",
                characteristics=characteristic_values,
                factors=factor_values,
                raw_data_files=raw_data_files,
                derived_data_files=derived_data_files,
                result_files=result_files,
                supplementary_files=supplementary_files,
                protocol_parameters=protocol_parameters,
                technology_type=technology_type_node_str,
                biosample_accession=biosample_accession,
            )
            sdrf_file.sample_runs.append(row)

        headers: OrderedDict[str, str] = OrderedDict()
        characteristic_definitions: list[IdentifiableMhdModel] = find_all_linked_nodes(
            all_nodes_map,
            node_relationships,
            study.id_,
            "has-characteristic-definition",
            "characteristic-definition",
        )
        headers["source name"] = None
        factor_headers = {}
        characteristic_headers = {}
        parameter_value_headers = {}

        for reqs in [REQUIRED_COLUMNS, RECOMMENDED_COLUMNS, OPTIONAL_COLUMNS]:
            for req in reqs:
                if req.startswith("characteristics["):
                    headers[req] = None

        characteristic_definitions.sort(key=lambda x: x.name)
        for definition in characteristic_definitions:
            definition_type = nodes_map[definition.characteristic_type_ref]
            name = (
                definition_type.name.lower()
                if definition_type.name
                else definition.name.lower()
            )
            header = get_sdrf_column_name(name, "characteristics")
            headers[header] = definition
            characteristic_headers[name] = header

        headers["assay name"] = None
        headers["technology type"] = None

        for reqs in [REQUIRED_COLUMNS, RECOMMENDED_COLUMNS, OPTIONAL_COLUMNS]:
            for req in reqs:
                if req.startswith("comment[") and "file" not in req:
                    headers[req] = None

        protocol_references = find_all_linked_nodes(
            all_nodes_map,
            node_relationships,
            assay.id_,
            relationship_name="follows",
            target_node_type="protocol",
        )
        if protocol_references:
            follows = [
                (k, v[0])
                for k, v in all_relationships.get("follows").get(assay.id_, {}).items()
            ]

            follows.sort(
                key=lambda x: (
                    x[1].tag_list[0].value
                    if x and x[1].tag_list and x[1].tag_list[0]
                    else -1
                )
            )
            protocols = [nodes_map[x] for x, _ in follows]
            for protocol_item in protocols:
                parameter_definitions: list[IdentifiableMhdModel] = (
                    find_all_linked_nodes(
                        all_nodes_map,
                        node_relationships,
                        protocol_item.id_,
                        "has-parameter-definition",
                        "parameter-definition",
                    )
                )
                if parameter_definitions:
                    for param in parameter_definitions:
                        parameter_type = nodes_map[param.parameter_type_ref]
                        name = (
                            parameter_type.name.lower()
                            if parameter_type.name
                            else param.name.lower()
                        )

                        header = get_sdrf_column_name(name, "comment")
                        headers[header] = definition
                        parameter_value_headers[name] = header

        max_raw_data_column = 0
        max_derived_data_column = 0
        max_result_data_column = 0
        max_supplementary_data_column = 0
        for row in sdrf_file.sample_runs:
            if row.raw_data_files:
                max_raw_data_column = max(max_raw_data_column, len(row.raw_data_files))
            if row.derived_data_files:
                max_derived_data_column = max(
                    max_derived_data_column, len(row.derived_data_files)
                )
            if row.result_files:
                max_result_data_column = max(
                    max_result_data_column, len(row.result_files)
                )
            if row.supplementary_files:
                max_supplementary_data_column = max(
                    max_supplementary_data_column, len(row.supplementary_files)
                )
        raw_files_data: list[list[tuple[str, str]]] = [[]] * max_raw_data_column
        derived_files_data: list[list[tuple[str, str]]] = [[]] * max_derived_data_column
        result_files_data: list[list[tuple[str, str]]] = [[]] * max_result_data_column
        supplementary_files_data: list[list[tuple[str, str]]] = [
            []
        ] * max_supplementary_data_column
        for name_prefix, files in [
            ("raw data file", raw_files_data),
            ("derived data file", derived_files_data),
            ("result file", result_files_data),
            ("supplementary file", supplementary_files_data),
        ]:
            for idx, item in enumerate(files, start=1):
                column_header, url_header = get_sdrf_file_column_name(idx, name_prefix)
                headers[column_header] = name
                headers[url_header] = url_header
        factor_definitions: list[IdentifiableMhdModel] = find_all_linked_nodes(
            all_nodes_map,
            node_relationships,
            study.id_,
            "has-factor-definition",
            "factor-definition",
        )
        factor_definitions.sort(key=lambda x: x.name)
        for definition in factor_definitions:
            definition_type = nodes_map[definition.factor_type_ref]
            name = (
                definition_type.name.lower()
                if definition_type.name
                else definition.name.lower()
            )
            header = get_sdrf_column_name(name, "factor value")
            headers[header] = definition
            factor_headers[name] = header

        tsv_data: OrderedDict[str, list[str]] = OrderedDict([(x, []) for x in headers])

        for row in sdrf_file.sample_runs:
            tsv_data.get("source name", []).append(row.sample_name or "")
            tsv_data.get("assay name", []).append(row.assay_name or "")
            tsv_data.get("technology type", []).append(row.technology_type)
            tsv_data.get("characteristics[biosample accession number]", []).append(
                row.biosample_accession or ""
            )

            filled_headers = {"source name", "assay name", "technology type"}
            all_param_value_definitions = []
            for item in row.protocol_parameters:
                all_param_value_definitions.extend(item.parameter_values)

            for items, item_headers in [
                (row.characteristics, characteristic_headers),
                (row.factors, factor_headers),
                (all_param_value_definitions, parameter_value_headers),
            ]:
                for item in items:
                    if item.key and item.key.name:
                        item_type = item.key.name.lower()
                        header = item_headers.get(item_type)
                        filled_headers.add(header)
                        if isinstance(item.value, BasicValueModel):
                            val = (
                                f"{item.value.value} {item.value.unit.name}"
                                if item.value
                                and item.value.unit
                                and item.value.unit.name
                                else item.value.value
                            )
                        else:
                            val = (
                                f"NT={item.value.name};AC={item.value.accession}"
                                if item.value.accession and item.value.name
                                else item.value.name
                            )
                        tsv_data.get(header, []).append(val or "")

            for name_prefix, files, values in [
                ("raw data file", raw_files_data, row.raw_data_files),
                ("derived data file", derived_files_data, row.derived_data_files),
                ("result file", result_files_data, row.result_files),
                (
                    "supplementary file",
                    supplementary_files_data,
                    row.supplementary_files,
                ),
            ]:
                for idx, item in enumerate(values, start=1):
                    if not item:
                        continue
                    header, url_header = get_sdrf_file_column_name(idx, name_prefix)

                    # header = f"comment[{name_prefix} name.{idx}]"
                    name_value = values[idx - 1].name or ""
                    tsv_data.get(header, []).append(name_value or "")
                    # url_header = f"comment[{name_prefix} url.{idx}]"
                    url_list = values[idx - 1].url_list
                    filled_headers.add(header)
                    url_value = ""
                    if url_list:
                        url_value = str(url_list[0])
                    tsv_data.get(url_header, []).append(url_value)
                    filled_headers.add(url_header)
            not_defined_headers = {x for x in tsv_data if x not in filled_headers}
            for header in not_defined_headers:
                if header in REQUIRED_COLUMNS:
                    tsv_data[header].append("not available")
                else:
                    tsv_data[header].append("")
        empty_columns = []
        exceptions = set(REQUIRED_COLUMNS)
        for header, values in tsv_data.items():
            if header in exceptions:
                continue
            unique_values = set(values)
            unique_values.discard("")
            unique_values.discard(None)
            if not unique_values:
                empty_columns.append(header)
        for item in empty_columns:
            del tsv_data[item]
        if empty_columns:
            logger.debug("Empty columns are dropped: %s", ", ".join(empty_columns))
        # assay_id = sdrf_file.assay_identifier

        if sdrf_output_filename and assay_name:
            sdrf_filename = sdrf_output_filename
        else:
            if assay.name.startswith(f"{study_id}_"):
                sdrf_filename = f"{Path(assay.name).stem}.sdrf.tsv"
            else:
                sdrf_filename = f"{study_id}_{Path(assay.name).stem}.sdrf.tsv"
        srdf_file_path = Path(sdrf_file_root_path) / Path(sdrf_filename)
        srdf_file_path.parent.mkdir(parents=True, exist_ok=True)
        sdrf_files.append(srdf_file_path)
        with srdf_file_path.open("w") as f:
            headers = "\t".join(list(tsv_data.keys())) + "\n"
            f.write(headers)
            row_count = len(tsv_data["source name"])
            for idx in range(row_count):
                row = [tsv_data[x][idx] for x in tsv_data]
                row_data = "\t".join(row) + "\n"
                f.write(row_data)
        logger.info("%s SDRF file is created: %s", study_id, str(srdf_file_path))

    return sdrf_files


SDRF_COLUMN_MAP = {
    "mass spectrometer": "instrument",
    "ionization type": "ion source",
    "acquisition polarity": "scan polarity",
    "instrument class": "mass analyzer",
}


def get_sdrf_column_name(name: str, prefix: None | str):
    if prefix == "comment" and name in SDRF_COLUMN_MAP:
        return f"comment[{SDRF_COLUMN_MAP.get(name)}]"
    column_header = f"{prefix}[{name}]" if prefix else name
    return column_header


def get_sdrf_file_column_name(idx: int, name_prefix: str):

    if name_prefix == "raw data file":
        if idx == 1:
            column_header = "comment[data file]"
            url_header = "comment[file uri]"
        elif idx == 2:
            column_header = "comment[associated data file]"
            url_header = "comment[file uri]"
        else:
            column_header = f"comment[associated data file.{idx}]"
            url_header = f"comment[associated data file.{idx} uri]"
    elif name_prefix == "derived data file":
        if idx == 1:
            column_header = "comment[processed data file]"
            url_header = "comment[processed data file uri]"
        else:
            column_header = f"comment[processed data file.{idx}]"
            url_header = f"comment[processed data file.{idx} uri]"
    elif name_prefix == "result file":
        if idx == 1:
            column_header = "comment[metabolite assignment file]"
            url_header = "comment[metabolite assignment file uri]"
        else:
            column_header = f"comment[metabolite assignment file.{idx}]"
            url_header = f"comment[metabolite assignment file.{idx} uri]"
    else:
        if idx == 1:
            column_header = f"comment[{name_prefix}]"
            url_header = f"comment[{name_prefix} uri]"
        else:
            column_header = f"comment[{name_prefix}.{idx}]"
            url_header = f"comment[{name_prefix}.{idx} uri]"
    return column_header, url_header


def find_all_linked_nodes(
    all_nodes_map: dict[str, IdentifiableMhdModel],
    node_relationships: dict[str, dict[str, list[str]]],
    source_id: str,
    relationship_name: str,
    target_node_type: str,
):
    links = node_relationships.get(source_id, {}).get(relationship_name, [])
    nodes = [
        all_nodes_map[x]
        for x in links
        if all_nodes_map[x].type_ == target_node_type
        or (
            all_nodes_map[x].type_.startswith("x-")
            and all_nodes_map[x].type_.endswith(target_node_type)
        )
    ]
    return nodes
