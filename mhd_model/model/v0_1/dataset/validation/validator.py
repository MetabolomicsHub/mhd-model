import logging
from typing import Any

import jsonschema
import jsonschema.protocols
from jsonschema import protocols, validators

from mhd_model.model.definitions import (
    MHD_MODEL_V0_1_LEGACY_PROFILE_NAME,
    MHD_MODEL_V0_1_MS_PROFILE_NAME,
    SUPPORTED_SCHEMA_MAP,
)
from mhd_model.model.v0_1.dataset.profiles.legacy.graph_validation import (
    MHD_LEGACY_PROFILE_V0_1,
)
from mhd_model.model.v0_1.dataset.profiles.ms.graph_validation import (
    MHD_MS_PROFILE_V0_1,
)
from mhd_model.model.v0_1.dataset.validation.base import MhdModelValidator
from mhd_model.schema_utils import load_mhd_json_schema
from mhd_model.shared.exceptions import MhdValidationError
from mhd_model.shared.model import ProfileEnabledDataset
from mhd_model.utils import json_path, load_json

logger = logging.getLogger(__name__)


def validate_mhd_file(file_path: str):
    json_data = load_json(file_path)

    mhd_validator = MhdFileValidator()
    errors = mhd_validator.validate(json_data)

    messages = set()
    validation_errors = []
    for x in errors:
        if x.message in messages:
            continue
        messages.add(x.message)
        validation_errors.append((json_path(x.absolute_path), x))
    validation_errors.sort(key=lambda x: x[0])
    return validation_errors


MHD_PROFILE_VALIDATIONS_V0_1 = {
    MHD_MODEL_V0_1_MS_PROFILE_NAME: MHD_MS_PROFILE_V0_1,
    MHD_MODEL_V0_1_LEGACY_PROFILE_NAME: MHD_LEGACY_PROFILE_V0_1,
}


def new_validator(
    schema_uri: None | str, profile_uri: None | str
) -> protocols.Validator:
    if not schema_uri:
        schema_uri = SUPPORTED_SCHEMA_MAP.schemas[
            SUPPORTED_SCHEMA_MAP.default_schema_uri
        ]
    if schema_uri in SUPPORTED_SCHEMA_MAP.schemas:
        schema = SUPPORTED_SCHEMA_MAP.schemas.get(schema_uri)
        if not profile_uri:
            profile_uri = schema.default_profile_uri

        if (
            schema.supported_profiles.get(profile_uri)
            and profile_uri in MHD_PROFILE_VALIDATIONS_V0_1
        ):
            _, schema_file = load_mhd_json_schema(profile_uri)
            node_validation = MHD_PROFILE_VALIDATIONS_V0_1[profile_uri]

            mhd_model_validator = MhdModelValidator(node_validation)

            validator = validators.extend(
                jsonschema.Draft202012Validator,
                validators={
                    "mhdGraphValidation": mhd_model_validator.validate_graph,
                    "anyOf": mhd_model_validator.anyOf,
                },
            )
            logger.info("Loaded schema: %s, profile: %s.", schema_uri, profile_uri)
            return validator(schema_file)
    return None


def get_profile(schema_uri: None | str, profile_uri: None | str) -> protocols.Validator:
    if not schema_uri:
        schema_uri = SUPPORTED_SCHEMA_MAP.schemas[
            SUPPORTED_SCHEMA_MAP.default_schema_uri
        ]
    if schema_uri in SUPPORTED_SCHEMA_MAP.schemas:
        schema = SUPPORTED_SCHEMA_MAP.schemas.get(schema_uri)
        if not profile_uri:
            profile_uri = schema.default_profile_uri

        if (
            schema.supported_profiles.get(profile_uri)
            and profile_uri in MHD_PROFILE_VALIDATIONS_V0_1
        ):
            return MHD_PROFILE_VALIDATIONS_V0_1[profile_uri]

    return None


class MhdFileValidator:
    def validate(self, json_file: dict[str, Any]) -> list[jsonschema.ValidationError]:
        profile: ProfileEnabledDataset = ProfileEnabledDataset.model_validate(json_file)
        validator: jsonschema.protocols.Validator = new_validator(
            profile.schema_name, profile.profile_uri
        )
        if not validator:
            logger.error(
                "No validator found for schema %s with profile URI %s",
                profile.schema_name,
                profile.profile_uri,
            )
            raise MhdValidationError(
                f"No validator found for schema {profile.schema_name} with profile URI {profile.profile_uri}"
            )
        validations = validator.iter_errors(json_file)
        all_errors = [x for x in validations]
        return all_errors
