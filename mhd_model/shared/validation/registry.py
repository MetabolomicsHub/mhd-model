from typing import Literal

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel, to_pascal


class ValidatorBaseModel(BaseModel):
    """Base model class to convert python attributes to camel case"""

    model_config = ConfigDict(
        populate_by_name=True,
        JSON_schema_serialization_defaults_required=True,
        field_title_generator=lambda field_name, field_info: to_pascal(
            field_name.replace("_", " ").strip()
        ),
        alias_generator=to_camel,
    )


class ProfileValidation(ValidatorBaseModel):
    name: str
    negate: bool = False
    allow_null_value: bool = False
    list_join_operator: Literal["any", "all", "minimum"] = "all"
    minimum: None | int = None
    input_type: Literal["list-or-item", "item", "list"] = "list-or-item"


def register_validator_class(
    validator_name: str, model_class: type[ProfileValidation]
) -> None:
    VALIDATORS[validator_name] = model_class


def unregister_validator_class(validator_name: str) -> None:
    validator = VALIDATORS.get(validator_name)
    if validator:
        del VALIDATORS[validator_name]


VALIDATORS: dict[str, type[ProfileValidation]] = {}
