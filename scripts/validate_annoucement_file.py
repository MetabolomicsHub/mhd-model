from __future__ import annotations

import logging

from mhd_model.log_utils import set_basic_logging_config
from mhd_model.model.v0_1.announcement.validation.validator import (
    MhdAnnouncementFileValidator,
)
from mhd_model.utils import load_json

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    set_basic_logging_config()
    validator = MhdAnnouncementFileValidator()
    # test_data_file_path = (
    #     "tests/data/announcement_files/legacy/MSV000099062.announcement.json"
    # )
    test_data_file_path = "MTBLS30008987.announcement.json"
    announcement_file_json = load_json(test_data_file_path)
    all_errors = validator.validate(announcement_file_json)
    if all_errors:
        logger.info("-" * 80)
        for idx, x in enumerate(all_errors, start=1):
            logger.info("%s | %s", idx, x)
        logger.info("-" * 80)
        exit(1)
    logger.info("Validation is successful.")
    exit(0)
