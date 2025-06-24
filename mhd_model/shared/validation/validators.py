from __future__ import annotations

import abc
import logging
import pathlib
from ftplib import FTP
from typing import Any
from urllib.parse import urlparse

import bioregistry
import httpx
import jsonschema
import reachable
from pydantic import BaseModel, ValidationError

from mhd_model.shared.model import CvTerm, CvTermKeyValue, CvTermValue
from mhd_model.shared.validation.cv_term_helper import (
    CvTermHelper,
)
from mhd_model.shared.validation.definitions import (
    AccessibleCompactURI,
    AccessibleURI,
    AllowAnyCvTerm,
    AllowedChildrenCvTerms,
    AllowedCvList,
    AllowedCvTerms,
    CvTermPlaceholder,
    ProfileCvTermValidation,
    ProfileValidationGroup,
)
from mhd_model.shared.validation.registry import ProfileValidation

logger = logging.getLogger(__name__)


class ValidationResult(BaseModel):
    name: str
    root: bool = False
    message: None | str
    valid: bool = False
    data: None | Any = None
    sub_path: None | list[int | str] = None
    error: None | Any = None
    context: None | Any = None
    parent: None | Any = None
    validator_value: None | Any = None


class BaseProfileValidator(abc.ABC):
    def __init__(self, cv_helper: CvTermHelper) -> None:
        self.cv_helper = cv_helper

    def is_accessible_url(self, url: str) -> bool:
        try:
            result = httpx.head(url, timeout=5)
            if result.status_code == 404:
                return False
            result.raise_for_status()
            return True
        except Exception as ex:
            logger.debug("Unaccessible URL: %s", str(ex))
            return False

    @abc.abstractmethod
    def get_profile_validation_class(self) -> type[ProfileValidation]:
        pass

    def validate(
        self,
        value: Any,
        profile_validation: dict[str, Any],
        sub_path: None | list[int | str] = None,
    ) -> tuple[bool, list[ValidationResult]]:
        if isinstance(profile_validation, dict):
            validation = self.get_profile_validation_class().model_validate(
                profile_validation
            )
        else:
            validation = profile_validation

        if not value:
            if validation.allow_null_value:
                return None

        if isinstance(validation, ProfileCvTermValidation):
            if isinstance(value, CvTermKeyValue) or (
                isinstance(value, dict) and value.get("key")
            ):
                data = value
                if isinstance(value, dict):
                    data = CvTermKeyValue.model_validate(value)
                if validation.allowed_placeholder_values:
                    if data.values and data.values[0].accession in {
                        x.accession for x in validation.allowed_placeholder_values
                    }:
                        return None
                if validation.allowed_missing_cv_terms:
                    if data.values and data.values[0] in {
                        x.accession for x in validation.allowed_missing_cv_terms
                    }:
                        return None

            if isinstance(value, CvTerm) or (
                isinstance(value, dict) and "source" in value and "accession" in value
            ):
                data = value
                if isinstance(value, dict):
                    data = CvTermPlaceholder.model_validate(value)

                if validation.allowed_placeholder_values:
                    if str(data) in {
                        str(x) for x in validation.allowed_placeholder_values
                    }:
                        return None
                if validation.allowed_missing_cv_terms:
                    if data.accession in {
                        x.accession for x in validation.allowed_missing_cv_terms
                    }:
                        return None
                if validation.allowed_other_sources:
                    if data.accession in {x for x in validation.allowed_other_sources}:
                        if not data.source:
                            source = data.accession.split(":")[0]
                            data.source = source
                        url = self.cv_helper.get_uri(cv_term=data)
                        acessible = self.is_accessible_url(url=url)
                        if acessible:
                            return None
                        error = jsonschema.ValidationError(
                            message=f"{data.accession} is not accessible",
                            validator=validation.name,
                            context=[],
                            path=(),
                            instance=data,
                        )

        validation_result = self.evaluate(value, validation, [])
        valid = validation_result is None or validation_result.valid

        if validation.negate:
            valid = not valid

        if not valid:
            # sub_path = sub_path if sub_path else []
            # new_subpath = validation_result.sub_path if validation_result.sub_path else []
            # if new_subpath:
            #     sub_path.extend(new_subpath)
            error = jsonschema.ValidationError(
                # message=self.create_message(validation_result),
                message=validation_result.message,
                validator=validation.name,
                context=[],
                path=(),
                instance=value,
            )
            self.update_error_context(error, validation_result)
            return error
        return None

    def update_error_context(
        self, error: jsonschema.ValidationError, result: ValidationResult
    ) -> None:
        context = []
        if result.context:
            for item in result.context:
                if isinstance(item, jsonschema.ValidationError):
                    context.append(item)
                elif isinstance(item, ValidationResult) and not item.valid:
                    cnxt_error = jsonschema.ValidationError(
                        # message=self.create_message(validation_result),
                        message=item.message,
                        validator=item.name,
                        context=item.context if item.context else [],
                        path=item.sub_path if item.sub_path else (),
                        instance=item.data,
                    )
                    self.update_error_context(cnxt_error, item)
                    context.append(cnxt_error)
        error.context = context

    @abc.abstractmethod
    def evaluate(
        self,
        value: Any,
        profile_validation: ProfileValidation,
        sub_path: None | list[int | str] = None,
    ) -> ValidationResult:
        pass

    def create_message(
        self, error: jsonschema.ValidationError | ValidationResult
    ) -> str:
        if not error:
            return "validation error"
        if isinstance(error, jsonschema.ValidationError):
            name = error.validator
            message = error.message
            jsonpath_str = self.json_path(error.absolute_path)
        else:
            name = error.name
            message = error.message
            jsonpath_str = ""
        if error.context and len(error.context) == 1:
            message = f"{message}"
        else:
            message = f"{name}: {message}"
        if error.context:
            sub_messages = []
            for x in error.context:
                sub_messages.append(self.create_message(x))
            if not jsonpath_str:
                return message + f" [{', '.join(sub_messages)}]"
            return message + f" [{jsonpath_str}: {', '.join(sub_messages)}]"
        return message

    def json_path(self, field_path: list[str | int]) -> str:
        return ".".join([x if isinstance(x, str) else f"[{x}]" for x in field_path])


