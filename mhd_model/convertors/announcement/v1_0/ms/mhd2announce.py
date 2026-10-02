import datetime
import logging
from collections import OrderedDict
from pathlib import Path
from typing import Any

from pydantic import AnyUrl, BaseModel

from mhd_model.domain_utils import get_urn
from mhd_model.model.definitions import (
    MHD_MODEL_ANNOUNCEMENT_FILE_PROFILE_MAP,
)
from mhd_model.model.v1_0.announcement.profiles.ms.fields import ExtendedCvTermKeyValue
from mhd_model.model.v1_0.announcement.profiles.ms.profile import (
    AnnouncementMsProfile,
    MsAnnouncementContact,
    MsAnnouncementDerivedDataFile,
    MsAnnouncementMetadataFile,
    MsAnnouncementProtocol,
    MsAnnouncementPublication,
    MsAnnouncementRawDataFile,
    MsAnnouncementReportedMolecularEntity,
    MsAnnouncementResultFile,
    MsAnnouncementSupplementaryFile,
)
from mhd_model.model.v1_0.dataset.profiles.base import graph_nodes
from mhd_model.model.v1_0.dataset.profiles.base.graph_nodes import CvTermValueObject
from mhd_model.model.v1_0.dataset.profiles.ms.profile import MhDatasetMsProfile_v1_0
from mhd_model.shared.base import (
    BasicValueModel,
    CvTerm,
    CvTermKeyValue,
    CvTermValue,
)
from mhd_model.shared.model import (
    BaseRelationshipModel,
    IdentifiableMhdModel,
    MhdModelValidationContext,
    MhdNode,
)

logger = logging.getLogger(__name__)


def convert_to_cv_term(val: CvTerm):
    val.source = val.source or ""
    val.name = val.name or ""
    val.accession = val.accession or ""
    return CvTerm.model_validate(val.model_dump(by_alias=True, exclude=None))


def convert_to_cv_term_value(val: CvTermValue, allow_only_value: bool = False):
    val.source = val.source or ""
    val.name = val.name or ""
    val.accession = val.accession or ""
    val.value = val.value or None
    if val.unit:
        val.unit.source = val.source or ""
        val.unit.name = val.name or ""
        val.unit.accession = val.accession or ""
    if (
        val.unit
        and not val.unit.source
        and not val.unit.name
        and not val.unit.accession
    ):
        val.unit = None
    if allow_only_value and not val.source and not val.name and not val.accession:
        return BasicValueModel.model_validate(
            val.model_dump(by_alias=True, exclude=None)
        )
    return CvTermValue.model_validate(val.model_dump(by_alias=True, exclude=None))


def update_characteristic_values(
    all_nodes_map: dict[str, IdentifiableMhdModel],
    relationships_map: dict[str, BaseRelationshipModel],
    announcement: AnnouncementMsProfile,
):
    study_characteristics = set()
    characteristic_values: OrderedDict[str, list[str]] = OrderedDict()
    for rel in relationships_map.values():
        source = all_nodes_map[rel.source_ref]
        if rel.relationship_name == "has-characteristic-definition" and isinstance(
            source, graph_nodes.Study
        ):
            study_characteristics.add(rel.target_ref)

        if rel.relationship_name == "has-instance" and isinstance(
            source, graph_nodes.CharacteristicDefinition
        ):
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
            val_obj = all_nodes_map[x]
            if isinstance(val_obj, CvTermValueObject) and val_obj.value:
                val = convert_to_cv_term_value(val_obj)
                values.append(val)
            elif val_obj.name:
                val = convert_to_cv_term(val_obj)
                values.append(val)
        type_node = all_nodes_map.get(characteristic.characteristic_type_ref, None)
        key = convert_to_cv_term(type_node)
        if not announcement.characteristic_values:
            announcement.characteristic_values = []
        announcement.characteristic_values.append(
            CvTermKeyValue(key=key, values=values)
        )


