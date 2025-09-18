from __future__ import annotations

import logging
from ftplib import FTP
from typing import Any

import jsonschema
import reachable
from jsonschema import protocols, validators
from pydantic import ValidationError

from mhd_model.model.definitions import (
    SUPPORTED_SCHEMA_MAP,
)
from mhd_model.model.v0_1.announcement.validation.definitions import (
    CheckChildCvTermKeyValues,
    CheckCvTermKeyValue,
    CheckCvTermKeyValues,
    ProfileValidation,
)
from mhd_model.schema_utils import load_mhd_json_schema
from mhd_model.shared.model import CvTerm, CvTermKeyValue
from mhd_model.shared.validation.cv_term_helper import (
    CvTermHelper,
)
from mhd_model.shared.validation.validators import (
    AccessibleCompactURIValidator,
    AccessibleURIValidator,
    AllowAnyCvTermValidator,
    AllowedChildrenCvTermsValidator,
    AllowedCvListValidator,
    AllowedCvTermValidator,
    BaseProfileValidator,
    ProfileValidationGroupValidator,
    ValidationResult,
)

logger = logging.getLogger(__name__)


class CheckCvTermKeyValueValidator(ProfileValidationGroupValidator):
    def __init__(
        self,
        cv_helper: CvTermHelper,
        validators: dict[str, BaseProfileValidator],
        ftp_client_pool: dict[str, FTP],
        url_client: reachable.client.Client,
    ) -> None:
        super().__init__(cv_helper, validators, ftp_client_pool, url_client)

    def get_profile_validation_class(self) -> type[CheckCvTermKeyValue]:
        return CheckCvTermKeyValue

    def evaluate(
        self,
        value: Any,
        profile_validation: ProfileValidation,
        sub_path: None | list[int | str] = None,
    ) -> ValidationResult:
        if not isinstance(profile_validation, CheckCvTermKeyValue):
            return ValidationResult(
                sub_path=sub_path,
                name="",
                valid=False,
                message=f"Invalid validator {str(profile_validation)}",
                data=value,
            )

        validator: CheckCvTermKeyValue = profile_validation
        if not isinstance(value, list):
            return ValidationResult(
                sub_path=sub_path,
                name=validator.name,
                valid=False,
                message="Input must be list",
                data=value,
            )
        item: CvTermKeyValue = CvTermKeyValue.model_validate(value)
        if item.key.accession != validator.cv_term_key.accession:
            return ValidationResult(
                sub_path=sub_path,
                name=validator.name,
                valid=False,
                message=f"Not applicable to evaluate key {item.key.accession}",
                data=value,
            )
        return super().evaluate(
            value=item.values,
            profile_validation=profile_validation,
            sub_path=sub_path,
        )


class CheckCvChildTermKeyValuesValidator(BaseProfileValidator):
    def __init__(
        self,
        cv_helper: CvTermHelper,
        ftp_client_pool: dict[str, FTP],
        url_client: reachable.client.Client,
        validators: dict[str, BaseProfileValidator],
    ) -> None:
        super().__init__(cv_helper)
        self.ftp_client_pool = ftp_client_pool
        self.url_client = url_client
        self.validators = validators

    def get_profile_validation_class(self) -> type[CheckChildCvTermKeyValues]:
        return CheckChildCvTermKeyValues

    def evaluate(
        self,
        value: Any,
        profile_validation: ProfileValidation,
        sub_path: None | list[int | str] = None,
    ) -> ValidationResult:
        if not isinstance(profile_validation, CheckChildCvTermKeyValues):
            return ValidationResult(
                sub_path=sub_path,
                name="",
                valid=False,
                message=f"invalid validator {str(profile_validation)}",
                data=value,
            )

        validator: CheckChildCvTermKeyValues = profile_validation

        if (
            validator.conditional_field_name in value
            and validator.key_values_field_name in value
        ):
            # sub_path_copy = sub_path.copy()

            errors = []
            # for item in value:
            key = CvTerm.model_validate(value.get(validator.conditional_field_name))
            if str(key) == str(validator.conditional_cv_term):
                # sub_path_copy.append(validator.key_values_field_name)
                values = value.get(validator.key_values_field_name)
                key_value_validator = self.validators.get("check-cv-term-key-values")
                error = key_value_validator.validate(
                    values,
                    profile_validation.key_values_control,
                    sub_path=[validator.key_values_field_name],
                )
                if error:
                    error.message = f"{key.accession}, {key.name}: {error.message}"
                    errors.append(error)
            else:
                # sub_path_copy.append(validator.conditional_field_name)
                return ValidationResult(
                    sub_path=sub_path,
                    name=validator.name,
                    valid=True,
                    message=f"Key does not match: {key.name}, expected value {validator.conditional_cv_term.name}",
                    data=value,
                )
            if errors:
                return ValidationResult(
                    sub_path=sub_path,
                    name=validator.name,
                    valid=False,
                    message="Invalid controlled terms.",
                    data=value,
                    context=errors,
                )
            return ValidationResult(
                sub_path=sub_path,
                name=validator.name,
                valid=True,
                message="Valid controlled terms.",
                data=value,
            )


