import logging

from mhd_model.model.v0_1.dataset.validation.validator import validate_mhd_file
from scripts.utils import set_basic_logging_config

logger = logging.getLogger(__name__)


if __name__ == "__main__":
    set_basic_logging_config()

    study_id = "MSV000099062"
    file_path = f"tests/data/mhd_data/legacy/{study_id}.mhd.json"
    validation_errors = validate_mhd_file(file_path)

    if validation_errors:
        logger.info("\n\n\n%s", "-" * 100)
        logger.info(
            "Found %s validation errors in the MHD file for study %s.",
            len(validation_errors),
            study_id,
        )
        for idx, (key, error) in enumerate(validation_errors, start=1):
            logger.info("%s %s %s", idx, key, error.message)
        logger.info("\n%s", "-" * 100)
    else:
        logger.info("MHD file for study %s is validated successfully.", study_id)