def update_keywords(
    all_nodes_map: dict[str, IdentifiableMhdModel],
    relationship_name_map: dict[str, dict[str, BaseRelationshipModel]],
    announcement: AnnouncementMsProfile,
):
    if "has-submitter-keyword" in relationship_name_map:
        for rel in relationship_name_map.get("has-submitter-keyword").values():
            source = all_nodes_map.get(rel.source_ref)
            if source and isinstance(source, graph_nodes.Study):
                keyword_node = all_nodes_map.get(rel.target_ref)
                if keyword_node:
                    keyword = convert_to_cv_term(keyword_node)
                    if announcement.submitter_keywords is None:
                        announcement.submitter_keywords = []
                    announcement.submitter_keywords.append(keyword)


def get_descriptors(
    all_nodes_map: dict[str, IdentifiableMhdModel],
    relationship_name_map: dict[str, dict[str, BaseRelationshipModel]],
) -> list[CvTerm]:
    descriptors = []
    if "has-repository-keyword" in relationship_name_map:
        for rel in relationship_name_map.get("has-repository-keyword").values():
            source = all_nodes_map.get(rel.source_ref)
            if source and isinstance(source, graph_nodes.Study):
                descriptor_node = all_nodes_map.get(rel.target_ref)
                if descriptor_node:
                    descriptor = convert_to_cv_term(descriptor_node)
                    descriptors.append(descriptor)
    return descriptors


def update_study_factors(
    all_nodes_map: dict[str, IdentifiableMhdModel],
    relationships_map: dict[str, BaseRelationshipModel],
    announcement: AnnouncementMsProfile,
):
    study_factors = set()
    factors: OrderedDict[str, list[str]] = OrderedDict()
    for rel in relationships_map.values():
        source = all_nodes_map[rel.source_ref]
        if rel.relationship_name == "has-factor-definition" and isinstance(
            source, graph_nodes.Study
        ):
            study_factors.add(rel.target_ref)

        if rel.relationship_name == "has-instance" and isinstance(
            source, graph_nodes.FactorDefinition
        ):
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
            val_obj = all_nodes_map[x]
            if isinstance(val_obj, CvTermValueObject) and val_obj.value:
                val = convert_to_cv_term_value(val_obj, allow_only_value=True)
                values.append(val)
            elif val_obj.name:
                val = convert_to_cv_term(val_obj)
                values.append(val)
        type_node = all_nodes_map.get(factor.factor_type_ref, None)
        key = convert_to_cv_term(type_node)
        if not announcement.study_factors:
            announcement.study_factors = []
        announcement.study_factors.append(
            ExtendedCvTermKeyValue(key=key, values=values)
        )


def update_protocol_parameters(
    all_nodes_map: dict[str, IdentifiableMhdModel],
    relationship_name_map: dict[str, BaseRelationshipModel],
    type_map: dict[str, dict[str, IdentifiableMhdModel]],
    study: graph_nodes.Study,
    announcement: AnnouncementMsProfile,
):
    protocols = type_map.get("protocol", {})

    for ref in protocols:
        protocol_parameters = []
        protocol_node: graph_nodes.Protocol = protocols.get(ref)
        for definition_key in protocol_node.parameter_definition_refs or []:
            if definition_key not in all_nodes_map:
                continue
            definition = all_nodes_map[definition_key]
            if not isinstance(definition, graph_nodes.ParameterDefinition):
                continue
            vals = []
            for rel in relationship_name_map["has-instance"].values():
                if rel.source_ref == definition.id_:
                    val_obj = all_nodes_map.get(rel.target_ref)
                    if isinstance(val_obj, CvTermValueObject) and val_obj.value:
                        val = convert_to_cv_term_value(val_obj, allow_only_value=True)
                        vals.append(val)
                    elif val_obj.name:
                        val = convert_to_cv_term(val_obj)
                        vals.append(val)
            if vals:
                def_type = all_nodes_map.get(definition.parameter_type_ref)
                key = convert_to_cv_term(def_type)
                param = ExtendedCvTermKeyValue(
                    key=key,
                    values=vals if vals else None,
                )
                protocol_parameters.append(param)
        if not protocol_parameters:
            protocol_parameters = None
        else:
            protocol_parameters.sort(key=lambda x: x.key.name)
        protocol_type_object = all_nodes_map.get(protocol_node.protocol_type_ref, None)
        protocol_type = convert_to_cv_term(protocol_type_object)

        protocol = MsAnnouncementProtocol(
            name=protocol_node.name,
            protocol_type=protocol_type,
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
    file_class: type[AnnouncementMsProfile],
):
    if file_type_name not in type_map or ref not in type_map.get(file_type_name, {}):
        return None
    item: graph_nodes.BaseFile = type_map.get(file_type_name, {}).get(ref)
    url_list = item.url_list
    format = None
    if item.format_ref in all_nodes_map:
        format_node: MhdNode = all_nodes_map[item.format_ref]
        format = convert_to_cv_term(format_node)
    compressions = []
    if item.compression_format_refs in all_nodes_map:
        for format_ref in item.compression_format_refs:
            compression_node: MhdNode = all_nodes_map[format_ref]
            compressions.append(convert_to_cv_term(compression_node))
    file = file_class(
        name=item.name,
        url_list=url_list,
        compression_formats=compressions or None,
        format=format or None,
        extension=item.extension or None,
    )

    return file


