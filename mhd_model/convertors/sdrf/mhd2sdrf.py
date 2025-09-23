import json
import logging
from pathlib import Path
from typing import OrderedDict

from mhd_model.model.v0_1.announcement.profiles.base.fields import (
    ExtendedCvTermKeyValue,
)
from mhd_model.model.v0_1.announcement.profiles.base.profile import (
    AnnouncementBaseFile,
    AnnouncementProtocol,
)
from mhd_model.model.v0_1.dataset.profiles.base import graph_nodes
from mhd_model.model.v0_1.dataset.profiles.base.base import (
    BaseMhdModel,
    BaseMhdRelationship,
    CvTerm,
    CvTermValue,
    IdentifiableMhdModel,
)
from mhd_model.model.v0_1.dataset.profiles.legacy.profile import MhDatasetLegacyProfile
from mhd_model.model.v0_1.rules.managed_cv_terms import (
    COMMON_ASSAY_TYPES,
    COMMON_MEASUREMENT_TYPES,
    COMMON_OMICS_TYPES,
    COMMON_TECHNOLOGY_TYPES,
)
from mhd_model.model.v0_1.sdrf.model import (
    LegacySdrf,
    LegacySdrfRow,
    SdrfFile,
    SdrfKeyValue,
    SdrfSampleProtocolDefinition,
)
from mhd_model.shared.model import QuantitativeValue

logger = logging.getLogger(__name__)


def get_characteristic_values(
    all_nodes_map: dict[str, IdentifiableMhdModel],
    relationships_map: dict[str, BaseMhdRelationship],
) -> list[ExtendedCvTermKeyValue]:
    study_characteristics = set()
    characteristic_values: OrderedDict[str, list[str]] = OrderedDict()
    for rel in relationships_map.values():
        source = all_nodes_map[rel.source_ref]
        if rel.relationship_name == "has-characteristic-definition":
            if isinstance(source, graph_nodes.Study):
                study_characteristics.add(rel.target_ref)

        if rel.relationship_name == "has-instance":
            if isinstance(source, graph_nodes.CharacteristicDefinition):
                if rel.source_ref not in characteristic_values:
                    characteristic_values[rel.source_ref] = []
                characteristic_values[rel.source_ref].append(rel.target_ref)
    referenced_characteristics = {
        x: y
        for x, y in characteristic_values.items()
        if x in study_characteristics and y
    }
    characteristic_keys = [
        (x, all_nodes_map[x]) for x, y in referenced_characteristics.items()
    ]
    characteristic_keys.sort(key=lambda x: x[1].name)
    announcement_characteristics = []
    for char_id, characteristic in characteristic_keys:
        value_ids = referenced_characteristics[char_id]
        values = []
        for x in value_ids:
            val = all_nodes_map[x]
            if val.id_.startswith("cv-value--"):
                val = CvTermValue.model_validate(val.model_dump(by_alias=True))
            else:
                val = CvTerm.model_validate(val.model_dump(by_alias=True))
            values.append(val)
        type_node = all_nodes_map.get(characteristic.characteristic_type_ref, None)
        key = CvTerm.model_validate(type_node.model_dump(by_alias=True))
        announcement_characteristics.append(
            ExtendedCvTermKeyValue(key=key, values=values)
        )

    return announcement_characteristics


def get_study_factors(
    all_nodes_map: dict[str, IdentifiableMhdModel],
    relationships_map: dict[str, BaseMhdRelationship],
):
    study_factors = set()
    factors: OrderedDict[str, list[str]] = OrderedDict()
    for rel in relationships_map.values():
        source = all_nodes_map[rel.source_ref]
        if rel.relationship_name == "has-factor-definition":
            if isinstance(source, graph_nodes.Study):
                study_factors.add(rel.target_ref)

        if rel.relationship_name == "has-instance":
            if isinstance(source, graph_nodes.FactorDefinition):
                if rel.source_ref not in factors:
                    factors[rel.source_ref] = []
                factors[rel.source_ref].append(rel.target_ref)
    referenced_factors = {x: y for x, y in factors.items() if x in study_factors and y}
    factor_keys = [(x, all_nodes_map[x]) for x, y in referenced_factors.items()]
    factor_keys.sort(key=lambda x: x[1].name)
    announcement_factors = []
    for factor_id, factor in factor_keys:
        value_ids = referenced_factors[factor_id]
        values = []
        for x in value_ids:
            val = all_nodes_map[x]
            if isinstance(val, CvTermValue):
                val = CvTermValue.model_validate(val.model_dump(by_alias=True))
            else:
                val = CvTerm.model_validate(val.model_dump(by_alias=True))
            values.append(val)
        type_node = all_nodes_map.get(factor.factor_type_ref, None)
        key = CvTerm.model_validate(type_node.model_dump(by_alias=True))
        announcement_factors.append(ExtendedCvTermKeyValue(key=key, values=values))
    return announcement_factors


