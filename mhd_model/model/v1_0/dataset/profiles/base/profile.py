import datetime
import inspect
import logging
import uuid
from typing import Annotated, Any

from pydantic import Field, ValidationInfo, model_validator
from pydantic.alias_generators import to_pascal

from mhd_model.model.v1_0.dataset.profiles.base import base, graph_nodes, relationships
from mhd_model.model.v1_0.dataset.profiles.base.base import (
    NAMESPACE_VALUE,
    BaseLabeledMhdModel,
    BaseMhdRelationship,
    BasicCvTermModel,
    BasicCvTermValueModel,
    CvTermObjectId,
    CvTermValueObjectId,
    GenericMhdEntityModel,
    IdentifiableMhdEntityModel,
    IdentifiableMhdModel,
    MhdConfigModel,
    MhdObjectId,
    MhdObjectType,
)
from mhd_model.shared.model import (
    CvEnabledDataset,
    generate_unique_id,
)
from mhd_model.shared.validation.definitions import MhdModelValidationContext

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

DEFAULT_CV_TERM_TYPES = {
    "characteristic-type",
    "descriptor",
    "factor-type",
    "parameter-type",
    "protocol-type",
    "characteristic-value",
    "data-provider",
    "factor-value",
    "metabolite-identifier",
    "parameter-value",
}


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
        if issubclass(
            node_class,
            (
                GenericMhdEntityModel,
                IdentifiableMhdEntityModel,
                BasicCvTermModel,
                BasicCvTermValueModel,
            ),
        ):
            json_schema_extra = node_class.model_config.get("json_schema_extra", {})
            contributions = json_schema_extra.get(contributions_label)
            default_type = node_class.model_fields.get("type_").default
            contribution_map[default_type] = contributions

    return contribution_map


