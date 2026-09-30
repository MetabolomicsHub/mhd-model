import inspect
import logging
import sys
from typing import Annotated, Any
from urllib.parse import quote

from pydantic import ConfigDict, Field

from mhd_model.model.v1_0.dataset.profiles.base import graph_nodes, relationships
from mhd_model.shared.base import MhdObjectType, UnitCvTerm
from mhd_model.shared.dataset_builder import MhDatasetBuilder
from mhd_model.shared.model import (
    BaseMhDatasetProfile,
    BaseMhdDataset,
    BaseMhdObjectModel,
    BaseReferencedObjectModel,
    BaseRelationshipModel,
    DatasetProfileConfiguration,
    IdentifiableMhdModel,
    MhdNode,
)

logger = logging.getLogger(__name__)

DEFAULT_GRAPH_NODES = Annotated[
    graph_nodes.CvTermValueObject
    | graph_nodes.CvTermObject
    | graph_nodes.Organization
    | graph_nodes.Person
    | graph_nodes.Project
    | graph_nodes.Study
    | graph_nodes.Protocol
    | graph_nodes.Publication
    | graph_nodes.Assay
    | graph_nodes.Specimen
    | graph_nodes.Subject
    | graph_nodes.Sample
    | graph_nodes.SampleRun
    | graph_nodes.SampleRunConfiguration
    | graph_nodes.MolecularEntity
    | graph_nodes.MetadataFile
    | graph_nodes.ResultFile
    | graph_nodes.RawDataFile
    | graph_nodes.DerivedDataFile
    | graph_nodes.SupplementaryFile
    | graph_nodes.CharacteristicDefinition
    | graph_nodes.FactorDefinition
    | graph_nodes.ParameterDefinition
    | graph_nodes.ReferencedObject
    | graph_nodes.Spectra,
    Field(description="Possible Default Node Type"),
]

DEFAULT_CV_TERM_TYPES = [
    "characteristic-type",
    "descriptor",
    "factor-type",
    "parameter-type",
    "protocol-type",
    "characteristic-value",
    "creator",
    "factor-value",
    "metabolite-identifier",
    "parameter-value",
]


def get_default_type_class_mapping(
    module: Any, base_classes: tuple[IdentifiableMhdModel, ...]
):
    items: dict[str, IdentifiableMhdModel] = {}
    alternative_types_label = "alternative_types"
    for _, node_class in inspect.getmembers(module, inspect.isclass):
        if issubclass(node_class, base_classes):
            node_class_type: type[IdentifiableMhdModel] = node_class
            json_schema_extra = node_class_type.model_config.get(
                "json_schema_extra", {}
            )
            alternative_types = json_schema_extra.get(alternative_types_label)
            default_type = node_class_type.model_fields.get("type_").default
            items[default_type] = node_class_type
            if alternative_types:
                for alternative_type in alternative_types:
                    items[alternative_type] = node_class_type
    return items


def get_unique_id_contribution_fields():
    contribution_map: dict[str, IdentifiableMhdModel] = {}
    contributions_label = "unique_value_contribution"
    for _, node_class in inspect.getmembers(graph_nodes, inspect.isclass):
        if issubclass(node_class, (MhdNode, BaseMhdDataset)):
            json_schema_extra = node_class.model_config.get("json_schema_extra", {})
            contributions = json_schema_extra.get(contributions_label)
            default_type = node_class.model_fields.get("type_").default
            contribution_map[default_type] = contributions

    return contribution_map


class DatasetProfileConfiguration_v1_0(DatasetProfileConfiguration):
    def get_default_cv_term_types(self) -> list[str]:
        return DEFAULT_CV_TERM_TYPES

    def get_default_relationship_type(self) -> str:
        return "default"

    def get_default_reference_object_type(self) -> str:
        return "default"

    def update_type_class_mapping(self):
        type_class_mapping = self.get_type_class_mapping()
        type_class_mapping["domain"] = self.get_default_type_class_mapping(
            modules=[graph_nodes],
            base_class=BaseMhdObjectModel,
            type_aliases_field="type_aliases",
        )
        type_class_mapping["reference"] = self.get_default_type_class_mapping(
            modules=[graph_nodes],
            base_class=BaseReferencedObjectModel,
            type_aliases_field="type_aliases",
        )
        type_class_mapping["relationship"] = self.get_default_type_class_mapping(
            modules=[relationships],
            base_class=BaseRelationshipModel,
            type_aliases_field="type_aliases",
        )
        type_class_mapping["cv"] = {"default": graph_nodes.CvTermObject}
        type_class_mapping["cv-value"] = {"default": graph_nodes.CvTermValueObject}


DEFAULT_PROFILE_CONFIG_V1_0 = DatasetProfileConfiguration_v1_0()


class MhDatasetBaseProfile_v1_0(BaseMhDatasetProfile):
    model_config = ConfigDict(
        json_schema_extra={
            "unique_value_alternatives": [
                ("doi",),
                ("mhd_identifier",),
                (
                    "repository_name",
                    "repository_identifier",
                ),
                ("additional_identifier_list",),
            ],
        }
    )
    type_: Annotated[MhdObjectType, Field(alias="type")] = MhdObjectType("base-v1-0")
    mhd_identifier: Annotated[None | str, Field()] = None

    @classmethod
    def get_config(cls) -> DatasetProfileConfiguration:
        return DEFAULT_PROFILE_CONFIG_V1_0


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s",
        datefmt="%d/%b/%Y %H:%M:%S",
        stream=sys.stdout,
    )
    dataset = MhDatasetBaseProfile_v1_0(
        schema_name="https://metabolomicshub.org/schema/mhd-v1.0.json",
        profile_uri="https://metabolomicshub.org/profile/mhd-v1.0",
        uri="urn:mhd:mtbls:mtbls1",
        repository_name="MetaboLights",
        repository_identifier="MTBLS1",
    )
    builder = MhDatasetBuilder[MhDatasetBaseProfile_v1_0](dataset=dataset)
    person = graph_nodes.Person(
        uri="urn:mhd:MTBLS:MTBLS1:person:ozgury@ebi.ac.uk",
        full_name="Ozgur Yurekten",
        orcid="1234-0001-8473-171X",
        email="ozgury@ebi.ac.uk",
        address="EMBL-EBI UK",
    )
    encoded_name = quote("EMBL-EBI UK")
    organization = graph_nodes.Organization(
        uri=f"urn:mhd:MTBLS:MTBLS1:organization:{encoded_name}",
        name="EMBL EBI",
        ror_id="https://ror.org/02catss52",
    )
    disease = graph_nodes.CvTermObject(
        type_="descriptor", source="MONDO", accession="MONDO:0000001", name="disease"
    )
    value = graph_nodes.CvTermValueObject(
        type_="mass-spectrometry-instrument",
        source="MONDO",
        accession="MONDO:0000001",
        name="disease",
        value="23",
        unit=UnitCvTerm(
            source="UO",
            accession="UO:0000196",
            name="pH",
        ),
    )
    reference = graph_nodes.ReferencedObject(referenced_id=person.id_)
    builder.add(item=person)
    builder.add(item=organization)
    builder.add(item=disease, use_label_for_invalid_cv_term=True)
    builder.add(item=reference)
    builder.add(item=value)

    builder.link(
        source=person,
        relationship_name="study-on",
        target=disease,
    )
    builder.link(
        source=person,
        relationship_name="affiliated-by",
        target=organization,
        reverse_relationship_name="has-employee",
    )
    builder.build_dataset(start_item_refs=[person.id_])
    values = list(dataset.graph.nodes)
    for item in values:
        logger.info(item)
