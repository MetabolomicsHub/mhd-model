import logging
from pathlib import Path

from mhd_model.log_utils import set_basic_logging_config
from mhd_model.model.v0_1.dataset.validation.validator import validate_mhd_model

logger = logging.getLogger(__name__)


if __name__ == "__main__":
    set_basic_logging_config(logging.INFO)

    # study_id = "MSV000099062"
    # file_path = f"tests/data/mhd_data/legacy/{study_id}.mhd.json"
    study_id = "MTBLS3107"
    file_path = Path("tests/data/mhd_data/legacy/MTBLS3107_full.mhd.json")
    success, validation_errors = validate_mhd_model(
        study_id, file_path, validate_announcement_file=True
    )

    if not success:
        for key, errors in validation_errors.items():
            logger.info("\n\n\n%s", "-" * 100)
            logger.info(
                "Found %s validation errors in the MHD file for study %s.",
                len(errors),
                study_id,
            )
            for idx, (error_path, error) in enumerate(errors, start=1):
                logger.info("%s %s %s %s", key, idx, error_path, error.message)
        logger.info("\n%s", "-" * 100)
    else:
        logger.info("MHD file for study %s is validated successfully.", study_id)
