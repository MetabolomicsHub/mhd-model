import logging
from pathlib import Path
from typing import Any, OrderedDict

from pydantic import AnyUrl, BaseModel

from mhd_model.model.definitions import (
    ANNOUNCEMENT_FILE_V0_1_DEFAULT_SCHEMA_NAME,
    ANNOUNCEMENT_FILE_V0_1_LEGACY_PROFILE_NAME,
)
from mhd_model.model.v0_1.announcement.profiles.base.fields import (
    ExtendedCvTermKeyValue,
)
from mhd_model.model.v0_1.announcement.profiles.base.profile import (
    AnnouncementBaseFile,
    AnnouncementDerivedDataFile,
    AnnouncementMetadataFile,
    AnnouncementProtocol,
    AnnouncementPublication,
    AnnouncementRawDataFile,
    AnnouncementReportedMetabolite,
    AnnouncementResultFile,
    AnnouncementSupplementaryFile,
)
from mhd_model.model.v0_1.announcement.profiles.legacy.profile import (
    AnnouncementContact,
    AnnouncementLegacyProfile,
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
from mhd_model.model.v0_1.rules.cv_definitions import (
    CONTROLLED_CV_DEFINITIONS,
    OTHER_CONTROLLED_CV_DEFINITIONS,
)
from mhd_model.model.v0_1.rules.managed_cv_terms import (
    COMMON_ASSAY_TYPES,
    COMMON_MEASUREMENT_TYPES,
    COMMON_OMICS_TYPES,
    COMMON_TECHNOLOGY_TYPES,
    MISSING_PUBLICATION_REASON,
)
from mhd_model.shared.model import CvDefinition

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


def get_keywords(
    all_nodes_map: dict[str, IdentifiableMhdModel],
    relationship_name_map: dict[str, dict[str, BaseMhdRelationship]],
) -> list[CvTerm]:
    keywords = []
    if "has-submitter-keyword" in relationship_name_map:
        for rel in relationship_name_map.get("has-submitter-keyword").values():
            source = all_nodes_map.get(rel.source_ref)
            if source:
                if isinstance(source, graph_nodes.Study):
                    keyword_node = all_nodes_map.get(rel.target_ref)
                    if keyword_node:
                        keyword = CvTerm.model_validate(
                            keyword_node.model_dump(by_alias=True)
                        )
                        keywords.append(keyword)
    return keywords


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
    compressions = []
    if item.compression_format_refs in all_nodes_map:
        for format_ref in item.compression_format_refs:
            compression_node: BaseMhdModel = all_nodes_map[format_ref]
            compressions.append(
                CvTerm.model_validate(compression_node.model_dump(by_alias=True))
            )

    file = file_class(
        name=item.name,
        url_list=url_list,
        compression_formats=compressions or None,
        format=format,
    )

    return file


def collect_cvterm_sources(obj: BaseModel, cv_sources: set[str]):
    if isinstance(obj, (CvTerm, CvTermValue)):
        source = getattr(obj, "source", None)
        if source:
            cv_sources.add(source)
    elif isinstance(obj, BaseModel):
        for value in obj.__dict__.values():
            collect_cvterm_sources(value, cv_sources)
    elif isinstance(obj, list):
        for item in obj:
            collect_cvterm_sources(item, cv_sources)
    elif isinstance(obj, dict):
        for value in obj.values():
            collect_cvterm_sources(value, cv_sources)


def create_announcement_file(
    mhd_file: dict[str, Any],
    mhd_file_url: str,
    announcement_file_path: str,
    announcement_schema_name: str = ANNOUNCEMENT_FILE_V0_1_DEFAULT_SCHEMA_NAME,
    announcement_profile_uri=ANNOUNCEMENT_FILE_V0_1_LEGACY_PROFILE_NAME,
):
    mhd_dataset = MhDatasetLegacyProfile.model_validate(mhd_file)
    nodes_map: dict[str, IdentifiableMhdModel] = {
        x.id_: x for x in mhd_dataset.graph.nodes
    }
    relationships_map: dict[str, BaseMhdRelationship] = {
        x.id_: x for x in mhd_dataset.graph.relationships
    }

    all_nodes_map: dict[str, BaseMhdModel] = {}
    type_map: dict[str, dict[str, BaseMhdModel]] = {}
    for node in mhd_dataset.graph.nodes:
        if node.type_ not in type_map:
            type_map[node.type_] = {}
        type_map[node.type_][node.id_] = node
        all_nodes_map[node.id_] = node

    relationship_name_map: dict[str, dict[str, BaseMhdRelationship]] = {}
    for rel in mhd_dataset.graph.relationships:
        if rel.relationship_name not in relationship_name_map:
            relationship_name_map[rel.relationship_name] = {}
        relationship_name_map[rel.relationship_name][rel.id_] = rel

    if "study" not in type_map:
        logger.error("Study not found for in the input file")
        return
    study: graph_nodes.Study = list(type_map["study"].values())[0]

    study_assays: list[graph_nodes.Assay] = []
    if "assay" in type_map:
        study_assays = list(type_map["assay"].values())

    publications = get_publications(nodes_map, type_map, relationship_name_map)

    submitters, principal_investigators = get_submitter_and_pi(
        type_map, relationship_name_map
    )
    keywords = get_keywords(all_nodes_map, relationship_name_map)
    assay_types, technology_types, measurement_types, omics_types = (
        get_main_assay_descriptors(nodes_map, study_assays, keywords)
    )

    repository_metadata_file_list = get_file_list(
        all_nodes_map, type_map, "metadata-file", AnnouncementMetadataFile
    )
    result_file_list = get_file_list(
        all_nodes_map, type_map, "result-file", AnnouncementResultFile
    )

    raw_data_file_list = get_file_list(
        all_nodes_map, type_map, "raw-data-file", AnnouncementRawDataFile
    )
    derived_data_file_list = get_file_list(
        all_nodes_map, type_map, "derived-data-file", AnnouncementDerivedDataFile
    )
    supplementary_file_list = get_file_list(
        all_nodes_map,
        type_map,
        "supplementary-file",
        AnnouncementSupplementaryFile,
    )
    reported_metabolites = get_metabolites(type_map, relationship_name_map)
    dataset_url_list = study.dataset_url_list

    protocols = get_protocols(all_nodes_map, relationship_name_map, type_map, study)

    study_factors = get_study_factors(all_nodes_map, relationships_map)
    characteristic_values = get_characteristic_values(all_nodes_map, relationships_map)

    if not mhd_file_url:
        ftp = [str(x) for x in study.dataset_url_list if str(x).startswith("ftp://")]
        if ftp:
            mhd_file_url = f"{ftp[0]}/{study.repository_identifier}.mhd.json"

    announcement = AnnouncementLegacyProfile(
        mhd_identifier=study.mhd_identifier,
        repository_identifier=study.repository_identifier,
        schema_name=announcement_schema_name,
        profile_uri=announcement_profile_uri,
        mhd_metadata_file_url=AnyUrl(mhd_file_url),
        dataset_url_list=dataset_url_list,
        license=study.license,
        title=study.title,
        description=study.description,
        submission_date=study.submission_date,
        public_release_date=study.public_release_date,
        submitters=submitters or None,
        principal_investigators=principal_investigators or None,
        measurement_type=measurement_types or None,
        technology_type=technology_types or None,
        assay_type=assay_types or None,
        omics_type=omics_types or None,
        repository_metadata_file_list=repository_metadata_file_list or None,
        result_file_list=result_file_list or None,
        raw_data_file_list=raw_data_file_list or None,
        derived_data_file_list=derived_data_file_list or None,
        supplementary_file_list=supplementary_file_list or None,
        publications=publications or None,
        submitter_keywords=keywords or None,
        reported_metabolites=reported_metabolites or None,
        protocols=protocols,
        study_factors=study_factors or None,
        characteristic_values=characteristic_values,
    )
    cv_sources = set()
    collect_cvterm_sources(announcement, cv_sources)
    cv_sources = list(cv_sources)
    cv_sources.sort()
    for source in cv_sources:
        if source in CONTROLLED_CV_DEFINITIONS:
            announcement.cv_definitions.append(CONTROLLED_CV_DEFINITIONS[source])
        elif source in OTHER_CONTROLLED_CV_DEFINITIONS:
            announcement.cv_definitions.append(OTHER_CONTROLLED_CV_DEFINITIONS[source])
        else:
            announcement.cv_definitions.append(
                CvDefinition(label=source, alternative_labels=[source.lower()])
            )
    logger.info("Writing to %s", announcement_file_path)
    Path(announcement_file_path).parent.mkdir(parents=True, exist_ok=True)
    with Path(announcement_file_path).open("w") as f:
        f.write(
            announcement.model_dump_json(indent=2, by_alias=True, exclude_none=True)
        )


def get_metabolites(
    type_map, relationship_name_map
) -> None | list[AnnouncementReportedMetabolite]:
    identification_map = {}
    identification_links = relationship_name_map.get("identified-as")
    items = type_map.get("metabolite-identification")
    if identification_links and items:
        for ref in identification_links:
            item = identification_links[ref]
            if item.target_ref in items:
                identification = items[item.target_ref]
                if item.source_ref not in identification_map:
                    identification_map[item.source_ref] = []
                identification_map[item.source_ref].append(identification)
    reported_metabolites: list[AnnouncementReportedMetabolite] = []
    if "metabolite" in type_map:
        for ref in type_map["metabolite"]:
            met = type_map["metabolite"][ref]
            item = AnnouncementReportedMetabolite(name=met.name)
            reported_metabolites.append(item)

            if ref in identification_map:
                identifications = identification_map[ref]
                item.database_identifiers = [
                    CvTermValue.model_validate(x.model_dump(by_alias=True))
                    for x in identifications
                ]

        if reported_metabolites:
            reported_metabolites.sort(key=lambda x: x.name)
    return reported_metabolites or None


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


def get_submitter_and_pi(
    type_map: dict[str, dict[str, BaseMhdModel]],
    relationship_name_map: dict[str, dict[str, BaseMhdRelationship]],
):
    submitter_links: list[BaseMhdRelationship] = []
    if "submits" in relationship_name_map:
        submitter_links = list(relationship_name_map["submits"].values())

    submitters = []

    principal_investigators = []
    if "person" in type_map:
        for item in submitter_links:
            if item.source_ref in type_map["person"]:
                submitter = type_map["person"][item.source_ref]
                submitters.append(
                    AnnouncementContact.model_validate(submitter, from_attributes=True)
                )

        if "principal-investigator-of" in relationship_name_map:
            pi_links: list[BaseMhdRelationship] = list(
                relationship_name_map["principal-investigator-of"].values()
            )
            for item in pi_links:
                if item.source_ref in type_map["person"]:
                    pi = type_map["person"][item.source_ref]
                    principal_investigators.append(
                        AnnouncementContact.model_validate(pi, from_attributes=True)
                    )

    return submitters, principal_investigators


def get_publications(
    nodes_map: dict[str, IdentifiableMhdModel],
    type_map: dict[str, dict[str, BaseMhdModel]],
    relationship_name_map: dict[str, dict[str, BaseMhdRelationship]],
) -> CvTerm | list[AnnouncementPublication]:
    publications: list[AnnouncementPublication] = []
    if "publication" in type_map:
        graph_publications: list[graph_nodes.Publication] = list(
            type_map["publication"].values()
        )
        for node in graph_publications:
            item = AnnouncementPublication.model_validate(
                node.model_dump(by_alias=True)
            )
            publications.append(item)
    if publications:
        return publications
    publication_status = None
    if "defined-as" in relationship_name_map:
        definitions = list(relationship_name_map["defined-as"].values())
        if definitions:
            for definition in definitions:
                source_node = nodes_map[definition.source_ref]
                target_node = nodes_map[definition.target_ref]
                if (
                    source_node.type_ == "study"
                    and target_node.type_ == "descriptor"
                    and target_node.accession in MISSING_PUBLICATION_REASON
                ):
                    publication_status = CvTerm.model_validate(
                        target_node.model_dump(by_alias=True)
                    )
                    break
    if not publication_status:
        logger.warning("Publication status is not found in study")
    return publication_status
