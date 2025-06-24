import json
import logging
from pathlib import Path

from mhd_model.model.v0_1.dataset.validation.validator import MhdFileValidator
from scripts.utils import set_basic_logging_config

logger = logging.getLogger(__name__)


if __name__ == "__main__":
    set_basic_logging_config()

    study_id = "MHDA003107"
    txt = Path(f"tests/data/mhd_data/mtbls/{study_id}.mhd.json").read_text()
    json_data = json.loads(txt)

    mhd_validator = MhdFileValidator()
    errors = mhd_validator.validate(json_data)

    def json_path(field_path: list[int | str]) -> str:
        return ".".join([x if isinstance(x, str) else f"[{x}]" for x in field_path])

    validation_errors = [(json_path(x.absolute_path), x) for x in errors]
    validation_errors.sort(key=lambda x: x[0])
    logger.info("")
    logger.info("")
    logger.info("")
    logger.info("-" * 100)

    for idx, (key, error) in enumerate(validation_errors, start=1):
        logger.info(idx, key, error.message)

    logger.info("-" * 100)