def get_protocols(
    all_nodes_map: dict[str, IdentifiableMhdModel],
    relationship_name_map: dict[str, BaseMhdRelationship],
    type_map: dict[str, dict[IdentifiableMhdModel]],
    study: graph_nodes.Study,
):
    protocols: list[AnnouncementProtocol] = []
    if not study.protocol_refs:
        return protocols

    for ref in study.protocol_refs:
        if ref not in type_map["protocol"]:
            logger.error("Protocol %s is not defined in dataset.", ref)
        protocol_parameters = []
        protocol_node: graph_nodes.Protocol = type_map["protocol"].get(ref)
        protocol_type_object = all_nodes_map.get(protocol_node.protocol_type_ref, None)
        # if not protocol_node.parameter_definition_refs:
        #     continue
        protocol_parameters = []
        if protocol_node.parameter_definition_refs:
            for definition_key in protocol_node.parameter_definition_refs:
                if definition_key not in all_nodes_map:
                    continue
                definition = all_nodes_map[definition_key]
                if not isinstance(definition, graph_nodes.ParameterDefinition):
                    continue
                vals = []
                for rel in relationship_name_map["has-instance"].values():
                    if rel.source_ref == definition.id_:
                        val = None
                        val_obj = all_nodes_map.get(rel.target_ref)
                        if isinstance(val_obj, CvTerm):
                            val = CvTerm.model_validate(
                                val_obj.model_dump(by_alias=True)
                            )
                        elif isinstance(val_obj, CvTermValue):
                            val = CvTermValue.model_validate(
                                val_obj.model_dump(by_alias=True)
                            )
                        if not val:
                            continue
                        vals.append(val)
                # if vals:
                def_type = all_nodes_map.get(definition.parameter_type_ref)
                key = CvTerm.model_validate(def_type.model_dump(by_alias=True))
                param = ExtendedCvTermKeyValue(
                    key=key,
                    values=vals or None,
                )
                protocol_parameters.append(param)
        if not protocol_parameters:
            protocol_parameters = None
        else:
            protocol_parameters.sort(key=lambda x: x.key.name)
        protocol_type = CvTerm.model_validate(
            protocol_type_object.model_dump(by_alias=True)
        )
        protocol = AnnouncementProtocol(
            name=protocol_node.name,
            protocol_type=protocol_type,
            description=protocol_node.description,
            protocol_parameters=protocol_parameters,
        )
        protocols.append(protocol)

    return protocols


def convert_file(
    all_nodes_map,
    type_map: dict[str, dict[str, IdentifiableMhdModel]],
    file_type_name: str,
    ref: str,
    file_class: type[AnnouncementBaseFile],
):
    if file_type_name not in type_map or ref not in type_map[file_type_name]:
        return None
    item: graph_nodes.BaseFile = type_map[file_type_name][ref]
    url_list = item.url_list
    format = None
    if item.format_ref in all_nodes_map:
        format_node: BaseMhdModel = all_nodes_map[item.format_ref]
        format = CvTerm.model_validate(format_node.model_dump(by_alias=True))
    compressions = None
    if item.compression_format_refs in all_nodes_map:
        for format_ref in item.compression_format_refs:
            compression_node: BaseMhdModel = all_nodes_map[format_ref]
            compressions.append(
                CvTerm.model_validate(compression_node.model_dump(by_alias=True))
            )
    file = file_class(
        name=item.name,
        url_list=url_list,
        compression_formats=compressions,
        format=format,
    )

    return file


