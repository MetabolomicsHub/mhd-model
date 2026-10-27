import logging
from pathlib import Path

from mhd_model.log_utils import set_basic_logging_config
from mhd_model.validation import validate_mhd_model

logger = logging.getLogger(__name__)


if __name__ == "__main__":
    set_basic_logging_config(logging.INFO)

    # study_id = "MSV000099062"
    # file_path = f"tests/data/mhd_data/legacy/{study_id}.mhd.json"
    study_id = "MTBLS30009012"
    file_path = Path("MTBLS30009012.mhd.json")
    validation_errors = validate_mhd_model(file_path)

    if validation_errors:
        logger.info("\n\n\n%s", "-" * 100)
        for x in validation_errors:
            logger.info(x)

        logger.info("\n%s", "-" * 100)
    else:
        logger.info("MHD file for study %s is validated successfully.", study_id)
