import abc
import datetime
import decimal
import uuid
from typing import Annotated

from pydantic import AnyUrl, BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_pascal

NAMESPACE_VALUE = uuid.UUID("efb4f8e4-d08b-4979-916e-600c4985e7f2")
object_type_value = r"[a-z][-_a-z0-9]*[a-z0-9]"
uuid_value = r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"
base_suffix = rf"{object_type_value}:{uuid_value}$"
OBJECT_UUID_PATTERN = rf"^domain:{base_suffix}"
CV_TERM_UUID_PATTERN = rf"^cv:{base_suffix}"
CV_TERM_VALUE_UUID_PATTERN = rf"^cv-value:{base_suffix}"
DATASET_UUID_PATTERN = rf"^dataset:{base_suffix}"
REFERENCE_UUID_PATTERN = rf"^reference:{base_suffix}"
RELATIONSHIP_UUID_PATTERN = rf"^relationship:{base_suffix}"
OBJECT_TYPE_PATTERN = rf"^{object_type_value}$"


MhdObjectType = Annotated[str, Field(..., pattern=OBJECT_TYPE_PATTERN)]

MhdObjectId = Annotated[str, Field(pattern=OBJECT_UUID_PATTERN)]
CvTermObjectId = Annotated[str, Field(pattern=CV_TERM_UUID_PATTERN)]
CvTermValueObjectId = Annotated[str, Field(pattern=CV_TERM_VALUE_UUID_PATTERN)]
MhdRelationshipObjectId = Annotated[str, Field(pattern=RELATIONSHIP_UUID_PATTERN)]
MhdDatasetId = Annotated[str, Field(pattern=DATASET_UUID_PATTERN)]
MhdReferencedObjectId = Annotated[str, Field(pattern=REFERENCE_UUID_PATTERN)]

MhdSupportedPrimitiveType = Annotated[
    str | int | float | datetime.datetime | bool,
    AnyUrl,
    bool,
    Field(description="Supported types"),
]


AnyMhdNodeId = Annotated[
    MhdObjectId
    | CvTermObjectId
    | CvTermValueObjectId
    | MhdDatasetId
    | MhdReferencedObjectId,
    Field(description="Node Id"),
]

AnyMhdId = Annotated[
    MhdObjectId
    | CvTermObjectId
    | CvTermValueObjectId
    | MhdDatasetId
    | MhdReferencedObjectId
    | MhdRelationshipObjectId,
    Field(description="Node Id"),
]


class MhdConfigModel(BaseModel, abc.ABC):
    """Base Mhd pydantic model class and create unique id from model property"""

    model_config = ConfigDict(
        populate_by_name=True,
        json_schema_serialization_defaults_required=True,
        field_title_generator=lambda field_name, field_info: to_pascal(
            field_name.replace("_", " ").strip()
        ),
    )


class BaseValueModel(MhdConfigModel, abc.ABC):
    @abc.abstractmethod
    def get_as_string(self) -> str: ...

    def __str__(self) -> str:
        return self.get_as_string()

    def __hash__(self) -> int:
        return hash(self.get_as_string())

    def __repr__(self) -> str:
        return hash(self.get_as_string())


class CvTerm(BaseValueModel):
    source: Annotated[
        str,
        Field(description="Ontology source name."),
    ] = ""
    accession: Annotated[
        str,
        Field(description="Accession number of CV term in compact URI format."),
    ] = ""
    name: Annotated[
        str,
        Field(description="Label of CV term."),
    ] = ""

    def __lt__(self, other: "CvTerm") -> bool:
        if isinstance(other, CvTerm):
            return self.get_as_string() < other.get_as_string()
        return NotImplemented

    def get_as_string(self):
        return f"[{self.source or ''}, {self.accession or ''}, {self.name or ''}]"


class BaseParentCvTerm(BaseValueModel):
    cv_term: CvTerm
    allow_only_leaf: bool = False
    allow_parent: None | bool = False
    excluded_cv_terms: None | list[str] = None


class UnitCvTerm(CvTerm): ...


class BasicValueModel(BaseValueModel):
    value: Annotated[
        None | MhdSupportedPrimitiveType,
        Field(description="Value"),
    ] = None
    unit: Annotated[
        None | UnitCvTerm,
        Field(description="unit of the value."),
    ] = None

    def get_as_string(self):
        if self.unit:
            return f"{self.value} {self.unit.get_as_string()}"
        return str(self.value) or ""


class CvTermValue(CvTerm, BasicValueModel):
    value: Annotated[
        None | str | int | float | decimal.Decimal | datetime.datetime,
        Field(description="Value of CV term."),
    ] = None
    unit: Annotated[
        None | UnitCvTerm,
        Field(description="Unit CV term if value has a unit."),
    ] = None

    def get_as_string(self) -> str:
        unit_key = self.unit.get_as_string() if self.unit else ""
        value_key = str(self.value) or ""

        return f"[{self.source or ''}, {self.accession or ''}, {self.name or ''}, {value_key or ''}, {unit_key or ''}]"


class CvTermKeyValue(BaseValueModel):
    key: Annotated[CvTerm, Field(description="key CV term of values.")]
    values: Annotated[
        None
        | list[
            None | MhdSupportedPrimitiveType | BasicValueModel | CvTerm | CvTermValue
        ],
        Field(),
    ] = None

    def get_as_string(self) -> str:
        key = self.key.get_as_string() if self.key else ""
        values = ",".join(
            [
                x.get_as_string() if isinstance(x, BaseValueModel) else str(x)
                for x in self.values or []
            ]
        )
        return f"{key or ''}: {values or ''}"


class CvDefinition(BaseValueModel):
    label: None | str = None
    name: None | str = None
    uri: None | str = None
    prefix: None | str = None
    version: None | str = None
    alternative_labels: Annotated[None | list[str], Field(exclude=True)] = None
    alternative_prefixes: Annotated[None | list[str], Field(exclude=True)] = None

    def get_as_string(self) -> str:
        return f"[{self.label or ''}, {self.name or ''}, {self.uri or ''}, {self.version or ''}]"


class Revision(BaseValueModel):
    revision: Annotated[None | int, Field()] = None
    revision_datetime: None | datetime.datetime = None
    comment: None | str = None

    def get_as_string(self) -> str:
        return f"[{self.revision or ''}, {self.revision_datetime or ''}, {self.comment or ''}]"


class KeyValue(MhdConfigModel):
    key: None | AnyMhdId | str | CvTerm = None
    value: (
        None
        | AnyMhdNodeId
        | MhdSupportedPrimitiveType
        | CvTerm
        | CvTermValue
        | BasicValueModel
    ) = None

    def get_as_string(self) -> str:
        key = (
            self.key.get_as_string()
            if isinstance(self.key, BaseValueModel)
            else str(self.key)
        )
        value = (
            self.value.get_as_string()
            if isinstance(self.value, BaseValueModel)
            else str(self.value)
        )
        return f"{key}: {value}"
