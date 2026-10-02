import abc
import datetime
import inspect
import logging
import uuid
from typing import Annotated, Any
from urllib.parse import quote

from pydantic import (
    AnyUrl,
    ConfigDict,
    Field,
    HttpUrl,
    InstanceOf,
    ValidationInfo,
    field_validator,
    model_validator,
)

from mhd_model.shared.base import (
    NAMESPACE_VALUE,
    AnyMhdId,
    AnyMhdNodeId,
    CvDefinition,
    CvTerm,
    CvTermObjectId,
    CvTermValue,
    CvTermValueObjectId,
    KeyValue,
    MhdConfigModel,
    MhdObjectId,
    MhdObjectType,
    MhdRelationshipObjectId,
    Revision,
)
from mhd_model.shared.fields import DOI
from mhd_model.shared.utils import generate_id_from_property, generate_unique_id

logger = logging.getLogger(__name__)


class IdentifiableMhdModel(MhdConfigModel, abc.ABC):
    prefix: Annotated[
        str,
        Field(exclude=True, description="prefix of the id"),
    ] = "node"
    id_: Annotated[
        None | AnyMhdId,
        Field(
            alias="id",
            description="Unique identifier of an MHD entity",
        ),
    ] = None
    type_: Annotated[
        None | MhdObjectType,
        Field(
            alias="type",
            description="The type property identifies the type of MHD Object. "
            "Its value MUST be the name of one of the types of MHD Objects",
        ),
    ]
    label: Annotated[None | str, Field(exclude=True)] = None
    created_by_ref: Annotated[
        None | CvTermValueObjectId,
        Field(
            description="The id property of the data-provider who created the object.",
        ),
    ] = None
    tag_list: Annotated[
        None | list[KeyValue],
        Field(description="Key-value descriptors related to the object."),
    ] = None
    external_reference_list: Annotated[
        None | list[KeyValue],
        Field(description="External references related to the object."),
    ] = None
    url_list: Annotated[
        None | list[AnyUrl],
        Field(
            description="List of web page or repository URLs for accessing the dataset.",
        ),
    ] = None

    def get_label(self) -> str:
        return self.id_ or ""

    def __hash__(self) -> int:
        return hash(self.id_)

    def __str__(self) -> int:
        return self.get_label()

    @field_validator("id_", mode="before")
    @classmethod
    def id_validator(cls, v) -> str:
        if isinstance(v, str):
            try:
                uuid.UUID(v.split(":")[2])
                return v
            except Exception:
                raise ValueError(f"invalid string structure {v}")
        raise ValueError("invalid type")

    @model_validator(mode="wrap")
    @classmethod
    def validate_model(
        cls, v: Any, handler, info: ValidationInfo
    ) -> "IdentifiableMhdModel":
        item: IdentifiableMhdModel = handler(v)
        context = info.context or {}
        if not item.id_:
            namespace = context.get("uuid_namespace") or None
            item.update_id(namespace)

        if not item.label:
            item.label = item.get_label()
        return item

    def update_id(self, namespace: None | str = None):
        if not namespace:
            namespace = NAMESPACE_VALUE
        self.id_ = self.get_unique_id(
            prefix=self.prefix, namespace=namespace, type_=self.type_
        )

    @abc.abstractmethod
    def get_unique_id(
        self, namespace: str, prefix: str, type_: str, property_name: None | str = None
    ) -> str: ...

    def generate_id_from_contribution_fields(
        self,
        namespace: str,
        prefix: None | str,
        type_: None | str,
        unique_value_contribution_field: None | str = "unique_value_alternatives",
    ) -> None | list[str]:
        if not type_:
            raise ValueError("type is not defined to create unique id")
        identifier_name = generate_unique_id(
            source=self,
            prefix=prefix,
            type_=type_,
            unique_value_contribution_field=unique_value_contribution_field,
        )
        identifier = str(uuid.uuid5(namespace, name=quote(identifier_name)))
        return f"{prefix}:{type_}:{identifier}"


class MhdRelationship(IdentifiableMhdModel):
    """Identifiable Mhd Relationship"""


