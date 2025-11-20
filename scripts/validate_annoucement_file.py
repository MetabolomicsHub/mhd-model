from __future__ import annotations

import logging
from typing import OrderedDict

import jsonschema
from jsonschema import exceptions

from mhd_model.log_utils import set_basic_logging_config
from mhd_model.model.v0_1.announcement.validation.base import ProfileValidator
from mhd_model.model.v0_1.announcement.validation.validator import (
    MhdAnnouncementFileValidator,
)
from mhd_model.utils import json_path, load_json

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    set_basic_logging_config()
    validator = MhdAnnouncementFileValidator()
    test_data_file_path = (
        "tests/data/announcement_files/legacy/ST0000253.announcement.json"
    )
    announcement_file_json = load_json(test_data_file_path)
    all_errors = validator.validate(announcement_file_json)

    number = 0
    profile_validator = ProfileValidator()

    def add_all_leaves(
        err: jsonschema.ValidationError, leaves: list[jsonschema.ValidationError]
    ) -> None:
        if err.validator in profile_validator.validators:
            if not err.context:
                leaves.append((err.absolute_path, err))
            else:
                for x in err.context:
                    add_all_leaves(x, leaves)

    errors: OrderedDict = OrderedDict()
    for idx, x in enumerate(all_errors, start=1):
        context_errors = [x]
        if x.validator == "anyOf" and len(x.context) > 1:
            context_errors = [
                x
                for x in x.context
                if x.validator != "type" and x.validator_value != "null"
            ]

        for error_item in context_errors:
            match = exceptions.best_match([error_item])
            error = (json_path(match.absolute_path), match.message)

            if match.validator in profile_validator.validators:
                leaves = []
                add_all_leaves(match, leaves)
                for leaf in leaves:
                    key = json_path(leaf[0])
                    value = leaf[1].message
                    number += 1
                    errors[str(number)] = f"{key}: {value}"
            else:
                number += 1
                errors[str(number)] = f"{error[0]}: {error[1]}"

    logger.info("-" * 80)
    for idx, x in errors.items():
        logger.info("%s | %s", idx, x)
    logger.info("-" * 80)
