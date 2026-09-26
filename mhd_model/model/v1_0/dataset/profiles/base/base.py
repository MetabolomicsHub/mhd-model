import datetime
import uuid
from typing import Annotated, Any

from pydantic import AnyUrl, ConfigDict, Field, field_validator, model_validator
from pydantic.alias_generators import to_pascal

from mhd_model.shared.model import (
    CvTerm,
    CvTermValue,
    MhdConfigModel,
    QuantitativeValue,
    generate_unique_id,
)

NAMESPACE_VALUE = uuid.UUID("efb4f8e4-d08b-4979-916e-600c4985e7f2")
base_suffix = (
    r"[-a-zA-Z0-9]+--[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"
)
OBJECT_UUID_PATTERN = rf"^mhd--{base_suffix}"
CV_TERM_UUID_PATTERN = rf"^cv--{base_suffix}"
CV_TERM_VALUE_UUID_PATTERN = rf"^cv-value--{base_suffix}"
RELATIONSHIP_UUID_PATTERN = rf"^rel--{base_suffix}"
OBJECT_TYPE_PATTERN = r"^[a-z0-9]+(?:-[a-z0-9]+)*$"


MhdObjectType = Annotated[str, Field(..., pattern=OBJECT_TYPE_PATTERN)]
MhdObjectType.__name__ = "MhdObjectType"

# MhdObjectType = Annotated[MhdObjectType, Field()]
MhdObjectId = Annotated[str, Field(pattern=OBJECT_UUID_PATTERN)]
MhdObjectId.__name__ = "MhdObjectId"
CvTermObjectId = Annotated[str, Field(pattern=CV_TERM_UUID_PATTERN)]
CvTermObjectId.__name__ = "CvTermObjectId"
CvTermValueObjectId = Annotated[str, Field(pattern=CV_TERM_VALUE_UUID_PATTERN)]
CvTermValueObjectId.__name__ = "CvTermValueObjectId"
MhdRelationshipObjectId = Annotated[str, Field(pattern=RELATIONSHIP_UUID_PATTERN)]
MhdRelationshipObjectId.__name__ = "MhdRelationshipObjectId"


class KeyValue(MhdConfigModel):
    key: None | MhdObjectId | CvTermObjectId | str | CvTerm = None
    value: (
        None
        | MhdObjectId
        | CvTermObjectId
        | CvTermValueObjectId
        | str
        | int
        | datetime.datetime
        | bool
        | float
        | CvTerm
        | CvTermValue
        | QuantitativeValue
    ) = None