class CheckCvTermKeyValuesValidator(BaseProfileValidator):
    def __init__(
        self,
        cv_helper: CvTermHelper,
        ftp_client_pool: dict[str, FTP],
        url_client: reachable.client.Client,
        validators: dict[str, BaseProfileValidator],
    ) -> None:
        super().__init__(cv_helper)
        self.ftp_client_pool = ftp_client_pool
        self.url_client = url_client
        self.validators = validators

    def get_profile_validation_class(self) -> type[CheckCvTermKeyValues]:
        return CheckCvTermKeyValues

    def evaluate(
        self,
        value: Any,
        profile_validation: ProfileValidation,
        sub_path: None | list[int | str] = None,
    ) -> ValidationResult:
        if not isinstance(profile_validation, CheckCvTermKeyValues):
            return ValidationResult(
                sub_path=sub_path,
                name="",
                valid=False,
                message=f"invalid validator {str(profile_validation)}",
                data=value,
            )

        validator: CheckCvTermKeyValues = profile_validation
        if not isinstance(value, list):
            return ValidationResult(
                sub_path=sub_path,
                name=validator.name,
                valid=False,
                message="Input must be list",
                data=value,
            )
        items: list[CvTermKeyValue] = [CvTermKeyValue.model_validate(x) for x in value]

        errors: list[ValidationResult | ValidationError] = []
        for control_items, required in [
            (validator.required_items, True),
            (validator.optional_items, False),
        ]:
            if not control_items:
                continue

            control_map = {str(x.cv_term_key): x for x in control_items}
            validated_keys = set()
            invalid_keys = set()
            for item_idx, item in enumerate(items):
                item_key = str(item.key)
                if item_key not in control_map:
                    continue
                # sub_path_copy = sub_path.copy()
                # sub_path_copy.append(item_idx)
                key_validator = control_map[item_key]
                for idx, item_value in enumerate(item.values):
                    # sub_item_path = sub_path_copy.copy()
                    # sub_item_path.extend(["values"])
                    valid, invalid_results = self.validate_key_values(
                        key_validator, item_value, [item_idx, "values", idx]
                    )
                    if valid:
                        validated_keys.add(item_key)
                    else:
                        invalid_keys.add(item_key)
                        errors.append(
                            ValidationResult(
                                sub_path=[item_idx, "values", idx],
                                name=validator.name,
                                valid=False,
                                message=f"Item at index {idx} is not valid.",
                                data=value,
                                context=invalid_results,
                            )
                        )
            if required and len(validated_keys) != len(control_items):
                undefined_keys = [
                    f"[{control_map[x].cv_term_key.accession}, {control_map[x].cv_term_key.name}]"
                    for x in control_map
                    if x not in validated_keys and x not in invalid_keys
                ]
                invalid_values = [
                    control_map[x].cv_term_key.name
                    for x in control_map
                    if x in invalid_keys
                ]

                messages = []
                if undefined_keys:
                    messages.append(f"Undefined key(s): {', '.join(undefined_keys)}")
                if invalid_values:
                    messages.append(
                        f"Invalid value(s) in keys: {', '.join(invalid_values)}"
                    )
                errors.append(
                    ValidationResult(
                        sub_path=sub_path,
                        name=validator.name,
                        valid=False,
                        message=". ".join(messages),
                        data=value,
                    )
                )

        if errors:
            return ValidationResult(
                sub_path=sub_path,
                name=validator.name,
                valid=False,
                message="Invalid controlled terms. "
                + ". ".join([x.message for x in errors]),
                data=value,
                context=errors,
            )
        return ValidationResult(
            sub_path=sub_path,
            name=validator.name,
            valid=True,
            message="Valid controlled terms.",
            data=value,
        )

    def validate_key_values(
        self,
        key_validator: CheckCvTermKeyValue,
        value,
        sub_path: None | list[int | str],
    ):
        invalid_results: list[ValidationResult | ValidationError] = []
        for control in key_validator.controls:
            # sub_path_copy = sub_path.copy()
            validation_error = self.validators[control.name].validate(
                value, control.model_dump(by_alias=True), sub_path
            )

            if validation_error:
                validation_error.path = sub_path
                invalid_results.append(validation_error)

        valid = False
        valid_controls = len(key_validator.controls) - len(invalid_results)

        if key_validator.join_operator == "or":
            if valid_controls > 0:
                valid = True
        else:
            if valid_controls == len(key_validator.controls):
                valid = True

        return valid, invalid_results


