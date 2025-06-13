from mhd_model.shared.model import CvTerm
from mhd_model.shared.validation.definitions import ProfileValidationGroup
from mhd_model.shared.validation.registry import ProfileValidation


class CheckCvTermKeyValue(ProfileValidationGroup):
    name: str = "check-cv-term-key-value"
    cv_term_key: CvTerm
    min_value_count: int = 0


class CheckCvTermKeyValues(ProfileValidation):
    name: str = "check-cv-term-key-values"
    required_items: None | list[CheckCvTermKeyValue] = None
    optional_items: None | list[CheckCvTermKeyValue] = None
    input_type: str = "list"


class CheckChildCvTermKeyValues(ProfileValidation):
    name: str = "check-conditional-cv-term-key-values"

    conditional_field_name: str
    conditional_cv_term: CvTerm
    key_values_field_name: str
    key_values_control: CheckCvTermKeyValues
