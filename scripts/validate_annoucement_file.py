from __future__ import annotations

import logging
import sys
from typing import OrderedDict

import jsonschema
from jsonschema import exceptions

from mhd.model.v0_1.announcement.validation.base import ProfileValidator
from mhd.model.v0_1.announcement.validation.validator import (
    MhdAnnouncementFileValidator,
)
from mhd.utils import json_path, load_json

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s",
        datefmt="%d/%b/%Y %H:%M:%S",
        stream=sys.stdout,
    )
    validator = MhdAnnouncementFileValidator()
    test_data_file_path = "tests/data/announcement_files/MHDA001987_announcement.json"
    announcement_file_json = load_json(test_data_file_path)
    all_errors = validator.validate(announcement_file_json)

    number = 0
    profile_validator = ProfileValidator()

    def add_all_leaves(
        err: jsonschema.ValidationError, leaves: list[jsonschema.ValidationError]
    ):
        if err.validator in profile_validator.validators:
            if not err.context:
                leaves.append((err.absolute_path, err))
            else:
                for x in err.context:
                    add_all_leaves(x, leaves)

    errors: OrderedDict = OrderedDict()
    for idx, x in enumerate(all_errors, start=1):
        match = exceptions.best_match([x])
        error = (json_path(x.absolute_path), match.message)

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

    print("-" * 80)
    for idx, x in errors.items():
        print(idx, "|", x)
    print("-" * 80)