def collect_cv_term_sources(obj: BaseModel, cv_sources: set[str]):
    if isinstance(obj, (CvTerm, CvTermValue)):
        source = getattr(obj, "source", None)
        if source:
            cv_sources.add(source)
    elif isinstance(obj, BaseModel):
        for value in obj.__dict__.values():
            collect_cv_term_sources(value, cv_sources)
    elif isinstance(obj, list):
        for item in obj:
            collect_cv_term_sources(item, cv_sources)
    elif isinstance(obj, dict):
        for value in obj.values():
            collect_cv_term_sources(value, cv_sources)


def get_submitters_and_pi(
    type_map: dict[str, dict[str, MhdNode]],
    relationship_name_map: dict[str, BaseRelationshipModel],
):
    submitters = []

    principal_investigators = []
    people = type_map.get("person") or {}
    if not people:
        return None, None
    submitter_links: list[BaseRelationshipModel] = []
    if "submits" in relationship_name_map:
        submitter_links = list(relationship_name_map.get("submits", {}).values())
    for item in submitter_links:
        if item.source_ref in people:
            submitter = people[item.source_ref]
            submitters.append(
                MsAnnouncementContact.model_validate(submitter, from_attributes=True)
            )
    pi_links: list[BaseRelationshipModel] = list(
        relationship_name_map.get("principal-investigator-of", {}).values()
    )
    for item in pi_links:
        if item.source_ref in people:
            pi = people[item.source_ref]
            principal_investigators.append(
                MsAnnouncementContact.model_validate(pi, from_attributes=True)
            )
    return submitters or None, principal_investigators or None


