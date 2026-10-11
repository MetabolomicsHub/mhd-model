import inspect
import logging
from typing import Annotated, Any

from pydantic import Field

from mhd_model.model.base import BaseMhdFile
from mhd_model.model.v1_0.dataset.profiles.base import graph_nodes, relationships
from mhd_model.shared.base import MhdObjectType
from mhd_model.shared.model import (
    BaseMhdDataset,
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
    "data-provider",
    "factor-value",
    "molecular-entity-identifier",
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
    def __init__(self, **kwargs):
        super().__init__(
            node_modules=[graph_nodes],
            relationship_modules=[relationships],
            default_reference_object_type="default",
            default_relationship_type="default",
            default_cv_term_types=DEFAULT_CV_TERM_TYPES,
            cv_term_class=graph_nodes.CvTermObject,
            cv_term_value_class=graph_nodes.CvTermValueObject,
            **kwargs,
        )


DEFAULT_PROFILE_CONFIG_V1_0 = DatasetProfileConfiguration_v1_0()


class MhDatasetBaseProfile_v1_0(BaseMhdFile):
    type_: Annotated[MhdObjectType, Field(alias="type")] = MhdObjectType("base-v1-0")

    @classmethod
    def get_config(cls) -> DatasetProfileConfiguration:
        return DEFAULT_PROFILE_CONFIG_V1_0
