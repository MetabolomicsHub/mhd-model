import logging
from pathlib import Path
from typing import Any, OrderedDict

from pydantic import BaseModel

from mhd_model.model.definitions import (
    ANNOUNCEMENT_FILE_V0_1_DEFAULT_SCHEMA_NAME,
    ANNOUNCEMENT_FILE_V0_1_LEGACY_PROFILE_NAME,
)
from mhd_model.model.v0_1.announcement.profiles.base.fields import (
    ExtendedCvTermKeyValue,
)
from mhd_model.model.v0_1.announcement.profiles.base.profile import (
    AnnouncementBaseFile,
    AnnouncementBaseProfile,
    AnnouncementContact,
    AnnouncementDerivedDataFile,
    AnnouncementMetadataFile,
    AnnouncementProtocol,
    AnnouncementPublication,
    AnnouncementRawDataFile,
    AnnouncementReportedMetabolite,
    AnnouncementResultFile,
    AnnouncementSupplementaryFile,
)
from mhd_model.model.v0_1.announcement.profiles.ms.profile import AnnouncementMsProfile
from mhd_model.model.v0_1.dataset.profiles.base import graph_nodes
from mhd_model.model.v0_1.dataset.profiles.base.base import (
    BaseMhdModel,
    BaseMhdRelationship,
    CvTerm,
    CvTermValue,
    IdentifiableMhdModel,
)
from mhd_model.model.v0_1.dataset.profiles.ms.profile import MhDatasetMsProfile
from mhd_model.model.v0_1.rules.cv_definitions import (
    CONTROLLED_CV_DEFINITIONS,
    OTHER_CONTROLLED_CV_DEFINITIONS,
)
from mhd_model.shared.model import CvDefinition

logger = logging.getLogger(__name__)


def update_characteristic_values(
    all_nodes_map: dict[str, IdentifiableMhdModel],
    relationships_map: dict[str, BaseMhdRelationship],
    announcement: AnnouncementMsProfile,
):
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
        if not announcement.characteristic_values:
            announcement.characteristic_values = []
        announcement.characteristic_values.append(
            ExtendedCvTermKeyValue(key=key, values=values)
        )


def update_keywords(
    all_nodes_map: dict[str, IdentifiableMhdModel],
    relationship_name_map: dict[str, dict[str, BaseMhdRelationship]],
    announcement: AnnouncementMsProfile,
):
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
                        if announcement.submitter_keywords is None:
                            announcement.submitter_keywords = []
                        announcement.submitter_keywords.append(keyword)


