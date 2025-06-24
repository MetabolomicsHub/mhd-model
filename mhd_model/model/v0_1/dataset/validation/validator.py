import logging
from typing import Any

import jsonschema
import jsonschema.protocols

from mhd_model.model.v0_1.dataset.validation.base import MhdModelValidator
from mhd_model.shared.exceptions import MhdValidationError
from mhd_model.shared.model import ProfileEnabledDataset

logger = logging.getLogger(__name__)


class MhdFileValidator:
    def validate(self, json_file: dict[str, Any]) -> list[jsonschema.ValidationError]:
        profile: ProfileEnabledDataset = ProfileEnabledDataset.model_validate(json_file)
        validator: jsonschema.protocols.Validator = MhdModelValidator.new_instance(
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
