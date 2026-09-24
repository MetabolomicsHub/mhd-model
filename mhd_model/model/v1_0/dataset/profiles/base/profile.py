import datetime
import uuid
from typing import Annotated, Any

from pydantic import Field, ValidationInfo, field_validator, model_validator
from pydantic.alias_generators import to_pascal

from mhd_model.model.v1_0.dataset.profiles.base import base, graph_nodes, relationships
from mhd_model.model.v1_0.dataset.profiles.base.base import (
    NAMESPACE_VALUE,
    BaseMhdModel,
    BaseMhdRelationship,
    CvTermObjectId,
    CvTermValueObjectId,
    IdentifiableMhdModel,
    MhdConfigModel,
    MhdObjectId,
    MhdObjectType,
)
from mhd_model.model.v1_0.dataset.profiles.base.relationships import Relationship
from mhd_model.shared.model import CvEnabledDataset
from mhd_model.shared.validation.definitions import MhdModelValidationContext

GraphNode = Annotated[
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
    | graph_nodes.Metabolite
    | graph_nodes.MetadataFile
    | graph_nodes.ResultFile
    | graph_nodes.RawDataFile
    | graph_nodes.DerivedDataFile
    | graph_nodes.SupplementaryFile
    | graph_nodes.BaseLabeledMhdModel
    | graph_nodes.ReferencedObject
    | graph_nodes.CharacteristicDefinition
    | graph_nodes.FactorDefinition
    | graph_nodes.ParameterDefinition,
    Field(description="Possible Node Type"),
]


class MhdGraph(MhdConfigModel):
    start_item_refs: Annotated[
        list[MhdObjectId | CvTermObjectId | CvTermValueObjectId], Field()
    ] = []
    nodes: Annotated[
        list[GraphNode],
        Field(),
    ] = []
    relationships: Annotated[list[Relationship], Field()] = []

    @field_validator("nodes", mode="before")
    @classmethod
    def node_validator(
        cls, v, info: None | ValidationInfo = None
    ) -> list[BaseMhdModel]:
        if isinstance(v, list):
            items = []
            for item in v:
                if isinstance(item, BaseMhdModel):
                    items.append(item)
                elif isinstance(item, dict):
                    val = cls.create_model(item, info=info)
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
    def create_model(item: dict[str, Any], info: None | ValidationInfo = None):
        type_: None | str = item.get("type")
        id_: None | str = item.get("id")
        if not type or not id_:
            raise ValueError("type and id properties are required.")
        if info and isinstance(info.context, dict):
            context = MhdModelValidationContext.model_validate(info.context)
            class_object = context.type_class_mapping.get(type_)
            if class_object:
                return class_object.model_validate(item)

        default_class_name = to_pascal(type_.replace("-", "_"))
        if id_.startswith("cv--"):
            return graph_nodes.CvTermObject.model_validate(item)
        elif id_.startswith("cv-value--"):
            return graph_nodes.CvTermValueObject.model_validate(item)
        elif hasattr(graph_nodes, default_class_name):
            class_object: type[BaseMhdModel] = getattr(graph_nodes, default_class_name)
            return class_object.model_validate(item)

        return None

    @staticmethod
    def get_node_class(
        item: dict[str, Any], type_class_mapping: None | type[MhdConfigModel] = None
    ):
        if (
            not item
            or not isinstance(item, dict)
            or not item.get("type")
            or not item.get("id")
        ):
            return
        return MhdGraph.get_mhd_class_by_type_and_id_prefix(
            id_=item.get("id"),
            node_type=item.get("type"),
            type_class_mapping=type_class_mapping,
        )

    @staticmethod
    def get_mhd_class_by_type_and_id_prefix(
        id_: str,
        node_type: str,
        type_class_mapping: None | dict[str, type[MhdConfigModel]] = None,
    ) -> None | IdentifiableMhdModel:
        node_class = None
        if type_class_mapping:
            node_class = type_class_mapping.get(node_type)
        if node_class:
            return node_class
        class_name = to_pascal(node_type.replace("-", "_"))
        class_object = None
        if hasattr(graph_nodes, class_name):
            class_object = getattr(graph_nodes, class_name)
        if not class_object:
            if hasattr(base, class_name):
                class_object = getattr(base, class_name)
            elif id_.startswith("cv--"):
                class_object = graph_nodes.CvTermObject
            elif id_.startswith("cv-value--"):
                class_object = graph_nodes.CvTermValueObject

        return class_object


class GraphEnabledBaseDataset(CvEnabledDataset):
    id_: Annotated[
        None | str,
        Field(
            alias="id",
            description="Unique identifier of the dataset",
        ),
    ] = None
    type_: Annotated[MhdObjectType, Field(frozen=True, alias="type")] = MhdObjectType(
        "dataset"
    )

    @model_validator(mode="wrap")
    @classmethod
    def validate_model(cls, v: Any, handler) -> "GraphEnabledBaseDataset":
        item: GraphEnabledBaseDataset = handler(v)
        if not item.type_:
            raise ValueError("type_ is required")
        identifier_name = f"{item.type_}--{item.get_unique_id(item.type_)}"
        identifier = str(uuid.uuid5(NAMESPACE_VALUE, name=identifier_name))
        item.id_ = item.id_ or f"dataset--{item.type_}--{identifier}"
        if hasattr(item, "label") and not item.label:
            item.label = item.get_label()
        return item


class MhDatasetBaseProfile(GraphEnabledBaseDataset):
    created_at: Annotated[datetime.datetime | None, Field(description="Created at")] = (
        None
    )
    name: Annotated[None | str, Field()] = None
    description: Annotated[None | str, Field()] = None
    graph: Annotated[MhdGraph, Field(json_schema_extra={"mhdGraphValidation": {}})] = (
        MhdGraph()
    )