class IdentifiableMhdModel(MhdConfigModel):
    id_: Annotated[
        None
        | MhdObjectId
        | CvTermObjectId
        | CvTermValueObjectId
        | MhdRelationshipObjectId,
        Field(
            alias="id",
            description="Unique identifier of graph node",
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

    def __hash__(self) -> int:
        return hash(self.id_)


class BaseMhdModel(IdentifiableMhdModel):
    model_config = ConfigDict(
        populate_by_name=True,
        json_schema_serialization_defaults_required=True,
        field_title_generator=lambda field_name, field_info: to_pascal(
            field_name.replace("_", " ").strip()
        ),
    )
    id_: Annotated[
        None | MhdObjectId,
        Field(
            alias="id", description="The id property uniquely identifies the object."
        ),
    ] = None
    type_: Annotated[None | MhdObjectType, Field(frozen=False, alias="type")] = (
        "base-mhd-model"
    )
    created_by_ref: Annotated[
        None | CvTermValueObjectId,
        Field(
            description="The id property of the data-provider who created the object.",
        ),
    ] = None
    tag_list: Annotated[
        None | list[KeyValue],
        Field(description="Key-value tags related to the object."),
    ] = None
    external_reference_list: Annotated[
        None | list[KeyValue],
        Field(description="External references related to the object."),
    ] = None
    url_list: Annotated[
        None | list[AnyUrl],
        Field(description="URL list related to the object."),
    ] = None
    repository_identifier: Annotated[
        None | str,
        Field(description="Unique identifier in the source repository."),
    ] = None

    @field_validator("id_", mode="before")
    @classmethod
    def id_validator(cls, v) -> str:
        if isinstance(v, str):
            try:
                uuid.UUID(v.split("--")[2])
                return v
            except Exception:
                raise ValueError(f"invalid string structure {v}")
        raise ValueError("invalid type")

    @model_validator(mode="wrap")
    @classmethod
    def validate_model(cls, v: Any, handler) -> "BaseMhdModel":
        item: BaseMhdModel = handler(v)
        if not item.id_:
            item.id_ = item.get_unique_id(
                prefix="mhd", namespace=NAMESPACE_VALUE, type_=item.type_
            )
        return item


class BaseLabeledMhdModel(BaseMhdModel):
    label: Annotated[None | str, Field(exclude=True)] = None

    @model_validator(mode="wrap")
    @classmethod
    def validate_model(cls, v: Any, handler) -> "BaseLabeledMhdModel":
        item: BaseLabeledMhdModel = handler(v)
        if not item.id_:
            item.id_ = item.get_unique_id(
                prefix="mhd", namespace=NAMESPACE_VALUE, type_=item.type_
            )
        if not item.label:
            item.label = item.get_label()
        return item

    def get_label(self) -> str:
        return self.id_ or ""


class IdentifiableMhdEntityModel(BaseLabeledMhdModel):
    additional_identifier_list: Annotated[
        None | list[CvTerm],
        Field(description="List of additional database or secondary identifiers."),
    ] = None


class GenericMhdEntityModel(BaseLabeledMhdModel):
    model_config = ConfigDict(
        populate_by_name=True,
        json_schema_serialization_defaults_required=True,
        field_title_generator=lambda field_name, field_info: to_pascal(
            field_name.replace("_", " ").strip()
        ),
        json_schema_extra={
            "unique_value_contribution": [
                ("global_identifier",),
                ("additional_identifier_list",),
                ("repository_identifier",),
            ]
        },
    )
    global_identifier: Annotated[
        None | CvTerm,
        Field(description="Unique identifier in the source repository."),
    ] = None
    additional_identifier_list: Annotated[
        None | list[CvTerm],
        Field(
            description="List of additional database or secondary identifiers for the node."
        ),
    ] = None


class BasicCvTermModel(CvTerm, IdentifiableMhdModel):
    id_: Annotated[
        None | CvTermObjectId,
        Field(
            ...,
            alias="id",
            description="The id property uniquely identifies the object.",
        ),
    ] = None
    label: Annotated[None | str, Field(exclude=True)] = None
    type_: Annotated[None | MhdObjectType, Field(..., alias="type")]

    @field_validator("id_", mode="before")
    @classmethod
    def id_validator(cls, v) -> str:
        if isinstance(v, str):
            try:
                uuid.UUID(v.split("--")[2])
                return v
            except Exception:
                raise ValueError(f"invalid string structure {v}")
        raise ValueError("invalid type")

    @model_validator(mode="wrap")
    @classmethod
    def validate_model(cls, v: Any, handler) -> "BasicCvTermModel":
        item: BasicCvTermModel = handler(v)
        if not item.id_:
            item.id_ = item.get_unique_id(
                prefix="cv", namespace=NAMESPACE_VALUE, type_=item.type_
            )
        if not item.label:
            item.label = item.get_label()
        return item

    def get_unique_id(self, namespace: str, prefix: str, type_: str):
        if not type_:
            raise ValueError("type is not defined to create unique id")
        identifier_name = generate_unique_id(source=self, prefix=prefix, type_=type_)
        identifier = str(uuid.uuid5(namespace, name=identifier_name))
        return f"{prefix}--{type_}--{identifier}"

    def get_label(self):
        return self.name or self.id_ or ""

    def __hash__(self) -> int:
        return hash(self.id_)


class BasicCvTermValueModel(CvTermValue, IdentifiableMhdModel):
    id_: Annotated[
        None | CvTermValueObjectId,
        Field(
            ...,
            alias="id",
            description="The id property uniquely identifies the object.",
        ),
    ] = None
    label: Annotated[None | str, Field(exclude=True)] = None
    type_: Annotated[MhdObjectType, Field(alias="type")] = "cv-term-value"

    @model_validator(mode="wrap")
    @classmethod
    def validate_model(cls, v: Any, handler) -> "BasicCvTermValueModel":
        item: BasicCvTermValueModel = handler(v)
        if not item.id_:
            item.id_ = item.get_unique_id(
                prefix="cv-value", namespace=NAMESPACE_VALUE, type_=item.type_
            )
        if not item.label:
            item.label = item.get_label()
        return item

    def get_unique_id(self, namespace: str, prefix: str, type_: str):
        if not type_:
            raise ValueError("type is not defined to create unique id")
        identifier_name = generate_unique_id(source=self, prefix=prefix, type_=type_)
        identifier = str(uuid.uuid5(namespace, name=identifier_name))
        return f"{prefix}--{type_}--{identifier}"

    def get_label(self):
        return self.value or self.name or self.id_ or ""

    def __hash__(self) -> int:
        return hash(self.id_)


class BaseMhdRelationship(BaseMhdModel):
    model_config = ConfigDict(
        json_schema_extra={
            "unique_value_contribution": [
                (
                    "source_ref",
                    "relationship_name",
                    "target_ref",
                    "source_role",
                    "target_role",
                ),
                ("repository_identifier",),
            ]
        }
    )
    id_: Annotated[None | MhdRelationshipObjectId, Field(alias="id")] = None
    source_ref: MhdObjectId | CvTermObjectId | CvTermValueObjectId
    relationship_name: str
    target_ref: MhdObjectId | CvTermObjectId | CvTermValueObjectId
    source_role: None | str = None
    target_role: None | str = None

    @model_validator(mode="wrap")
    @classmethod
    def validate_model(cls, v: Any, handler) -> "BaseMhdRelationship":
        item: BaseMhdRelationship = handler(v)
        if not item.id_:
            item.id_ = item.get_unique_id(
                prefix="rel", namespace=NAMESPACE_VALUE, type_=item.type_
            )
        return item

    def get_unique_id(self, namespace: str, prefix: str, type_: str):
        if not type_:
            raise ValueError("type is not defined to create unique id")
        identifier_name = generate_unique_id(source=self, prefix=prefix, type_=type_)
        identifier = str(uuid.uuid5(namespace, name=identifier_name))
        return f"{prefix}--{type_}--{identifier}"

    def get_label(self):
        return self.relationship_name
