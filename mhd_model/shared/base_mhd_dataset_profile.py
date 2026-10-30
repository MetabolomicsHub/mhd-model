import abc
import logging
from typing import Annotated, Any

from pydantic import (
    ConfigDict,
    Field,
    InstanceOf,
    ValidationInfo,
    model_validator,
)

from mhd_model.shared.base import (
    NAMESPACE_VALUE,
    CvTermObjectId,
    CvTermValueObjectId,
    MhdConfigModel,
    MhdObjectId,
)
from mhd_model.shared.model import (
    BaseRelationshipModel,
    CvEnabledDataset,
    DatasetProfileConfiguration,
    MhdNode,
)
from mhd_model.shared.validation.base_cv_term_helper import BaseCvTermHelper

logger = logging.getLogger(__name__)


class MhdModelValidationContext(MhdConfigModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    uuid_namespace: None | str = None
    repository_name: None | str = None
    repository_short_name: None | str = None
    repository_dataset_identifier: None | str = None

    dataset_configuration: None | DatasetProfileConfiguration = None
    cv_term_helper: None | BaseCvTermHelper = None


class MhdGraph(MhdConfigModel):
    start_item_refs: Annotated[
        list[MhdObjectId | CvTermValueObjectId | CvTermObjectId], Field()
    ] = []
    nodes: Annotated[list[InstanceOf[MhdNode]], Field()] = []
    relationships: Annotated[list[InstanceOf[BaseRelationshipModel]], Field()] = []

    @model_validator(mode="wrap")
    @classmethod
    def validate_model(
        cls, v: Any, handler: callable, info: ValidationInfo
    ) -> "MhdGraph":
        if isinstance(v, MhdGraph):
            return v
        context = None
        if info:
            if isinstance(info.context, MhdModelValidationContext):
                context = info.context
            elif info and isinstance(info.context, dict):
                context = MhdModelValidationContext.model_validate(info.context)
        if v and isinstance(v, dict):
            for entities in ("nodes", "relationships"):
                nodes = v.get(entities) or []
                if isinstance(nodes, list):
                    items = []

                    for item in nodes:
                        if isinstance(item, MhdConfigModel):
                            items.append(item)
                        elif isinstance(item, dict):
                            if not context:
                                raise ValueError(
                                    f"Context is required to convert '{item}'"
                                )
                            val = cls.create_model(item, context=context)
                            if not val:
                                raise ValueError("invalid type in nodes")
                            items.append(val)
                        else:
                            raise ValueError("invalid type in nodes")
                    v[entities] = items

        graph = handler(v)
        return graph

    @staticmethod
    def create_model(item: dict[str, Any], context: MhdModelValidationContext):
        type_: None | str = item.get("type")
        id_: None | str = item.get("id")

        if not type_ or not id_:
            raise ValueError("type and id properties are required.")
        if not context:
            raise ValueError("validation context is not defined.")
        prefix = id_.split(":")[0]
        config = context.dataset_configuration
        if prefix == "cv":
            node_class_object = config.get_cv_term_type_class()
        elif prefix == "cv-value":
            node_class_object = config.get_cv_term_value_type_class()
        elif prefix == "relationship":
            node_class_object = config.get_relationship_type_class(type_)
        else:
            node_class_object = config.get_type_class(prefix, type_)

        if node_class_object:
            return node_class_object.model_validate(item)

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
        if mhd_model_validation_context:
            config = mhd_model_validation_context.dataset_configuration
            mappings = config.get_type_class_mapping() or {}
        id_ = item.get("id", "")
        prefix = id_.split(":")[0]
        node_type = item.get("type")
        return mappings.get(prefix, {}).get(node_type)

    def update_graph_ids(self, inline: bool = False) -> "MhdGraph":
        updated_node_ids: dict[str, str] = {}
        updated_node_types = {}
        updated_rel_ids = {}
        updated_rel_types = {}
        node_class_refs: dict[str, list[str]] = {}
        node_id_mapper = {}
        node_actions: dict[str, list[tuple[MhdNode, str, Any]]] = {}
        rel_actions: dict[str, list[tuple[BaseRelationshipModel, str, Any]]] = {}
        new_start_items = []
        if inline:
            graph = self
        else:
            graph = self.model_copy()
        for node in graph.nodes or []:
            node_actions[node.id_] = []
            prefix = node.id_.split(":")[0]
            default_type_ = node.__class__.model_fields.get("type_").default
            node_id_mapper[node.id_] = node.id_
            expected_type = node.type_
            if prefix == "domain":
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
            prefix = rel.id_.split(":")[0]
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


class BaseMhDatasetProfile(CvEnabledDataset, abc.ABC):
    graph: Annotated[MhdGraph, Field(json_schema_extra={"mhdGraphValidation": {}})] = (
        MhdGraph()
    )

    @model_validator(mode="wrap")
    @classmethod
    def validate_model(
        cls, v: Any, handler: callable, info: ValidationInfo
    ) -> "BaseMhDatasetProfile":
        item: BaseMhDatasetProfile = handler(v)
        item.get_config().update_type_class_mapping()
        namespace = (
            info.context.uuid_namespace or NAMESPACE_VALUE
            if isinstance(info.context, MhdModelValidationContext)
            else NAMESPACE_VALUE
        )
        if not namespace:
            namespace = (
                info.context.get("uuid_namespace") or NAMESPACE_VALUE
                if isinstance(info.context, dict)
                else NAMESPACE_VALUE
            )
        item.update_id(namespace=namespace)
        item.update_alternative_id_list(namespace=namespace)
        return item

    @classmethod
    def get_config(cls) -> DatasetProfileConfiguration: ...

    def clone_dataset(self, consolidate_graph: bool = False) -> "BaseMhDatasetProfile":
        new_dataset = self.model_copy()
        if consolidate_graph:
            new_dataset.graph.update_graph_ids(inline=True)
        return new_dataset

    def regenerate_ids(self, inline: bool = False) -> "BaseMhDatasetProfile":

        dataset = self if inline else self.model_copy()
        dataset.graph.update_graph_ids(inline=True)
        dataset.id_ = dataset.get_unique_id(
            prefix="dataset", namespace=NAMESPACE_VALUE, type_=dataset.type_
        )
        return dataset
