from typing import Any

from pydantic import Field, field_validator
from pydantic.alias_generators import to_pascal
from typing_extensions import Annotated

from mhd_model.model.v0_1.dataset.profiles.base import base, graph_nodes, relationships
from mhd_model.model.v0_1.dataset.profiles.base.base import (
    BaseMhdModel,
    BaseMhdRelationship,
    CvTermObjectId,
    CvTermValueObjectId,
    IdentifiableMhdModel,
    MhdConfigModel,
    MhdObjectId,
    MhdObjectType,
)
from mhd_model.model.v0_1.dataset.profiles.base.relationships import Relationship
from mhd_model.shared.model import CvEnabledDataset


class MhdGraph(MhdConfigModel):
    start_item_refs: Annotated[
        list[MhdObjectId | CvTermObjectId | CvTermValueObjectId], Field()
    ] = []
    nodes: Annotated[
        list[
            graph_nodes.CvTermValueObject
            | graph_nodes.CvTermObject
            | graph_nodes.Person
            | graph_nodes.Project
            | graph_nodes.Study
            | graph_nodes.Protocol
            | graph_nodes.Publication
            | graph_nodes.BasicAssay
            | graph_nodes.Assay
            | graph_nodes.Specimen
            | graph_nodes.Subject
            | graph_nodes.Sample
            | graph_nodes.SampleRun
            | graph_nodes.SampleRunConfiguration
            | graph_nodes.Metabolite
            | graph_nodes.MetadataFile
            | graph_nodes.ResultFile
            | graph_nodes.RawDataFile
            | graph_nodes.DerivedDataFile
            | graph_nodes.SupplementaryFile
            | graph_nodes.BaseLabeledMhdModel
        ],
        Field(),
    ] = []
    relationships: Annotated[list[Relationship], Field()] = []

    @field_validator("nodes", mode="before")
    @classmethod
    def node_validator(cls, v) -> list[BaseMhdModel]:
        if isinstance(v, list):
            items = []
            for item in v:
                if isinstance(item, BaseMhdModel):
                    items.append(item)
                elif isinstance(item, dict):
                    val = cls.create_model(item)
                    if not val:
                        raise ValueError("invalid type in nodes")
                    items.append(val)
                else:
                    raise ValueError("invalid type in nodes")
            return items

        raise ValueError("invalid type")

    @field_validator("relationships", mode="before")
    @classmethod
    def relationship_validator(cls, v) -> list[BaseMhdRelationship]:
        if isinstance(v, list):
            items = []
            for item in v:
                if isinstance(item, BaseMhdRelationship):
                    items.append(item)
                elif isinstance(item, dict):
                    class_name = to_pascal(item["type"].replace("-", "_"))
                    if hasattr(relationships, class_name):
                        class_object = getattr(relationships, class_name)
                        items.append(class_object.model_validate(item))
                else:
                    raise ValueError("invalid type in nodes")
            return items

        raise ValueError("invalid type")

    @staticmethod
    def create_model(item: dict[str, Any]):
        class_name = to_pascal(item["type"].replace("-", "_"))
        if item["id"].startswith("cv--"):
            return graph_nodes.CvTermObject.model_validate(item)
        elif item["id"].startswith("cv-value--"):
            return graph_nodes.CvTermValueObject.model_validate(item)
        elif hasattr(graph_nodes, class_name):
            class_object = getattr(graph_nodes, class_name)
            return class_object.model_validate(item)
        return None

    @staticmethod
    def get_node_class(item: dict[str, Any]):
        if not item or not item.get("type") or not item.get("id"):
            return None

    @staticmethod
    def get_mhd_class_by_type(node_type: str) -> None | IdentifiableMhdModel:
        class_name = to_pascal(node_type.replace("-", "_"))
        class_object = None
        if hasattr(graph_nodes, class_name):
            class_object = getattr(graph_nodes, class_name)
        if not class_object:
            class_object = getattr(base, class_name)
        return class_object


class GraphEnabledBaseDataset(CvEnabledDataset): ...


class MhDatasetBaseProfile(GraphEnabledBaseDataset):
    id_: Annotated[
        None | str,
        Field(
            alias="id",
            description="Unique identifier of graph node",
        ),
    ] = None
    type_: Annotated[MhdObjectType, Field(frozen=True, alias="type")] = MhdObjectType(
        "base-dataset"
    )
    name: Annotated[None | str, Field()] = None
    description: Annotated[None | str, Field()] = None
    graph: Annotated[MhdGraph, Field(json_schema_extra={"mhdGraphValidation": {}})] = (
        MhdGraph()
    )