class AllowedCvTermValidator(BaseProfileValidator):
    def __init__(self, cv_helper: CvTermHelper) -> None:
        super().__init__(cv_helper)

    def get_profile_validation_class(self) -> type[AllowedCvTerms]:
        return AllowedCvTerms

    def evaluate(
        self,
        value: Any,
        profile_validation: ProfileValidation,
        sub_path: None | list[int | str] = None,
    ) -> ValidationResult:
        try:
            val: CvTerm = CvTerm.model_validate(value)
        except ValidationError as ex:
            ex.errors()

        validator: AllowedCvTerms = profile_validation

        for term in validator.cv_terms:
            if (
                val.name == term.name
                and val.accession == term.accession
                and val.source == term.source
            ):
                message = None
                return ValidationResult(
                    sub_path=sub_path,
                    name=validator.name,
                    valid=True,
                    message=f"[{val.source}, {val.accession}, {val.name}] is an allowed CV term.",
                    data=value,
                )
        terms = ", ".join(
            [f"[{x.source}, {x.accession}, {x.name}]" for x in validator.cv_terms]
        )
        message = f"[{val.source}, {val.accession}, {val.name}] does not match any allowed CV term. Allowed CV terms: {terms}"

        return ValidationResult(
            sub_path=sub_path,
            name=validator.name,
            valid=False,
            message=message,
            data=value,
        )


class AllowAnyCvTermValidator(BaseProfileValidator):
    def __init__(self, cv_helper: CvTermHelper) -> None:
        super().__init__(cv_helper)

    def get_profile_validation_class(self) -> type[AllowAnyCvTerm]:
        return AllowAnyCvTerm

    def evaluate(
        self,
        value: Any,
        profile_validation: ProfileValidation,
        sub_path: None | list[int | str] = None,
    ) -> ValidationResult:
        validator: AllowAnyCvTerm = profile_validation
        data = CvTerm.model_validate(value)
        if isinstance(data, CvTerm):
            if ":" not in data.accession:
                return ValidationResult(
                    sub_path=sub_path,
                    name=validator.name,
                    message=f"{data.accession} is not valid CURIE value.",
                    data=value,
                )

            # prefix, identifier = tuple(data.accession.split(":"))

            result = self.cv_helper.get_uri(data)
            if not result:
                return ValidationResult(
                    sub_path=sub_path,
                    name=validator.name,
                    message=f"[{data.name}, {data.accession}, {data.name}] is not valid CV term",
                    data=value,
                )
        else:
            return ValidationResult(
                sub_path=sub_path,
                name=validator.name,
                message=f"{value} is not an valid CV term",
                data=value,
            )
        return ValidationResult(
            sub_path=sub_path,
            valid=True,
            name=validator.name,
            message=f"[{data.name}, {data.accession}, {data.name}] is valid CV term",
            data=value,
        )


