import json
import logging
import sys
from pathlib import Path

from mhd_model.model.v0_1.dataset.validation.validator import MhdFileValidator

logger = logging.getLogger(__name__)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s",
        datefmt="%d/%b/%Y %H:%M:%S",
        stream=sys.stdout,
    )

    study_id = "MHDA003107"
    txt = Path(f"tests/data/mhd_data/mtbls/{study_id}.mhd.json").read_text()
    json_data = json.loads(txt)

    mhd_validator = MhdFileValidator()
    errors = mhd_validator.validate(json_data)

    def json_path(field_path):
        return ".".join([x if isinstance(x, str) else f"[{x}]" for x in field_path])

    validation_errors = [(json_path(x.absolute_path), x) for x in errors]
    validation_errors.sort(key=lambda x: x[0])
    print("")
    print("")
    print("")
    print("-" * 100)

    for idx, (key, error) in enumerate(validation_errors, start=1):
        print(idx, key, error.message)

    print("-" * 100)
