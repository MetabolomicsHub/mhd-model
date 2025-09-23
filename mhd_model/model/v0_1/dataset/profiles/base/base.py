import datetime
import uuid
from typing import Any

from pydantic import AnyUrl, Field, field_validator, model_validator
from typing_extensions import Annotated

from mhd_model.shared.model import (
    CvTerm,
    CvTermValue,
    MhdConfigModel,
    QuantitativeValue,
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
setattr(MhdObjectType, "__name__", "MhdObjectType")

# MhdObjectType = Annotated[MhdObjectType, Field()]
MhdObjectId = Annotated[str, Field(pattern=OBJECT_UUID_PATTERN)]
setattr(MhdObjectId, "__name__", "MhdObjectId")
CvTermObjectId = Annotated[str, Field(pattern=CV_TERM_UUID_PATTERN)]
setattr(CvTermObjectId, "__name__", "CvTermObjectId")
CvTermValueObjectId = Annotated[str, Field(pattern=CV_TERM_VALUE_UUID_PATTERN)]
setattr(CvTermValueObjectId, "__name__", "CvTermValueObjectId")
MhdRelationshipObjectId = Annotated[str, Field(pattern=RELATIONSHIP_UUID_PATTERN)]
setattr(MhdRelationshipObjectId, "__name__", "MhdRelationshipObjectId")


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


# class CvTermKeyValue(MhdConfigModel):
#     key: CvTerm
#     value: str | datetime.datetime | bool | CvTerm | CvTermValue | QuantitativeValue


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


class BaseMhdModel(IdentifiableMhdModel):
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

        if item.type_ and not item.id_:
            item.id_ = f"mhd--{item.type_}--{uuid.uuid4()}"
        return item

    def get_unique_id(self):
        return self.id_

    def __hash__(self) -> int:
        return hash(self.get_unique_id())


class BaseLabeledMhdModel(BaseMhdModel):
    label: Annotated[None | str, Field(exclude=True)] = None

    @model_validator(mode="wrap")
    @classmethod
    def validate_model(cls, v: Any, handler) -> "BaseLabeledMhdModel":
        item: BaseLabeledMhdModel = handler(v)

        if item.type_ and not item.id_:
            item.id_ = f"mhd--{item.type_}--{uuid.uuid4()}"
        if not item.label:
            item.label = item.get_label()
        return item

    def get_label(self) -> str:
        return self.id_ or ""


class Definition(BaseLabeledMhdModel):
    name: Annotated[None | str, Field()] = None
    definition_type: Annotated[None | CvTerm, Field()] = None

    @model_validator(mode="wrap")
    @classmethod
    def validate_model(cls, v: Any, handler) -> "Definition":
        item: Definition = handler(v)
        if item.type_ and not item.id_:
            str_repr = item.get_unique_id()
            identifier_name = f"{item.type_}--{str_repr}"
            identifier = str(uuid.uuid5(NAMESPACE_VALUE, name=identifier_name))
            item.id_ = f"{item.type_}--{identifier}"
        if not item.label:
            item.label = item.get_label()
        return item

    def get_unique_id(self):
        return f"{self.name or ''},{self.definition_type.get_unique_id() if self.definition_type else ''}"

    def __hash__(self) -> int:
        return hash(self.get_unique_id())

    def get_label(self):
        return self.name or ""


class DefinitionValue(KeyValue): ...


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
        if item.type_ and not item.id_:
            str_repr = item.get_unique_id()
            identifier_name = f"{item.type_}--{str_repr}"
            identifier = str(uuid.uuid5(NAMESPACE_VALUE, name=identifier_name))
            item.id_ = f"cv--{item.type_}--{identifier}"
        if not item.label:
            item.label = item.get_label()
        return item

    def get_label(self):
        return self.name or self.id_ or ""

    def __hash__(self) -> int:
        return hash(self.get_unique_id())


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
    type_: Annotated[MhdObjectType, Field(frozen=False, alias="type")] = "cv-term-value"

    @model_validator(mode="wrap")
    @classmethod
    def validate_model(cls, v: Any, handler) -> "BasicCvTermValueModel":
        item: BasicCvTermValueModel = handler(v)
        if item.type_ and not item.id_:
            str_repr = item.get_unique_id()
            identifier_name = f"{item.type_}--{str_repr}"
            identifier = str(uuid.uuid5(NAMESPACE_VALUE, name=identifier_name))
            item.id_ = f"cv-value--{item.type_}--{identifier}"
        if not item.label:
            item.label = item.get_label()
        return item

    def get_label(self):
        return self.value or self.name or self.id_ or ""

    def __hash__(self) -> int:
        return hash(self.get_unique_id())


class BaseMhdRelationship(BaseMhdModel):
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
        if item.type_ and not item.id_:
            str_repr = item.get_unique_id()
            identifier_name = f"{item.type_}--{str_repr}"
            identifier = str(uuid.uuid5(NAMESPACE_VALUE, name=identifier_name))
            item.id_ = f"rel--{item.type_}--{identifier}"

        return item

    def get_unique_id(self):
        return f"{self.source_ref or ''},{self.relationship_name or ''},{self.target_ref or ''}"

    def get_label(self):
        return self.relationship_name
