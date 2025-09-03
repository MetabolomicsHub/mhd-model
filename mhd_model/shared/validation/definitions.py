from typing import Annotated, Any, Literal

from pydantic import Field, ValidationError, field_validator

from mhd_model.shared.model import CvTerm
from mhd_model.shared.validation.registry import (
    VALIDATORS,
    ProfileValidation,
    ValidatorBaseModel,
)


class CvTermPlaceholder(ValidatorBaseModel):
    source: str = ""
    accession: str = ""

    def __hash__(self) -> int:
        return f"[{self.source}, {self.accession}]"


class ProfileCvTermValidation(ProfileValidation):
    allowed_missing_cv_terms: None | list[CvTerm] = None
    allowed_placeholder_values: None | list[CvTermPlaceholder] = None
    allowed_other_sources: None | list[str] = None

    def __str__(self) -> str:
        result = [
            (
                "Allowed Missing CV Terms: "
                + ", ".join([str(x) for x in self.allowed_missing_cv_terms])
                if self.allowed_missing_cv_terms
                else None
            ),
            (
                "Allowed Placeholder Values: "
                + ", ".join([str(x) for x in self.allowed_placeholder_values])
                if self.allowed_placeholder_values
                else None
            ),
            (
                "Allowed Other Sources: "
                + ", ".join([x for x in self.allowed_other_sources])
                if self.allowed_other_sources
                else None
            ),
        ]
        filtered_result = [x for x in result if x]
        return "Exceptions:\n" + "\n".join(filtered_result) if filtered_result else ""


class AllowedCvList(ProfileCvTermValidation):
    name: str = "allowed-cv-list"
    source_names: list[str]

    def __str__(self) -> str:
        sources = (
            "Ontology Sources:" + ", ".join(self.source_names)
            if self.source_names
            else ""
        )
        parent_str = super().__str__()

        if parent_str:
            return sources + f"\n{parent_str}"

        return sources


class ParentCvTerm(ValidatorBaseModel):
    cv_term: CvTerm
    allow_only_leaf: bool = False
    allow_parent: None | bool = False
    excluded_cv_terms: None | list[CvTerm] = None
    index_cv_terms: None | bool = True

    def __str__(self) -> str:
        parent = str(self.cv_term)
        excludes = (
            "Excluded CV Terms: " + ", ".join([str(x) for x in self.excluded_cv_terms])
            if self.excluded_cv_terms
            else ""
        )
        allow_parent = "Allow parent CV Term: " + ("Yes" if self.allow_parent else "No")
        allow_only_leaf_terms = "Allow only leaf CV Terms: " + (
            "Yes" if self.allow_only_leaf else "No"
        )

        result = [
            x for x in [parent, allow_parent, allow_only_leaf_terms, excludes] if x
        ]
        return "\n".join(result)


class AllowedChildrenCvTerms(ProfileCvTermValidation):
    name: str = "allowed-children-cv-terms"
    parent_cv_terms: list[ParentCvTerm]

    def __str__(self) -> str:
        sources = (
            "Allowed Parent CV Terms: "
            + ", ".join([str(x) for x in self.parent_cv_terms])
            if self.parent_cv_terms
            else ""
        )
        parent_str = super().__str__()

        if parent_str:
            return sources + f"\n{parent_str}"

        return sources


class AllowedCvTerms(ProfileCvTermValidation):
    name: Annotated[str, Field()] = "allowed-cv-terms"
    cv_terms: None | list[CvTerm]

    def __str__(self) -> str:
        sources = (
            "Allowed CV Terms: " + ", ".join([str(x) for x in self.cv_terms])
            if self.cv_terms
            else ""
        )
        parent_str = super().__str__()

        if parent_str:
            return sources + f"\n{parent_str}"

        return sources


class AccessibleURI(ProfileValidation):
    name: str = "accessible-uri"
    max_retries: int = 1
    retry_period_in_seconds: int = 0


class AccessibleCompactURI(ProfileValidation):
    name: str = "accessible-compact-uri"
    default_prefix: None | str = None
    follow_redirects: bool = False


class AllowAnyCvTerm(ProfileCvTermValidation):
    name: str = "allow-any-cv-term"

    def __str__(self) -> str:
        sources = "Allow any valid CV Term"
        parent_str = super().__str__()

        if parent_str:
            return sources + f"\n{parent_str}"

        return sources


class ProfileValidationGroup(ProfileValidation):
    name: str = "validation-group"
    controls: list[ProfileValidation]
    join_operator: Literal["and", "or"] = "and"

    @field_validator("controls", mode="before")
    @classmethod
    def controls_validator(cls, value: Any) -> None:
        if not value:
            return []
        return_value = []
        if isinstance(value, list):
            for item in value:
                if isinstance(item, ProfileValidation):
                    return_value.append(item)
                elif isinstance(item, dict) and "name" in item:
                    validation_name = item["name"]
                    validator = VALIDATORS.get(validation_name)
                    if validator:
                        return_value.append(validator.model_validate(item))
                    else:
                        raise ValidationError(
                            f"invalid validator name {validation_name}"
                        )

        else:
            raise ValidationError(f"invalid value {value}")
        return return_value