def create_sdrf_files(
    mhd_file_path: str,
    sdrf_file_root_path: str,
    assay_name: None | str = None,
    sdrf_output_filename: None | str = None,
):
    sdrf_files = []
    txt = Path(mhd_file_path).read_text()
    mhd_data_json = json.loads(txt)

    mhd_dataset = MhDatasetLegacyProfile.model_validate(mhd_data_json)
    nodes_map: dict[str, IdentifiableMhdModel] = {
        x.id_: x for x in mhd_dataset.graph.nodes
    }
    # relationships_map: dict[str, BaseMhdRelationship] = {
    #     x.id_: x for x in mhd_dataset.graph.relationships
    # }

    all_nodes_map: dict[str, BaseMhdModel] = {}
    type_map: dict[str, dict[str, BaseMhdModel]] = {}
    for node in mhd_dataset.graph.nodes:
        if node.type_ not in type_map:
            type_map[node.type_] = {}
        type_map[node.type_][node.id_] = node
        all_nodes_map[node.id_] = node

    relationship_name_map: dict[str, dict[str, BaseMhdRelationship]] = {}
    node_relationships: dict[str, dict[str, list[str]]] = {}
    for rel in mhd_dataset.graph.relationships:
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
    study: graph_nodes.Study = list(type_map["study"].values())[0]
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
    for idx, assay in selected_assays:
        if not assay.sample_run_refs:
            logger.error("Study %s Assay '%s' has no sample run", study_id, assay.name)
            continue
        sdrf_file = LegacySdrf(
            study_identifier=study.repository_identifier,
            assay_identifier=assay.repository_identifier,
        )
        parameter_type_cv_terms: dict[str, CvTerm] = {}

        for sample_run_ref in assay.sample_run_refs:
            sample_run: graph_nodes.SampleRun = all_nodes_map[sample_run_ref]
            sample: graph_nodes.Sample = all_nodes_map[sample_run.sample_ref]

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
                            if value.value is not None and value.name is None:
                                target_value = QuantitativeValue.model_validate(
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
                            if value.value is not None and value.name is None:
                                target_value = QuantitativeValue.model_validate(
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
                            paramter_types: list[IdentifiableMhdModel] = (
                                find_all_linked_nodes(
                                    all_nodes_map,
                                    node_relationships,
                                    value.id_,
                                    "has-type",
                                    "parameter-type",
                                )
                            )
                            if paramter_types:
                                parameter_type = paramter_types[0]
                                if parameter_type.id_ not in parameter_type_cv_terms:
                                    parameter_type_cv_terms[parameter_type.id_] = (
                                        CvTerm.model_validate(
                                            parameter_type.model_dump(by_alias=True)
                                        )
                                    )
                                target_value = None
                                if value.value is not None and value.name is None:
                                    target_value = QuantitativeValue.model_validate(
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
        headers["sample name"] = None
        factor_headers = {}
        characteristic_headers = {}
        parameter_value_headers = {}

        characteristic_definitions.sort(key=lambda x: x.name)
        for definition in characteristic_definitions:
            definition_type = nodes_map[definition.characteristic_type_ref]
            name = (
                definition_type.name.lower()
                if definition_type.name
                else definition.name.lower()
            )
            if definition_type.accession:
                header = f"characteristic[{name}|{definition_type.accession}]"
                headers[header] = definition
            else:
                header = f"characteristic[{name}]"
                headers[header] = definition
            characteristic_headers[name] = header

        headers["assay name"] = None
        if assay.protocol_refs:
            protocols = [nodes_map[x] for x in assay.protocol_refs]
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
                        if parameter_type and parameter_type.accession:
                            header = (
                                f"parameter value[{name}|{parameter_type.accession}]"
                            )
                            headers[header] = definition
                        else:
                            header = f"parameter value[{name}]"
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
        summplementary_files_data: list[list[tuple[str, str]]] = [
            []
        ] * max_supplementary_data_column
        for name_prefix, files in [
            ("raw data file", raw_files_data),
            ("derived data file", derived_files_data),
            ("result file", result_files_data),
            ("supplementary file", summplementary_files_data),
        ]:
            for idx, item in enumerate(files, start=1):
                name = f"comment[{name_prefix} name.{idx}]"
                headers[name] = name
                url = f"comment[{name_prefix} url.{idx}]"
                headers[url] = url
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
            if definition_type.accession:
                header = f"factor value[{name}|{definition_type.accession}]"
                headers[header] = definition
            else:
                header = f"factor value[{name}]"
                headers[header] = definition
            factor_headers[name] = header

        tsv_data: OrderedDict[str, list[str]] = OrderedDict([(x, []) for x in headers])

        for row in sdrf_file.sample_runs:
            tsv_data.get("sample name", []).append(row.sample_name or "")
            tsv_data.get("assay name", []).append(row.assay_name or "")
            filled_headers = set(["sample name", "assay name"])
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
                        item_type = item.key.name
                        header = item_headers.get(item_type)
                        filled_headers.add(header)
                        tsv_data.get(header, []).append(item.value.name or "")

            for name_prefix, files, values in [
                ("raw data file", raw_files_data, row.raw_data_files),
                ("derived data file", derived_files_data, row.derived_data_files),
                ("result file", result_files_data, row.result_files),
                (
                    "supplementary file",
                    summplementary_files_data,
                    row.supplementary_files,
                ),
            ]:
                for idx, item in enumerate(files, start=1):
                    header = f"comment[{name_prefix} name.{idx}]"
                    name_value = values[idx - 1].name or ""
                    tsv_data.get(header, []).append(name_value or "")
                    url_header = f"comment[{name_prefix} url.{idx}]"
                    url_list = values[idx - 1].url_list
                    filled_headers.add(header)
                    url_value = ""
                    if url_list:
                        url_value = str(url_list[0])
                    tsv_data.get(url_header, []).append(url_value)
                    filled_headers.add(url_header)
            not_defined_headers = {x for x in tsv_data if x not in filled_headers}
            for header in not_defined_headers:
                tsv_data[header].append("")
        empty_columns = []
        exceptions = {
            "sample name",
            "assay name",
            "comment[raw data file name.1]",
            "comment[raw data file url.1]",
        }
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
            row_count = len(tsv_data["sample name"])
            for idx in range(row_count):
                row = [tsv_data[x][idx] for x in tsv_data]
                row_data = "\t".join(row) + "\n"
                f.write(row_data)
        logger.info("%s SDRF file is created: %s", study_id, str(srdf_file_path))

    return sdrf_files


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


def get_file_list(
    all_nodes_map: dict[str, IdentifiableMhdModel],
    type_map: dict[str, dict[str, BaseMhdModel]],
    node_type: str,
    file_class: type[AnnouncementBaseFile],
) -> list[AnnouncementBaseFile]:
    file_list = []
    if node_type in type_map:
        for ref in type_map[node_type]:
            file_object = convert_file(
                all_nodes_map, type_map, node_type, ref, file_class
            )
            if file_object:
                file_list.append(file_object)
    return file_list


def get_main_assay_descriptors(
    nodes_map: dict[str, IdentifiableMhdModel],
    study_assays: list[graph_nodes.Assay],
    keywords: list[CvTerm],
) -> tuple[list[CvTerm], list[CvTerm], list[CvTerm], list[CvTerm]]:
    assay_types: dict[str, CvTerm] = {}
    technology_types: dict[str, CvTerm] = {}
    measurement_types: dict[str, CvTerm] = {}
    omics_types: dict[str, CvTerm] = {}
    for item in study_assays:
        if item.assay_type_ref in nodes_map:
            assay_type: graph_nodes.CvTermObject = nodes_map[item.assay_type_ref]
            if assay_type.accession not in assay_types:
                term = COMMON_ASSAY_TYPES.get(assay_type.accession, None)
                if not term:
                    term = CvTerm.model_validate(assay_type.model_dump(by_alias=True))
                assay_types[term.accession] = term

        if item.technology_type_ref in nodes_map:
            technology_type: graph_nodes.CvTermObject = nodes_map[
                item.technology_type_ref
            ]
            if technology_type.accession not in technology_types:
                term = COMMON_TECHNOLOGY_TYPES.get(technology_type.accession)
                if not term:
                    term = CvTerm.model_validate(
                        technology_type.model_dump(by_alias=True)
                    )
                technology_types[term.accession] = term
        if item.measurement_type_ref in nodes_map:
            measurement_type: graph_nodes.CvTermObject = nodes_map[
                item.technology_type_ref
            ]
            if measurement_type.accession not in measurement_types:
                term = COMMON_MEASUREMENT_TYPES.get(measurement_type.accession)
                if not term:
                    term = CvTerm.model_validate(
                        technology_type.model_dump(by_alias=True)
                    )
                measurement_types[term.accession] = term

    for keyword in keywords:
        if "untargetted" in keyword.name.lower():
            measurement_types["MSIO:0000101"] = COMMON_MEASUREMENT_TYPES["MSIO:0000101"]
        elif "targetted" in keyword.name.lower():
            measurement_types["MSIO:0000100"] = COMMON_MEASUREMENT_TYPES["MSIO:0000101"]
        for accession, value in COMMON_OMICS_TYPES.items():
            if accession.lower() == keyword.name.lower():
                omics_types[accession] = value

    return (
        list(assay_types.values()),
        list(technology_types.values()),
        list(measurement_types.values()),
        list(omics_types.values()),
    )
