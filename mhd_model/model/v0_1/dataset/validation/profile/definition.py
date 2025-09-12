from typing import Annotated, Any, Literal

from pydantic import AnyUrl, Field, model_validator

from mhd_model.model.v0_1.dataset.validation.profile.base import (
    EmbeddedRefValidation,
    RelationshipValidation,
)
from mhd_model.shared.model import CvTerm, MhdConfigModel
from mhd_model.shared.validation.definitions import (
    AllowAnyCvTerm,
    AllowedChildrenCvTerms,
    AllowedCvList,
    AllowedCvTerms,
)


class FilterCondition(MhdConfigModel):
    name: Annotated[str, Field()]
    relationship_name: Annotated[str, Field()]
    start_node_type: Annotated[None | str, Field()]
    expression: Annotated[None | str, Field()] = None
    expression_value: Annotated[None | str | CvTerm, Field()] = None


NodePropertyType = Literal["int", "str", "float", "CvTerm", "CvTermValue"]


class PropertyConstraint(MhdConfigModel):
    min_length: None | int = None
    max_length: None | int = None
    null_allowed: None | bool = None
    required: None | bool = None
    pattern: None | str = None
    allowed_types: None | NodePropertyType | list[NodePropertyType] = None

    def __str__(self) -> str:
        min = "Min Length: " + str(self.min_length) if self.min_length else ""
        max = "Max Length: " + str(self.max_length) if self.max_length else ""
        required = "Required" if self.required else ""
        return ", ".join(x for x in [min, max, required] if x)


class CvTermValidation(MhdConfigModel):
    min_count: Annotated[int, Field()] = 0
    node_type: Annotated[str, Field()]
    node_property_name: Annotated[None | str, Field()] = None
    validation: Annotated[
        AllowedCvTerms | AllowedChildrenCvTerms | AllowAnyCvTerm | AllowedCvList,
        Field(),
    ]
    condition: Annotated[None | list[FilterCondition], Field()] = None


class NodePropertyValidation(MhdConfigModel):
    node_type: Annotated[str, Field()]
    node_property_name: Annotated[None | str, Field()] = None
    contraints: Annotated[PropertyConstraint, Field()]


class NodeValidation(MhdConfigModel):
    node_type: Annotated[str, Field()]
    min: Annotated[int, Field()]
    max: Annotated[None | int, Field()] = None
    validations: Annotated[
        None | list[CvTermValidation | EmbeddedRefValidation | NodePropertyValidation],
        Field(),
    ] = None

    relationships: Annotated[None | list[RelationshipValidation], Field()] = None

    @model_validator(mode="wrap")
    @classmethod
    def validate_model(cls, v: Any, handler: callable) -> "NodeValidation":
        item: NodeValidation = handler(v)

        item.node_type = item.node_type.lower().replace(" ", "-")
        return item


class CvNodeValidation(NodeValidation):
    has_value: Annotated[bool, Field()] = False
    value_required: Annotated[bool, Field()] = False


class MhDatasetValidation(MhdConfigModel):
    mhd_nodes: Annotated[list[NodeValidation], Field()] = []
    cv_nodes: Annotated[list[CvNodeValidation], Field()] = []
    schema: Annotated[AnyUrl, Field()]
