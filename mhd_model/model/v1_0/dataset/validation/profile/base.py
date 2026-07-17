from typing import Annotated, Any

from pydantic import Field, model_validator

from mhd_model.shared.model import CvTerm, MhdConfigModel


class ValidationId(MhdConfigModel):
    identifier: Annotated[None | str, Field(description="Validation id")] = None
    description: Annotated[None | str, Field(description="Validation description")] = (
        None
    )


class FilterCondition(ValidationId):
    name: Annotated[str, Field()]
    relationship_name: Annotated[str, Field()]
    start_node_type: Annotated[None | str | list[str], Field()] = None
    expression: Annotated[None | str, Field()] = None
    expression_value: Annotated[None | str | CvTerm, Field()] = None


class EmbeddedRefValidation(ValidationId):
    node_type: Annotated[None | str, Field()] = None
    node_property_name: Annotated[None | str, Field()] = None
    required: Annotated[None | bool, Field()] = None
    target_ref_types: Annotated[list[str], Field()]
    min: Annotated[None | int, Field()] = None
    max: Annotated[None | int, Field()] = None

    def __str__(self) -> str:
        targets = (
            "Target node type: <code>**"
            + ", ".join(self.target_ref_types)
            + "**</code>"
            if self.target_ref_types
            else ""
        )
        min_length = None
        max_length = None
        if self.min:
            min_length = f"Minimum length: **{self.min}**"

        if self.max:
            max_length = f"Maximum length: **{self.max}**"
        return "\n".join([x for x in [targets, min_length, max_length] if x])


class RelationshipValidation(ValidationId):
    description: Annotated[None | str, Field()] = None
    source: Annotated[None | str, Field()]
    source_property_name: Annotated[None | str, Field()] = None
    relationship_name: Annotated[str, Field()]
    reverse_relationship_name: Annotated[None | str, Field()]
    target: Annotated[None | str, Field()]
    min: Annotated[int, Field()]
    max: Annotated[None | int, Field()] = None
    min_for_each_source: Annotated[None | int, Field()] = None
    max_for_each_source: Annotated[None | int, Field()] = None
    condition: Annotated[None | list[FilterCondition], Field()] = None

    @model_validator(mode="wrap")
    @classmethod
    def validate_model(cls, v: Any, handler: callable) -> "RelationshipValidation":
        item: RelationshipValidation = handler(v)
        if item.source is not None:
            item.source = item.source.lower().replace(" ", "-")
        if item.target is not None:
            item.target = item.target.lower().replace(" ", "-")
        item.relationship_name = item.relationship_name.lower().replace(" ", "-")
        return item