def create_ms_announcement_file(
    mhd_file: dict[str, Any],
    mhd_file_url: str,
    announcement_file_path: str,
    mhd_metadata_file_hashes: None | list[CvTermValue] = None,
):
    context = MhdModelValidationContext(
        dataset_configuration=MhDatasetMsProfile_v1_0.get_config()
    )
    mhd_dataset = MhDatasetMsProfile_v1_0.model_validate(mhd_file, context=context)
    announcement_schema_name, announcement_profile_uri = (
        MHD_MODEL_ANNOUNCEMENT_FILE_PROFILE_MAP.get(
            mhd_dataset.profile_uri, (None, None)
        )
    )
    if not announcement_schema_name or not announcement_profile_uri:
        raise ValueError("Announcement Schema or profile is not defined")
    nodes_map: dict[str, IdentifiableMhdModel] = {
        x.id_: x for x in mhd_dataset.graph.nodes
    }
    relationships_map: dict[str, BaseRelationshipModel] = {
        x.id_: x for x in mhd_dataset.graph.relationships
    }

    all_nodes_map: dict[str, MhdNode] = {}
    type_map: dict[str, dict[str, MhdNode]] = {}
    for node in mhd_dataset.graph.nodes:
        if node.type_ not in type_map:
            type_map[node.type_] = {}
        type_map[node.type_][node.id_] = node
        all_nodes_map[node.id_] = node

    relationship_name_map: dict[str, dict[str, BaseRelationshipModel]] = {}
    for rel in mhd_dataset.graph.relationships:
        if rel.relationship_name not in relationship_name_map:
            relationship_name_map[rel.relationship_name] = {}
        relationship_name_map[rel.relationship_name][rel.id_] = rel

    if "study" not in type_map:
        logger.error("Study not found for in the input file")
        return
    study: graph_nodes.Study = next(iter(type_map.get("study", {}).values()))

    study_assays: list[graph_nodes.Assay] = (
        list(type_map.get("assay", {}).values()) or []
    )
    publications: list[MsAnnouncementPublication] = []
    if "publication" in type_map:
        graph_publications: list[graph_nodes.Publication] = list(
            type_map.get("publication", {}).values()
        )
        for node in graph_publications:
            item = MsAnnouncementPublication.model_validate(
                node.model_dump(by_alias=True)
            )
            publications.append(item)

    publication_status = None
    if not publications and "defined-as" in relationship_name_map:
        publication_status = list(relationship_name_map["defined-as"].values())
        if publication_status:
            status = publication_status[0]
            publication_status = convert_to_cv_term(nodes_map[status.target_ref])

    submitters, principal_investigators = get_submitters_and_pi(
        type_map, relationship_name_map
    )

    assay_types: OrderedDict[str, CvTerm] = OrderedDict()
    technology_types: OrderedDict[str, CvTerm] = OrderedDict()
    measurement_types: OrderedDict[str, CvTerm] = OrderedDict()
    omics_types: OrderedDict[str, CvTerm] = OrderedDict()
    for item in study_assays:
        if item.assay_type_ref in nodes_map:
            assay_type: graph_nodes.CvTermObject = nodes_map[item.assay_type_ref]
            if assay_type.accession not in assay_types:
                term = convert_to_cv_term(assay_type)
                assay_types[term.accession] = term

        if item.technology_type_ref in nodes_map:
            technology_type: graph_nodes.CvTermObject = nodes_map[
                item.technology_type_ref
            ]
            if technology_type.accession not in technology_types:
                term = convert_to_cv_term(technology_type)
                technology_types[term.accession] = term
        if item.measurement_type_ref in nodes_map:
            measurement_type: graph_nodes.CvTermObject = nodes_map[
                item.measurement_type_ref
            ]
            if measurement_type.accession not in measurement_types:
                term = convert_to_cv_term(measurement_type)
                measurement_types[term.accession] = term

        if item.omics_type_ref in nodes_map:
            omics_type: graph_nodes.CvTermObject = nodes_map[item.omics_type_ref]
            if omics_type.accession not in omics_types:
                term = convert_to_cv_term(omics_type)
                omics_types[term.accession] = term

    url_list = study.url_list
    repository_metadata_file_list = []
    if "metadata-file" in type_map:
        for ref in type_map.get("metadata-file", {}):
            metadata = convert_file(
                all_nodes_map,
                type_map,
                "metadata-file",
                ref,
                MsAnnouncementMetadataFile,
            )
            if metadata:
                repository_metadata_file_list.append(metadata)
    urn = get_urn(
        urn_namespace="mhd",
        repository_short_name="",
        dataset_id=study.mhd_identifier,
        node_class=AnnouncementMsProfile,
        identifier=None,
    )
    now = datetime.datetime.now(datetime.UTC)
    announcement = AnnouncementMsProfile(
        uri=urn,
        created_at=now,
        repository_name=mhd_dataset.repository_name,
        repository_short_name=mhd_dataset.repository_short_name,
        mhd_identifier=study.mhd_identifier,
        repository_identifier=study.repository_identifier,
        repository_revision=mhd_dataset.repository_revision,
        repository_revision_datetime=mhd_dataset.repository_revision_datetime or None,
        repository_revision_comment=mhd_dataset.repository_revision_comment or None,
        change_log=mhd_dataset.change_log if mhd_dataset.change_log else None,
        schema_name=announcement_schema_name,
        profile_uri=announcement_profile_uri,
        mhd_metadata_file_url=AnyUrl(mhd_file_url),
        mhd_metadata_file_hashes=mhd_metadata_file_hashes or None,
        url_list=url_list or None,
        license=study.license,
        license_name=study.license_name or None,
        name=study.title,
        description=study.description,
        submission_date=study.submission_date,
        public_release_date=study.public_release_date,
        doi=study.doi or None,
        submitters=submitters or None,
        principal_investigators=principal_investigators or None,
        measurement_type=list(measurement_types.values()) or None,
        technology_type=list(technology_types.values()) or None,
        assay_type=list(assay_types.values()) or None,
        omics_type=list(omics_types.values()) or None,
        repository_metadata_file_list=repository_metadata_file_list or None,
        result_file_list=None,
        raw_data_file_list=None,
        derived_data_file_list=None,
        supplementary_file_list=None,
        publications=publications if publications else publication_status,
        # study_factors=[],
        # characteristic_values=[],
    )

    update_keywords(all_nodes_map, relationship_name_map, announcement)
    announcement.descriptors = (
        get_descriptors(all_nodes_map, relationship_name_map) or None
    )
    update_protocol_parameters(
        all_nodes_map, relationship_name_map, type_map, study, announcement
    )
    update_study_factors(all_nodes_map, relationships_map, announcement)
    update_characteristic_values(all_nodes_map, relationships_map, announcement)

    if "result-file" in type_map:
        for ref in type_map.get("result-file", {}):
            file = convert_file(
                all_nodes_map, type_map, "result-file", ref, MsAnnouncementResultFile
            )
            if file:
                if not announcement.result_file_list:
                    announcement.result_file_list = []
                announcement.result_file_list.append(file)

    if "raw-data-file" in type_map:
        for ref in type_map.get("raw-data-file", {}):
            file = convert_file(
                all_nodes_map, type_map, "raw-data-file", ref, MsAnnouncementRawDataFile
            )
            if file:
                if not announcement.raw_data_file_list:
                    announcement.raw_data_file_list = []
                announcement.raw_data_file_list.append(file)
    if "derived-data-file" in type_map:
        for ref in type_map.get("derived-data-file", {}):
            file = convert_file(
                all_nodes_map,
                type_map,
                "derived-data-file",
                ref,
                MsAnnouncementDerivedDataFile,
            )
            if file:
                if not announcement.derived_data_file_list:
                    announcement.derived_data_file_list = []
                announcement.derived_data_file_list.append(file)
    if "supplementary-file" in type_map:
        for ref in type_map.get("supplementary-file", {}):
            file = convert_file(
                all_nodes_map,
                type_map,
                "supplementary-file",
                ref,
                MsAnnouncementSupplementaryFile,
            )
            if file:
                if not announcement.supplementary_file_list:
                    announcement.supplementary_file_list = []
                announcement.supplementary_file_list.append(file)
    identification_map = {}
    identification_links = relationship_name_map.get("identified-as")
    items = type_map.get("molecular-entity-identifier")
    if identification_links and items:
        for ref in identification_links:
            item = identification_links[ref]
            if item.target_ref in items:
                identification = items[item.target_ref]
                if item.source_ref not in identification_map:
                    identification_map[item.source_ref] = []
                identification_map[item.source_ref].append(identification)
    reported_molecular_entities: list[MsAnnouncementReportedMolecularEntity] = []
    for reported_entity_type in ("metabolite", "molecular-entity"):
        if reported_entity_type in type_map:
            for ref in type_map.get(reported_entity_type, {}):
                met = type_map.get(reported_entity_type, {})[ref]
                item = MsAnnouncementReportedMolecularEntity(name=met.name)
                reported_molecular_entities.append(item)

                if ref in identification_map:
                    identifications = identification_map[ref]
                    item.database_identifiers = [
                        convert_to_cv_term_value(x) for x in identifications
                    ]

    if reported_molecular_entities:
        announcement.reported_molecular_entities = reported_molecular_entities
        announcement.reported_molecular_entities.sort(key=lambda x: x.name)
    cv_sources = set()
    collect_cv_term_sources(announcement, cv_sources)
    definitions = {x.label: x for x in mhd_dataset.cv_definitions}
    cv_sources = list(cv_sources)
    cv_sources.sort()
    for source in cv_sources:
        if source in definitions:
            announcement.cv_definitions.append(definitions[source])

    logger.info("Writing to %s", announcement_file_path)
    Path(announcement_file_path).parent.mkdir(parents=True, exist_ok=True)
    with Path(announcement_file_path).open("w") as f:
        f.write(
            announcement.model_dump_json(indent=2, by_alias=True, exclude_none=True)
        )