class BaseRelationshipModel(MhdRelationship, abc.ABC):
    model_config = ConfigDict(
        json_schema_extra={
            "unique_value_fields": [
                "source_ref",
                "relationship_name",
                "target_ref",
                "source_role",
                "target_role",
            ]
        }
    )
    prefix: Annotated[
        str,
        Field(exclude=True, description="prefix of the id"),
    ] = "relationship"
    id_: Annotated[None | MhdRelationshipObjectId, Field(alias="id")] = None
    source_ref: MhdObjectId | CvTermObjectId | CvTermValueObjectId
    relationship_name: str
    target_ref: MhdObjectId | CvTermObjectId | CvTermValueObjectId
    source_role: None | str = None
    target_role: None | str = None

    def get_unique_id(
        self, namespace: str, prefix: str, type_: str, property_name: None | str = None
    ) -> str:
        return self.generate_id_from_contribution_fields(
            namespace=namespace,
            prefix=prefix or self.prefix,
            type_=type_ or self.type_,
            unique_value_contribution_field=property_name or "unique_value_fields",
        )

    def get_label(self):
        return self.relationship_name


class MhdNode(IdentifiableMhdModel):
    """Identifiable Mhd Node"""


class BaseReferencedObjectModel(MhdNode, abc.ABC):
    """Node or link reference defined in other MHD common data model file.
    The specified referenced_id must be already defined in the referenced file.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "unique_value_fields": ["referenced_id"],
        }
    )
    prefix: Annotated[
        None | MhdObjectType,
        Field(
            alias="type",
            description="The type property identifies the type of MHD Object. It must be `referenced-object`",
        ),
    ] = "reference"
    type_: Annotated[
        None | MhdObjectType,
        Field(
            alias="type",
            description="The type property identifies the type of MHD Object.",
        ),
    ] = "default"
    referenced_id: Annotated[
        AnyMhdId,
        Field(
            description="Id of referenced node or link. "
            "This id must be defined in the referenced dataset with the specified type_.",
        ),
    ]
    referenced_type: Annotated[
        None | MhdObjectType,
        Field(description="Type of referenced object."),
    ] = None
    dataset_id: Annotated[
        None | str,
        Field(description="Id of dataset contains referenced object."),
    ] = None
    dataset_uri: Annotated[
        None | str,
        Field(description="URI of dataset contains referenced object."),
    ] = None
    dataset_repository_identifier: Annotated[
        None | str,
        Field(description="Dataset Repository Identifier."),
    ] = None
    dataset_repository_revision: Annotated[
        None | str,
        Field(description="Dataset revision assigned by repository."),
    ] = None
    dataset_mhd_identifier: Annotated[
        None | str,
        Field(description="MHD Identifier of the dataset."),
    ] = None
    dataset_mhd_revision: Annotated[
        None | int,
        Field(description="Dataset revision assigned by MetabolomicsHub."),
    ] = None

    def get_unique_id(
        self, namespace: str, prefix: str, type_: str, property_name: None | str = None
    ) -> str:
        return self.generate_id_from_contribution_fields(
            namespace=namespace,
            prefix=prefix or self.prefix,
            type_=type_ or self.type_,
            unique_value_contribution_field=property_name or "unique_value_fields",
        )


class BaseCvTermModel(MhdNode, CvTerm, abc.ABC):
    model_config = ConfigDict(
        json_schema_extra={"unique_value_fields": ["source", "accession", "name"]}
    )
    prefix: Annotated[
        str,
        Field(exclude=True, description="prefix of the id"),
    ] = "cv"

    def get_unique_id(
        self, namespace: str, prefix: str, type_: str, property_name: None | str = None
    ) -> str:
        return self.generate_id_from_contribution_fields(
            namespace=namespace,
            prefix=prefix or self.prefix,
            type_=type_ or self.type_,
            unique_value_contribution_field=property_name or "unique_value_fields",
        )

    def get_label(self):
        return self.get_as_string()


class BaseCvTermValueModel(MhdNode, CvTermValue, abc.ABC):
    model_config = ConfigDict(
        json_schema_extra={
            "unique_value_fields": [
                ("source", "accession", "name", "value", "unit"),
            ]
        }
    )
    prefix: Annotated[
        str,
        Field(exclude=True, description="prefix of the id"),
    ] = "cv-value"

    def get_unique_id(
        self, namespace: str, prefix: str, type_: str, property_name: None | str = None
    ) -> str:
        return self.generate_id_from_contribution_fields(
            namespace=namespace,
            prefix=prefix or self.prefix,
            type_=type_ or self.type_,
            unique_value_contribution_field=property_name or "unique_value_fields",
        )

    def get_label(self):
        return self.get_as_string()


class UriBasedMhdObjectModel(IdentifiableMhdModel, abc.ABC):
    model_config = ConfigDict(
        json_schema_extra={
            "unique_value_fields": "uri",
            "unique_value_alternatives": [
                ("additional_identifier_list",),
            ],
        }
    )
    uri: Annotated[
        str,
        Field(description="Unified resource name"),
    ]
    repository_identifier: Annotated[
        None | str,
        Field(description="Assigned identifier by the source repository."),
    ] = None
    additional_identifier_list: Annotated[
        None | list[CvTerm],
        Field(
            description="List of additional database or secondary unique identifiers."
        ),
    ] = None

    alternative_id_list: Annotated[
        None | list[AnyMhdNodeId],
        Field(
            description="List of additional ids populated from unique value contribution fields."
        ),
    ] = None

    def get_unique_id(
        self, namespace: str, prefix: str, type_: str, property_name: None | str = None
    ) -> str:

        if not property_name:
            extra = self.__class__.model_config.get("json_schema_extra", {})
            property_name = extra.get("unique_value_fields") or "uri"
        identifier_name = generate_id_from_property(
            source=self,
            prefix=self.prefix,
            type_=self.type_,
            property_name=property_name,
        )

        identifier = str(uuid.uuid5(namespace, name=quote(identifier_name)))
        return f"{prefix}:{type_}:{identifier}"

    def update_id(self, namespace: None | str = None):
        if not namespace:
            namespace = NAMESPACE_VALUE
        self.id_ = self.get_unique_id(
            prefix=self.prefix, namespace=namespace, type_=self.type_
        )
        self.update_alternative_id_list(namespace=namespace)

    def update_alternative_id_list(self, namespace: str) -> list[str]:
        identifier_names = generate_unique_id(
            source=self, prefix=self.prefix, type_=self.type_, calculate_all=True
        )
        generated_ids = [
            f"{self.prefix}:{self.type_}:{uuid.uuid5(namespace, name=quote(x))!s}"
            for x in identifier_names or []
        ]

        self.alternative_id_list = [x for x in generated_ids if x != self.id_] or None


class BaseMhdObjectModel(UriBasedMhdObjectModel, MhdNode, abc.ABC):
    prefix: Annotated[
        str,
        Field(exclude=True, description="prefix of the id"),
    ] = "domain"


class ProfileEnabledDataset(MhdConfigModel):
    schema_name: Annotated[
        str, Field(alias="$schema", description="Schema name of the file")
    ]
    profile_uri: Annotated[str, Field(description="Validation Profiles")]
    created_at: Annotated[datetime.datetime | None, Field(description="Created at")] = (
        None
    )


class RevisionModel(MhdConfigModel):
    revision: Annotated[None | int, Field()] = None
    revision_comment: Annotated[None | str, Field()] = None
    revision_datetime: Annotated[None | datetime.datetime, Field()] = None
    repository_revision: Annotated[None | int, Field()] = None
    repository_revision_comment: Annotated[None | str, Field()] = None
    repository_revision_datetime: Annotated[None | datetime.datetime, Field()] = None
    change_log: Annotated[
        None | list[Revision], Field(min_length=1, description="Revision")
    ] = None


class BaseMhdDataset(UriBasedMhdObjectModel, ProfileEnabledDataset, RevisionModel):
    model_config = ConfigDict(
        json_schema_extra={
            "unique_value_alternatives": [
                ("doi",),
                (
                    "repository_name",
                    "repository_identifier",
                ),
                ("additional_identifier_list",),
            ],
        }
    )
    prefix: Annotated[
        str,
        Field(exclude=True, description="prefix of the id"),
    ] = "dataset"
    doi: Annotated[
        None | DOI,
        Field(description="Digital Object Identifier (DOI) for the dataset."),
    ] = None
    repository_name: Annotated[None | str, Field()]
    repository_short_name: Annotated[None | str, Field()]
    repository_identifier: Annotated[
        str,
        Field(
            description="Original dataset accession number or identifier in the source repository."
        ),
    ]
    license: Annotated[
        None | str | HttpUrl,
        Field(
            description="Dataset license URL defining usage rights for the study.",
            examples=[HttpUrl("https://creativecommons.org/publicdomain/zero/1.0/")],
        ),
    ] = None
    license_name: Annotated[
        None | str,
        Field(description="Dataset license name.", examples=["CC0 v1.0"]),
    ] = None
    name: Annotated[
        None | str,
        Field(description="Name of the dataset."),
    ] = None
    description: Annotated[
        None | str,
        Field(
            description="Comprehensive description or summary abstract of the dataset.",
        ),
    ] = None


class DatasetProfileConfiguration:
    def __init__(
        self,
        node_modules: None | list[object] = None,
        relationship_modules: None | list[object] = None,
        default_reference_object_type: None | str = None,
        default_relationship_type: None | str = "default",
        default_cv_term_types: None | list[str] = None,
        cv_term_class: None | type[BaseMhdObjectModel] = None,
        cv_term_value_class: None | type[BaseMhdObjectModel] = None,
        **kwargs,
    ):
        self._type_class_mapping: dict[
            str, dict[str, type[InstanceOf[IdentifiableMhdModel]]]
        ] = {}
        self.node_modules = node_modules
        self.relationship_modules = relationship_modules
        self.default_reference_object_type = default_reference_object_type
        self.default_relationship_type = default_relationship_type

        self.default_cv_term_types = default_cv_term_types or []
        self.cv_term_class = cv_term_class
        self.cv_term_value_class = cv_term_value_class
        self.kwargs = kwargs
        self.update_type_class_mapping()

    def get_default_cv_term_types(self) -> list[str]:
        return self.default_cv_term_types

    def get_default_relationship_type(self) -> str:
        return self.default_relationship_type

    def get_default_reference_object_type(self) -> str:
        return self.default_reference_object_type

    def update_type_class_mapping(self):
        type_class_mapping = self.get_type_class_mapping()

        type_class_mapping["domain"] = self.get_default_type_class_mapping(
            modules=self.node_modules,
            base_class=BaseMhdObjectModel,
            type_aliases_field="type_aliases",
        )
        type_class_mapping["reference"] = self.get_default_type_class_mapping(
            modules=self.node_modules,
            base_class=BaseReferencedObjectModel,
            type_aliases_field="type_aliases",
        )
        type_class_mapping["relationship"] = self.get_default_type_class_mapping(
            modules=self.relationship_modules,
            base_class=BaseRelationshipModel,
            type_aliases_field="type_aliases",
        )
        type_class_mapping["cv"] = {"default": self.cv_term_class}
        type_class_mapping["cv-value"] = {"default": self.cv_term_value_class}

    def get_type_class_mapping(
        self,
    ) -> dict[str, dict[str, type[InstanceOf[IdentifiableMhdModel]]]]:
        return self._type_class_mapping

    def get_type_class(
        self, prefix: str, type_: str
    ) -> dict[str, type[InstanceOf[IdentifiableMhdModel]]]:
        if not self._type_class_mapping:
            self.update_type_class_mapping()
        return self._type_class_mapping.get(prefix, {}).get(type_)

    def get_domain_object_type_class(
        self, type_: str
    ) -> type[InstanceOf[BaseMhdObjectModel]]:
        return self._type_class_mapping.get("domain", {}).get(type_)

    def get_relationship_type_class(
        self, type_: str
    ) -> type[InstanceOf[BaseRelationshipModel]]:
        return self._type_class_mapping.get("relationship", {}).get(type_)

    def get_reference_type_class(
        self, type_: str
    ) -> type[InstanceOf[BaseReferencedObjectModel]]:
        return self._type_class_mapping.get("reference", {}).get(type_)

    def get_cv_term_type_class(self) -> type[InstanceOf[BaseCvTermModel]]:
        return self._type_class_mapping.get("cv", {}).get("default")

    def get_cv_term_value_type_class(self) -> type[InstanceOf[BaseCvTermValueModel]]:
        return self._type_class_mapping.get("cv-value", {}).get("default")

    def get_default_type_class_mapping(
        self,
        modules: list[object],
        base_class: type[InstanceOf[MhdNode]],
        type_aliases_field: None | str = None,
    ) -> dict[str, type[InstanceOf[MhdNode]]]:
        items: dict[str, type[InstanceOf[MhdNode]]] = {}
        if not modules:
            return items
        if not type_aliases_field:
            type_aliases_field = "type_aliases"
        for module in modules:
            for _, rel_class_type in inspect.getmembers(module, inspect.isclass):
                if issubclass(rel_class_type, base_class):
                    json_schema_extra = rel_class_type.model_config.get(
                        "json_schema_extra", {}
                    )
                    type_aliases = json_schema_extra.get(type_aliases_field)
                    default_type = rel_class_type.model_fields.get("type_").default
                    items[default_type] = rel_class_type
                    if type_aliases:
                        for alternative_type in type_aliases:
                            items[alternative_type] = rel_class_type
        return items


class MhdModelValidationContext(MhdConfigModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    uuid_namespace: None | str = None
    repository_name: None | str = None
    repository_short_name: None | str = None
    repository_dataset_identifier: None | str = None

    dataset_configuration: None | DatasetProfileConfiguration = None


class CvEnabledDataset(BaseMhdDataset):
    cv_definitions: Annotated[None | list[CvDefinition], Field()] = []


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
        if isinstance(v, dict):
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