class ProfileValidationGroupValidator(BaseProfileValidator):
    def __init__(
        self,
        cv_helper: CvTermHelper,
        validators: dict[str, BaseProfileValidator],
        ftp_client_pool: dict[str, FTP],
        url_client: reachable.client.Client,
    ) -> None:
        super().__init__(cv_helper)
        self.ftp_client_pool = ftp_client_pool
        self.url_client = url_client
        self.validators = validators

    def get_profile_validation_class(self) -> type[ProfileValidationGroup]:
        return ProfileValidationGroup

    def evaluate(
        self,
        value: Any,
        profile_validation: ProfileValidation,
        sub_path: None | list[int | str] = None,
    ) -> ValidationResult:
        validation_tests: list[ValidationResult | list[ValidationResult]] = []
        profile_validation_list: ProfileValidationGroup = profile_validation
        invalid_results = []

        if isinstance(value, list):
            list_invalid_results = []
            for control in profile_validation_list.controls:
                for idx, item in enumerate(value):
                    sub_path_copy = sub_path.copy()
                    sub_path_copy.append(idx)
                    validation_error = self.validators[control.name].validate(
                        item, control, [idx]
                    )
                    if validation_error:
                        list_invalid_results.extend(validation_error)
                if list_invalid_results:
                    validation_tests.append((control.name, list_invalid_results))
        else:
            for control in profile_validation_list.controls:
                sub_path_copy = sub_path.copy()
                validation_error = self.validators[control.name].validate(
                    value, control, []
                )

                if validation_error:
                    invalid_results.append((control.name, validation_error))

        valid = False
        valid_controls = len(profile_validation_list.controls) - len(invalid_results)

        if profile_validation_list.join_operator == "or":
            if valid_controls > 0:
                valid = True
        else:
            if valid_controls == len(profile_validation_list.controls):
                valid = True

        validation_results = [x[1] for x in invalid_results]

        if valid:
            return ValidationResult(
                sub_path=sub_path,
                name=profile_validation_list.name,
                valid=True,
                message=f"{value} is valid.",
                data=value,
                context=validation_results,
            )
        return ValidationResult(
            sub_path=sub_path,
            name=profile_validation_list.name,
            valid=False,
            message=f"{value} is not valid.",
            data=value,
            context=validation_results,
        )


class AllowedChildrenCvTermsValidator(BaseProfileValidator):
    def __init__(self, cv_helper: CvTermHelper) -> None:
        super().__init__(cv_helper)

    def get_profile_validation_class(self) -> type[AllowedChildrenCvTerms]:
        return AllowedChildrenCvTerms

    def evaluate(
        self,
        value: Any,
        profile_validation: ProfileValidation,
        sub_path: None | list[int | str] = None,
    ) -> ValidationResult:
        validator: AllowedChildrenCvTerms = profile_validation
        if not isinstance(profile_validation, AllowedChildrenCvTerms):
            ValidationResult(
                sub_path=sub_path,
                name=validator.name,
                valid=False,
                message="Invalid validator",
                data=value,
            )

        parents = ", ".join(
            [
                f"[{x.cv_term.source}, {x.cv_term.accession}, {x.cv_term.name}]"
                for x in validator.parent_cv_terms
            ]
        )
        cv_term = value
        if isinstance(cv_term, dict):
            cv_term: CvTerm = CvTerm.model_validate(value)
        if not isinstance(cv_term, CvTerm):
            return ValidationResult(
                sub_path=sub_path,
                name=validator.name,
                valid=False,
                message="input is not Cv term",
                data=value,
            )
        for parent in validator.parent_cv_terms:
            if parent.index_cv_terms:
                terms = self.cv_helper.get_children_of_cv_term(parent)
                if cv_term.accession in terms:
                    return ValidationResult(
                        sub_path=sub_path,
                        name=validator.name,
                        valid=True,
                        message=f"[{cv_term.source}, {cv_term.accession}, {cv_term.name}] is a child of allowed CV terms. ",
                        data=value,
                    )

            else:
                search_result, message = self.cv_helper.check_cv_term(
                    cv_term=cv_term, parent_cv_term=parent
                )
                if search_result:
                    return ValidationResult(
                        sub_path=sub_path,
                        name=validator.name,
                        valid=True,
                        message=f"[{cv_term.source}, {cv_term.accession}, {cv_term.name}] is a child of allowed CV terms. ",
                        data=value,
                    )
                return ValidationResult(
                    sub_path=sub_path,
                    name=validator.name,
                    valid=search_result,
                    message=message,
                    data=value,
                )

        return ValidationResult(
            sub_path=sub_path,
            name=validator.name,
            valid=False,
            message=f"[{cv_term.source}, {cv_term.accession}, {cv_term.name}] is not child of allowed CV terms. "
            f"Terms should be child of any {parents} CV terms",
            data=value,
        )