class MhdGraph(MhdConfigModel):
    start_item_refs: Annotated[
        list[MhdObjectId | CvTermValueObjectId | CvTermObjectId], Field()
    ] = []
    nodes: Annotated[list[DEFAULT_GRAPH_NODES], Field()] = []
    relationships: Annotated[list[BaseMhdRelationship], Field()] = []

    @model_validator(mode="wrap")
    @classmethod
    def validate_model(
        cls, v: Any, handler: callable, info: ValidationInfo
    ) -> "MhdGraph":
        if isinstance(v, MhdGraph):
            return v
        graph = handler(v)

        if isinstance(graph, dict):
            context = None
            if info and isinstance(info.context, dict):
                context = MhdModelValidationContext.model_validate(info.context)
            if not context:
                context = MhdModelValidationContext()
            if not context.node_type_class_mapping:
                context.node_type_class_mapping = get_default_type_class_mapping(
                    module=graph_nodes,
                    base_classes=(GenericMhdEntityModel, IdentifiableMhdEntityModel),
                )

            if not context.relationship_type_class_mapping:
                context.relationship_type_class_mapping = (
                    get_default_type_class_mapping(
                        module=relationships,
                        base_classes=(BaseMhdRelationship),
                    )
                )

            for entities in ("nodes", "relationships"):
                nodes = v.get(entities) or []
                if isinstance(nodes, list):
                    items = []

                    for item in nodes:
                        if isinstance(item, MhdConfigModel):
                            items.append(item)
                        elif isinstance(item, dict):
                            val = cls.create_model(item, context=context)
                            if not val:
                                raise ValueError("invalid type in nodes")
                            items.append(val)
                        else:
                            raise ValueError("invalid type in nodes")
                    graph[entities] = items

        return graph

    @staticmethod
    def create_model(item: dict[str, Any], context: MhdModelValidationContext):
        type_: None | str = item.get("type")
        id_: None | str = item.get("id")
        if not type or not id_:
            raise ValueError("type and id properties are required.")
        if not context:
            raise ValueError("validation context is not defined.")
        node_type_class_mapping = context.node_type_class_mapping or {}

        class_object: MhdConfigModel = node_type_class_mapping.get(type_, None)
        if not class_object:
            relationship_type_class_mapping = (
                context.relationship_type_class_mapping or {}
            )
            class_object = relationship_type_class_mapping.get(type_, None)
        if class_object:
            # default_type = class_object.model_fields.get("type_").default
            # item["type"] = default_type
            return class_object.model_validate(item)
        if id_.startswith("cv--"):
            return graph_nodes.CvTermObject.model_validate(item)
        elif id_.startswith("cv-value--"):
            return graph_nodes.CvTermValueObject.model_validate(item)

        raise ValueError(f"There is no class for type {type_}")

    @staticmethod
    def get_node_class(
        item: dict[str, Any],
        mhd_model_validation_context: None | MhdModelValidationContext = None,
    ):
        if (
            not item
            or not isinstance(item, dict)
            or not item.get("type")
            or not item.get("id")
        ):
            return
        node_type_class_mapping = None
        if mhd_model_validation_context:
            node_type_class_mapping = (
                mhd_model_validation_context.node_type_class_mapping or None
            )
        return MhdGraph.get_mhd_class_by_type_and_id_prefix(
            id_=item.get("id"),
            node_type=item.get("type"),
            node_type_class_mapping=node_type_class_mapping,
        )

    def update_graph_ids(self, inline: bool = False) -> "MhdGraph":
        updated_node_ids = {}
        updated_node_types = {}
        updated_rel_ids = {}
        updated_rel_types = {}
        node_class_refs: dict[str, list[str]] = {}
        node_id_mapper = {}
        node_actions: dict[str, list[tuple[MhdConfigModel, str, Any]]] = {}
        rel_actions: dict[str, list[tuple[MhdConfigModel, str, Any]]] = {}
        new_start_items = []
        if inline:
            graph = self
        else:
            graph = self.model_copy()
        for node in graph.nodes or []:
            node_actions[node.id_] = []
            prefix = node.id_.split("--")[0]
            default_type_ = node.__class__.model_fields.get("type_").default
            node_id_mapper[node.id_] = node.id_
            expected_type = node.type_
            if prefix == "mhd":
                expected_type = default_type_
            try:
                new_unique_id = node.get_unique_id(
                    namespace=NAMESPACE_VALUE, prefix=prefix, type_=expected_type
                )
            except Exception as ex:
                raise ex
            if new_unique_id != node.id_:
                updated_node_ids[node.id_] = new_unique_id
                node_actions[node.id_].append((node, "id_", new_unique_id))
                node_id_mapper[node.id_] = new_unique_id
                node_id_mapper[new_unique_id] = new_unique_id

            if expected_type != node.type_:
                updated_node_types[node.id_] = expected_type
                node_actions[node.id_].append((node, "type_", expected_type))

        for node in graph.nodes or []:
            reference_fields = node_class_refs.get(node.__class__) or []
            if node.__class__ not in reference_fields:
                reference_fields = []
                node_class_refs[node.__class__] = reference_fields
                for name in node.__class__.model_fields:
                    if name.endswith(("_ref", "_refs")):
                        node_class_refs[node.__class__].append(name)
            for name in reference_fields:
                value = getattr(node, name)
                if not value:
                    continue
                if name.endswith("_ref"):
                    # setattr(node, name, updated_node_ids[value])
                    if value in updated_node_ids:
                        node_actions[node.id_].append(
                            (node, name, node_id_mapper[value])
                        )
                else:
                    updated = False
                    new_values = []
                    for x in value:
                        new_values.append(node_id_mapper.get(x))
                        if x in updated_node_ids:
                            updated = True
                    if updated:
                        node_actions[node.id_].append((node, name, new_values))

        for item in graph.start_item_refs or []:
            new_start_items.append(node_id_mapper[item])

        for rel in graph.relationships or []:
            rel_actions[rel.id_] = []
            if rel.source_ref in updated_node_ids:
                rel_actions[rel.id_].append(
                    (rel, "source_ref", updated_node_ids[rel.source_ref])
                )
            if rel.target_ref in updated_node_ids:
                rel_actions[rel.id_].append(
                    (rel, "target_ref", updated_node_ids[rel.target_ref])
                )

            default_type_ = rel.__class__.model_fields.get("type_").default
            prefix = rel.id_.split("--")[0]
            new_unique_id = node.get_unique_id(
                namespace=NAMESPACE_VALUE, prefix=prefix, type_=default_type_
            )
            if new_unique_id != node.id_:
                updated_rel_ids[rel.id_] = new_unique_id
                rel_actions[rel.id_].append((rel, "id_", new_unique_id))
            if default_type_ != rel.type_:
                updated_rel_types[node.id_] = default_type_
                rel_actions[rel.id_].append((rel, "type_", default_type_))
        logger.debug("Updated node ids: %s", len(updated_node_ids))
        logger.debug("Updated node types: %s", len(updated_node_types))
        logger.debug("Updated relationship ids: %s", len(updated_rel_ids))
        logger.debug("Updated relationship types: %s", len(updated_rel_types))

        for group in (node_actions, rel_actions):
            for actions in group.values():
                for action in actions:
                    node, name, value = action
                    setattr(node, name, value)

        graph.start_item_refs = new_start_items

        return graph

    @staticmethod
    def get_mhd_class_by_type_and_id_prefix(
        id_: str,
        node_type: str,
        node_type_class_mapping: None | dict[str, type[MhdConfigModel]] = None,
    ) -> None | IdentifiableMhdModel:
        node_class = None
        if node_type_class_mapping:
            node_class = node_type_class_mapping.get(node_type)
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