def update_study_factors(
    all_nodes_map: dict[str, IdentifiableMhdModel],
    relationships_map: dict[str, BaseMhdRelationship],
    announcement: AnnouncementMsProfile,
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
        if not announcement.study_factors:
            announcement.study_factors = []
        announcement.study_factors.append(
            ExtendedCvTermKeyValue(key=key, values=values)
        )


def update_protocol_parameters(
    all_nodes_map: dict[str, IdentifiableMhdModel],
    relationship_name_map: dict[str, BaseMhdRelationship],
    type_map: dict[str, dict[IdentifiableMhdModel]],
    study: graph_nodes.Study,
    announcement: AnnouncementMsProfile,
):
    if "protocol" in type_map:
        for ref in type_map["protocol"]:
            protocol_parameters = []
            protocol_node: graph_nodes.Protocol = type_map["protocol"].get(ref)
            if not protocol_node.parameter_definition_refs:
                continue
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
                if vals:
                    def_type = all_nodes_map.get(definition.parameter_type_ref)
                    key = CvTerm.model_validate(def_type.model_dump(by_alias=True))
                    param = ExtendedCvTermKeyValue(
                        key=key,
                        values=vals if vals else None,
                    )
                    protocol_parameters.append(param)
            if not protocol_parameters:
                protocol_parameters = None
            else:
                protocol_parameters.sort(key=lambda x: x.key.name)
            protocol_type_object = all_nodes_map.get(
                protocol_node.protocol_type_ref, None
            )
            protocol = AnnouncementProtocol(
                name=protocol_node.name,
                protocol_type=protocol_type_object,
                description=protocol_node.description,
                protocol_parameters=protocol_parameters,
            )
            if not announcement.protocols:
                announcement.protocols = []
            announcement.protocols.append(protocol)


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
    mhd_dataset = MhDatasetMsProfile.model_validate(mhd_file)
    nodes_map = {x.id_: x for x in mhd_dataset.graph.nodes}
    relationships_map = {x.id_: x for x in mhd_dataset.graph.relationships}

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
        logger.info("Study not found for in input file")
        return
    study: graph_nodes.Study = list(type_map["study"].values())[0]

    study_assays: list[graph_nodes.Assay] = []
    if "assay" in type_map:
        study_assays = list(type_map["assay"].values())

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

    publication_status = None
    if not publications:
        if "defined-as" in relationship_name_map:
            publication_status = list(relationship_name_map["defined-as"].values())
            if publication_status:
                status = publication_status[0]

                publication_status = CvTerm.model_validate(
                    nodes_map[status.target_ref].model_dump(by_alias=True)
                )

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

    assay_types: OrderedDict[str, CvTerm] = OrderedDict()
    technology_types: OrderedDict[str, CvTerm] = OrderedDict()
    measurement_types: OrderedDict[str, CvTerm] = OrderedDict()
    for item in study_assays:
        if item.assay_type_ref in nodes_map:
            assay_type: graph_nodes.CvTermObject = nodes_map[item.assay_type_ref]
            if assay_type.accession not in assay_types:
                term = CvTerm.model_validate(assay_type)
                assay_types[term.accession] = term

        if item.technology_type_ref in nodes_map:
            technology_type: graph_nodes.CvTermObject = nodes_map[
                item.technology_type_ref
            ]
            if technology_type.accession not in technology_types:
                term = CvTerm.model_validate(technology_type)
                technology_types[term.accession] = term
        if item.measurement_type_ref in nodes_map:
            measurement_type: graph_nodes.CvTermObject = nodes_map[
                item.technology_type_ref
            ]
            if measurement_type.accession not in measurement_types:
                term = CvTerm.model_validate(technology_type)
                measurement_types[term.accession] = term

    dataset_url_list = study.url_list

    announcement = AnnouncementBaseProfile(
        mhd_identifier=study.mhd_identifier,
        repository_identifier=study.repository_identifier,
        schema_name=announcement_schema_name,
        profile_uri=announcement_profile_uri,
        mhd_metadata_file_url=CvTermValue(
            accession="EDAM:1052",
            name="URL",
            source="EDAM",
            value=mhd_file_url,
        ),
        dataset_url_list=dataset_url_list,
        license=study.license,
        title=study.title,
        description=study.description,
        submission_date=study.submission_date,
        public_release_date=study.public_release_date,
        submitters=submitters,
        principal_investigators=principal_investigators,
        measurement_type=list(measurement_types.values()),
        technology_type=list(technology_types.values()),
        assay_type=list(assay_types.values()),
        repository_metadata_file_list=[],
        result_file_list=[],
        raw_data_file_list=[],
        derived_data_file_list=[],
        supplementary_file_list=[],
        publications=publications if publications else publication_status,
        # study_factors=[],
        # characteristic_values=[],
    )

    update_keywords(all_nodes_map, relationship_name_map, announcement)
    update_protocol_parameters(
        all_nodes_map, relationship_name_map, type_map, study, announcement
    )
    update_study_factors(all_nodes_map, relationships_map, announcement)
    update_characteristic_values(all_nodes_map, relationships_map, announcement)

    if "metadata-file" in type_map:
        for ref in type_map["metadata-file"]:
            metadata = convert_file(
                all_nodes_map, type_map, "metadata-file", ref, AnnouncementMetadataFile
            )
            if metadata:
                announcement.repository_metadata_file_list.append(metadata)

    if "result-file" in type_map:
        for ref in type_map["result-file"]:
            file = convert_file(
                all_nodes_map, type_map, "result-file", ref, AnnouncementResultFile
            )
            if file:
                announcement.result_file_list.append(file)

    if "raw-data-file" in type_map:
        for ref in type_map["raw-data-file"]:
            file = convert_file(
                all_nodes_map, type_map, "raw-data-file", ref, AnnouncementRawDataFile
            )
            if file:
                announcement.raw_data_file_list.append(file)
    if "derived-data-file" in type_map:
        for ref in type_map["derived-data-file"]:
            file = convert_file(
                all_nodes_map,
                type_map,
                "derived-data-file",
                ref,
                AnnouncementDerivedDataFile,
            )
            if file:
                announcement.derived_data_file_list.append(file)
    if "supplementary-file" in type_map:
        for ref in type_map["supplementary-file"]:
            file = convert_file(
                all_nodes_map,
                type_map,
                "supplementary-file",
                ref,
                AnnouncementSupplementaryFile,
            )
            if file:
                announcement.supplementary_file_list.append(file)
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

    if "metabolite" in type_map:
        reported_metabolites = []
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
            announcement.reported_metabolites = reported_metabolites
            announcement.reported_metabolites.sort(key=lambda x: x.name)
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
