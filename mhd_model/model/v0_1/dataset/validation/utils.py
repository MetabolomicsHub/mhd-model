from mhd_model.model.v0_1.dataset.validation.validator import MhdFileValidator
from mhd_model.utils import json_path, load_json


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