class AllowedCvListValidator(BaseProfileValidator):
    def __init__(self, cv_helper: CvTermHelper) -> None:
        super().__init__(cv_helper)

    def get_profile_validation_class(self) -> type[AllowedCvList]:
        return AllowedCvList

    def evaluate(
        self,
        value: Any,
        profile_validation: ProfileValidation,
        sub_path: None | list[int | str] = None,
    ) -> ValidationResult:
        if not isinstance(profile_validation, AllowedCvList):
            return ValidationResult(
                sub_path=sub_path,
                name="invalid validation ",
                valid=False,
                message="Invalid validator",
                data=value,
            )
        data = value
        if isinstance(value, dict):
            data = CvTerm.model_validate(value)
        validator: AllowedCvList = profile_validation

        if data.source in validator.source_names:
            check_valid, message = self.cv_helper.check_cv_term(data)
            if check_valid:
                return ValidationResult(
                    sub_path=sub_path,
                    name=validator.name,
                    valid=True,
                    message=f"[{data.source}, {data.accession}, {data.name}] is an allowed CV source.",
                    data=value,
                )
            return ValidationResult(
                sub_path=sub_path,
                name=validator.name,
                valid=check_valid,
                message=message,
                data=value,
            )
        else:
            labels = ", ".join(validator.source_names)
            message = (
                f"[{data.source}, {data.accession}, {data.name}] is not in any allowed CV source. "
                f"Define a CV term from the selected CV sources: {labels}"
            )
            return ValidationResult(
                sub_path=sub_path,
                name=validator.name,
                valid=False,
                message=message,
                data=value,
            )


class AccessibleURIValidator(BaseProfileValidator):
    def __init__(
        self,
        cv_helper: CvTermHelper,
        ftp_client_pool: dict[str, FTP],
        url_client: reachable.client.Client,
    ) -> None:
        super().__init__(cv_helper)
        self.ftp_client_pool = ftp_client_pool
        self.url_client = url_client
        self.cache: dict[None | str, ValidationResult] = {}

    def get_profile_validation_class(self) -> type[AccessibleURI]:
        return AccessibleURI

    def return_result(self, key: str, result: ValidationResult) -> ValidationResult:
        if key not in self.cache:
            self.cache[key] = result
        return result

    def evaluate(
        self,
        value: Any,
        profile_validation: ProfileValidation,
        sub_path: None | list[int | str] = None,
    ) -> ValidationResult:
        validator: AccessibleURI = profile_validation
        try:
            data: CvTermValue = CvTermValue.model_validate(value)

            if not data.value:
                logger.debug("URL is not defined")
                return self.return_result(
                    data.value,
                    ValidationResult(
                        sub_path=sub_path,
                        name=validator.name,
                        valid=False,
                        message="URL is not defined",
                        data=value,
                    ),
                )
            if not isinstance(data.value, str):
                logger.debug("Value type is not string: %s", data.value)
                sub_path.append("value")
                return self.return_result(
                    data.value,
                    ValidationResult(
                        sub_path=sub_path,
                        name=validator.name,
                        valid=False,
                        message=f"Value type is not string: {data.value}",
                        data=value,
                    ),
                )
            url: str = data.value

            uri = urlparse(url=url)
            updated_url = url.split("#")[0]
            if updated_url in self.cache:
                return self.cache[updated_url]

            if uri.scheme in ("http", "https"):
                sub_path.append("value")
                logger.debug("Check URL: %s", updated_url)
                result = httpx.head(updated_url, timeout=5)
                if result.status_code == 404:
                    logger.debug("URL does not exist: %s", url)
                    return self.return_result(
                        updated_url,
                        ValidationResult(
                            sub_path=sub_path,
                            name=validator.name,
                            valid=False,
                            message=f"URL does not exist: {value}",
                            data=value,
                        ),
                    )
                result.raise_for_status()
                logger.debug("URL exist: %s", url)
                return self.return_result(
                    updated_url,
                    ValidationResult(
                        sub_path=sub_path,
                        name=validator.name,
                        valid=True,
                        message=f"URL exists: {value}",
                        data=value,
                    ),
                )
            elif uri.scheme in ("ftp", "ftp"):
                sub_path.append("value")
                if uri.hostname not in self.ftp_client_pool:
                    ftp = FTP(user="", host=uri.hostname, timeout=5)
                    ftp.login()
                    if uri.hostname not in self.ftp_client_pool:
                        self.ftp_client_pool[uri.hostname] = ftp
                ftp = self.ftp_client_pool[uri.hostname]
                try:
                    full_path = pathlib.Path(uri.path)
                    ftp.size(str(full_path))

                except Exception as ex:
                    logger.debug(
                        "Target file is not accessible: %s - %s",
                        url,
                        ex.__qualname__,
                    )
                    return self.return_result(
                        updated_url,
                        ValidationResult(
                            sub_path=sub_path,
                            name=validator.name,
                            valid=False,
                            message=f"Target file is not accessible: {url}. {ex.__qualname__}",
                            data=value,
                        ),
                    )

                logger.debug("URL exist: %s", url)
                return self.return_result(
                    updated_url,
                    ValidationResult(
                        sub_path=sub_path,
                        name=validator.name,
                        valid=True,
                        message=f"URL exists: {url}",
                        data=value,
                    ),
                )
            sub_path.append("accession")
            logger.error("Unsupported protocol %s", uri.scheme)
            return self.return_result(
                updated_url,
                ValidationResult(
                    sub_path=sub_path,
                    name=validator.name,
                    valid=False,
                    message=f"Unsupported protocol {url}",
                    data=value,
                ),
            )
        except Exception as ex:
            logger.error("Unaccessible URI: %s", str(ex))
            return self.return_result(
                updated_url,
                ValidationResult(
                    sub_path=sub_path,
                    name=validator.name,
                    valid=False,
                    message=f"Unaccessible URI: {value}",
                    data=value,
                ),
            )