class GraphEnabledBaseDataset(CvEnabledDataset, BaseLabeledMhdModel):
    id_: Annotated[
        None | str,
        Field(
            alias="id",
            description="Unique identifier of the dataset",
        ),
    ] = None
    type_: Annotated[MhdObjectType, Field(alias="type")] = MhdObjectType("dataset")

    @model_validator(mode="wrap")
    @classmethod
    def validate_model(cls, v: Any, handler) -> "GraphEnabledBaseDataset":
        item: GraphEnabledBaseDataset = handler(v)
        if not item.id_:
            item.id_ = item.get_unique_id(
                prefix="dataset", namespace=NAMESPACE_VALUE, type_=item.type_
            )
        if hasattr(item, "label") and not item.label:
            item.label = item.get_label()
        return item

    def get_unique_id(self, namespace: str, prefix: str, type_: str):
        if not type_:
            raise ValueError("type is not defined to create unique id")
        identifier_name = generate_unique_id(source=self, type_=type_)
        identifier = str(uuid.uuid5(namespace, name=identifier_name))
        return f"{prefix}--{type_}--{identifier}"

    def get_label(self):
        return self.doi or self.mhd_identifier or self.repository_identifier or ""


class MhDatasetBaseProfile(GraphEnabledBaseDataset):
    created_at: Annotated[datetime.datetime | None, Field(description="Created at")] = (
        None
    )
    name: Annotated[None | str, Field()] = None
    description: Annotated[None | str, Field()] = None
    graph: Annotated[MhdGraph, Field(json_schema_extra={"mhdGraphValidation": {}})] = (
        MhdGraph()
    )

    def clone_dataset(self, consolidate_graph: bool = False) -> "MhDatasetBaseProfile":
        new_dataset = self.model_copy()
        if consolidate_graph:
            new_dataset.graph.update_graph_ids(inline=True)
        return new_dataset

    def regenerate_ids(self, inline: bool = False) -> "MhDatasetBaseProfile":

        dataset = self if inline else self.model_copy()
        dataset.graph.update_graph_ids(inline=True)
        dataset.id_ = dataset.get_unique_id(
            prefix="dataset", namespace=NAMESPACE_VALUE, type_=dataset.type_
        )
        return dataset
