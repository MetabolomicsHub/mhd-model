import abc
import datetime
import inspect
import logging
import uuid
from typing import Annotated, Any

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
from mhd_model.shared.utils import generate_unique_id

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

    def get_unique_id(
        self,
        namespace: str,
        prefix: None | str,
        type_: None | str,
        unique_value_contribution_extra_field: None | str = "unique_value_fields",
    ) -> None | list[str]:
        if not type_:
            raise ValueError("type is not defined to create unique id")
        identifier_name = generate_unique_id(
            source=self,
            prefix=prefix,
            type_=type_,
            unique_value_contribution_extra_field=unique_value_contribution_extra_field,
        )
        identifier = str(uuid.uuid5(namespace, name=identifier_name))
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


class BaseCvTermModel(MhdNode, CvTerm, abc.ABC):
    model_config = ConfigDict(
        json_schema_extra={"unique_value_fields": ["source", "accession", "name"]}
    )
    prefix: Annotated[
        str,
        Field(exclude=True, description="prefix of the id"),
    ] = "cv"

    def get_label(self):
        return self.get_as_string()


class BaseCvTermValueModel(MhdNode, CvTermValue, abc.ABC):
    model_config = ConfigDict(
        json_schema_extra={
            "unique_value_fields": [
                "source",
                "accession",
                "name",
                "value",
                "unit",
            ]
        }
    )
    prefix: Annotated[
        str,
        Field(exclude=True, description="prefix of the id"),
    ] = "cv-value"

    def get_label(self):
        return self.get_as_string()


class UriBasedMhdObjectModel(IdentifiableMhdModel, abc.ABC):
    model_config = ConfigDict(
        json_schema_extra={
            "unique_value_fields": ["uri"],
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
        None | list[CvTermValue],
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

    def update_alternative_id_list(self, namespace: str) -> list[str]:
        identifier_names = generate_unique_id(
            source=self,
            prefix=self.prefix,
            type_=self.type_,
            calculate_all=True,
            unique_value_contribution_extra_field="unique_value_alternatives",
        )
        generated_ids = [
            f"{self.prefix}:{self.type_}:{uuid.uuid5(namespace, name=x)!s}"
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
            "unique_value_fields": ["uri"],
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


class CvEnabledDataset(BaseMhdDataset):
    cv_definitions: Annotated[None | list[CvDefinition], Field()] = []