class AccessibleCompactURIValidator(BaseProfileValidator):
    def __init__(
        self,
        cv_helper: CvTermHelper,
        ftp_client_pool: dict[str, FTP],
        url_client: reachable.client.Client,
    ) -> None:
        super().__init__(cv_helper)
        self.ftp_client_pool = ftp_client_pool
        self.url_client = url_client

    def get_profile_validation_class(self) -> type[AccessibleCompactURI]:
        return AccessibleCompactURI

    def evaluate(
        self,
        value: Any,
        profile_validation: ProfileValidation,
        sub_path: None | list[int | str] = None,
    ) -> ValidationResult:
        if not isinstance(profile_validation, AccessibleCompactURI):
            return ValidationResult(
                sub_path=sub_path,
                name="",
                valid=False,
                message=f"invalid validator {str(profile_validation)}",
                data=value,
            )

        if value is None:
            if profile_validation.allow_null_value:
                return ValidationResult(
                    sub_path=sub_path,
                    name=profile_validation.name,
                    valid=True,
                    message="Allow empty value",
                    data=value,
                )
            return ValidationResult(
                sub_path=sub_path,
                name=profile_validation.name,
                valid=False,
                message="Empty file is not allowed.",
                data=value,
            )
        validator: AccessibleCompactURI = profile_validation

        if not validator.default_prefix:
            return ValidationResult(
                sub_path=sub_path,
                name=validator.name,
                valid=False,
                message=f"Invalid URI  prefix: {validator.default_prefix}",
                data=value,
            )
        identifier = value.replace(f"{validator.default_prefix}:", "")
        default_uri = bioregistry.get_default_iri(validator.default_prefix, identifier)

        if not default_uri:
            return ValidationResult(
                sub_path=sub_path,
                name=validator.name,
                valid=False,
                message=f"Invalid URI: {default_uri}",
                data=value,
            )

        headers = {
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Cache-Control": "no-cache",
            "User-Agent": "PostmanRuntime/7.43.3",
            "Authorization": "",
        }
        try:
            url: str = default_uri
            result = httpx.get(
                url,
                headers=headers,
                follow_redirects=validator.follow_redirects,
                timeout=60,
            )
            if not validator.follow_redirects:
                if result.status_code in (301, 302):
                    logger.debug("URL is redirected: %s", default_uri)
                    return ValidationResult(
                        sub_path=sub_path,
                        name=validator.name,
                        valid=True,
                        message=f"URL is redirected: {default_uri}",
                        data=value,
                    )
            if result.status_code == 404:
                logger.warning("URL is not found: %s", default_uri)
                return ValidationResult(
                    sub_path=sub_path,
                    name=validator.name,
                    valid=False,
                    message=f"URL is not found: {default_uri}",
                    data=value,
                )
            result.raise_for_status()
            return ValidationResult(
                sub_path=sub_path,
                name=validator.name,
                valid=True,
                message=f"URL exists: {default_uri}",
                data=value,
            )

        except Exception as ex:
            logger.debug("Unaccessible URI: %s, %s", default_uri)
            logger.exception(ex)
            return ValidationResult(
                sub_path=sub_path,
                name=validator.name,
                valid=False,
                message=f"Unaccessible URI: {default_uri}",
                data=value,
            )