class ProfileValidator:
    def __init__(self) -> None:
        ftp_client_pool: dict[str, FTP] = {}
        url_client: reachable.client.Client = reachable.client.Client()
        self.cv_helper = CvTermHelper()

        self.validators: dict[str, BaseProfileValidator] = {
            "allowed-cv-terms": AllowedCvTermValidator(self.cv_helper),
            "allow-any-cv-term": AllowAnyCvTermValidator(self.cv_helper),
            "allowed-children-cv-terms": AllowedChildrenCvTermsValidator(
                self.cv_helper
            ),
            "allowed-cv-list": AllowedCvListValidator(self.cv_helper),
            "accessible-uri": AccessibleURIValidator(
                self.cv_helper, ftp_client_pool=ftp_client_pool, url_client=url_client
            ),
            "accessible-compact-uri": AccessibleCompactURIValidator(
                self.cv_helper, ftp_client_pool=ftp_client_pool, url_client=url_client
            ),
        }
        self.validators["validation-group"] = ProfileValidationGroupValidator(
            self.cv_helper,
            validators=self.validators,
            ftp_client_pool=ftp_client_pool,
            url_client=url_client,
        )
        self.validators["check-cv-term-key-value"] = CheckCvTermKeyValueValidator(
            self.cv_helper,
            validators=self.validators,
            ftp_client_pool=ftp_client_pool,
            url_client=url_client,
        )
        self.validators["check-cv-term-key-values"] = CheckCvTermKeyValuesValidator(
            self.cv_helper,
            validators=self.validators,
            ftp_client_pool=ftp_client_pool,
            url_client=url_client,
        )

        self.validators["check-conditional-cv-term-key-values"] = (
            CheckCvChildTermKeyValuesValidator(
                self.cv_helper,
                validators=self.validators,
                ftp_client_pool=ftp_client_pool,
                url_client=url_client,
            )
        )

    def validate_instance(
        self, validator: jsonschema.Validator, profile_validation, instance, schema
    ):
        """
        Custom validation logic for the 'profile_validation' keyword.
        """
        if isinstance(profile_validation, dict) and "name" in profile_validation:
            model = ProfileValidation.model_validate(profile_validation)

            if model.list_join_operator in ("any", "minimum") and model.minimum is None:
                model.minimum = 1
            validator_name = model.name
            if validator_name in self.validators:
                validator_instance = self.validators[validator_name]
                if model.input_type in ("list-or-item", "item") and isinstance(
                    instance, list
                ):
                    validation_errors = []
                    valid_count = 0
                    valid = False
                    for idx, x in enumerate(instance):
                        # va = validator.evolve(schema=schema["items"])
                        # y = [x for x in va.iter_errors(x)]
                        validation_error = validator_instance.validate(
                            x, profile_validation, [idx]
                        )
                        if not validation_error:
                            valid_count += 1
                        else:
                            validation_errors.append(validation_error)
                        if model.list_join_operator == "all":
                            if validation_error:
                                yield validation_error
                        elif model.list_join_operator in ("any", "minimum"):
                            if model.minimum <= valid_count:
                                valid = True
                                break

                    if model.list_join_operator in ("any", "minimum") and not valid:
                        yield jsonschema.ValidationError(
                            message=f"Number of valid list items: {valid_count}, expected {model.minimum}.",
                            validator=model.name,
                            context=(),
                            path=(),
                            instance=instance,
                        )

                else:
                    validation_error = validator_instance.validate(
                        value=instance,
                        profile_validation=profile_validation,
                        sub_path=[],
                    )
                    if validation_error:
                        yield validation_error
            else:
                yield jsonschema.ValidationError(message="Not valid validation name")
        else:
            yield jsonschema.ValidationError(message="Not valid")

    @staticmethod
    def new_instance(
        schema_uri: None | str, profile_uri: None | str
    ) -> protocols.Validator:
        profile_validator = ProfileValidator()
        validator = validators.extend(
            jsonschema.Draft202012Validator,
            validators={"profileValidation": profile_validator.validate_instance},
        )
        if not schema_uri:
            schema_uri = SUPPORTED_SCHEMA_MAP.schemas[
                SUPPORTED_SCHEMA_MAP.default_schema_uri
            ]
        if schema_uri in SUPPORTED_SCHEMA_MAP.schemas:
            schema = SUPPORTED_SCHEMA_MAP.schemas.get(schema_uri)
            if not profile_uri:
                profile_uri = schema.default_profile_uri

            if schema.supported_profiles.get(profile_uri):
                _, schema_file = load_mhd_json_schema(profile_uri)
                return validator(schema_file)
        return None
