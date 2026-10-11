import logging
import traceback
from pathlib import Path
from typing import Any

from mhd_model.model.definitions import (
    ANNOUNCEMENT_FILE_V0_1_LEGACY_PROFILE_NAME,
    ANNOUNCEMENT_FILE_V0_1_MS_PROFILE_NAME,
    ANNOUNCEMENT_FILE_V1_0_LEGACY_PROFILE_NAME,
    ANNOUNCEMENT_FILE_V1_0_MS_PROFILE_NAME,
    MHD_MODEL_V0_1_LEGACY_PROFILE_NAME,
    MHD_MODEL_V0_1_MS_PROFILE_NAME,
    MHD_MODEL_V1_0_LEGACY_PROFILE_NAME,
    MHD_MODEL_V1_0_MS_PROFILE_NAME,
)
from mhd_model.model.v1_0.announcement.validation.json_profie_validator import (
    MhdAnnouncementFileJsonProfileValidator_v1_0,
)
from mhd_model.model.v1_0.dataset.validation.validator import MhdFileValidator_v1_0
from mhd_model.shared.model import MhdModelValidationContext, ProfileEnabledDataset
from mhd_model.shared.validation.base import (
    BaseAnnouncementFileValidator,
    BaseMhdFileValidator,
)
from mhd_model.utils import load_json

logger = logging.getLogger(__name__)

MHD_VALIDATORS: dict[str, type[BaseMhdFileValidator]] = {
    MHD_MODEL_V0_1_LEGACY_PROFILE_NAME: MhdFileValidator_v1_0,
    MHD_MODEL_V0_1_MS_PROFILE_NAME: MhdFileValidator_v1_0,
    MHD_MODEL_V1_0_LEGACY_PROFILE_NAME: MhdFileValidator_v1_0,
    MHD_MODEL_V1_0_MS_PROFILE_NAME: MhdFileValidator_v1_0,
}


ANNOUNCEMENT_FILE_VALIDATORS: dict[str, type[BaseAnnouncementFileValidator]] = {
    ANNOUNCEMENT_FILE_V0_1_LEGACY_PROFILE_NAME: MhdAnnouncementFileJsonProfileValidator_v1_0,
    ANNOUNCEMENT_FILE_V0_1_MS_PROFILE_NAME: MhdAnnouncementFileJsonProfileValidator_v1_0,
    ANNOUNCEMENT_FILE_V1_0_LEGACY_PROFILE_NAME: MhdAnnouncementFileJsonProfileValidator_v1_0,
    ANNOUNCEMENT_FILE_V1_0_MS_PROFILE_NAME: MhdAnnouncementFileJsonProfileValidator_v1_0,
}


def validate_mhd_file_json(
    json_data: dict[str, Any],
    ontology_lookup_file_path: None | str = None,
) -> list[str]:
    dataset: ProfileEnabledDataset = ProfileEnabledDataset.model_validate(json_data)

    validator = MHD_VALIDATORS[dataset.profile_uri]()
    try:
        return validator.validate(mhd_file_json=json_data)
    except Exception as ex:
        traceback.print_exc()
        return [str(ex)]


def validate_mhd_model(
    mhd_file_path: str | Path,
    ontology_lookup_file_path: None | str = None,
) -> list[str]:
    if isinstance(mhd_file_path, str):
        mhd_file_path = Path(mhd_file_path)
    json_data = load_json(mhd_file_path)
    dataset: ProfileEnabledDataset = ProfileEnabledDataset.model_validate(json_data)

    validator = MHD_VALIDATORS[dataset.profile_uri]()
    try:
        context = MhdModelValidationContext()
        validator.validate(
            mhd_file_json=json_data, mhd_model_validation_context=context
        )
    except Exception as ex:
        traceback.print_exc()
        return [str(ex)]


def validate_announcement_file(
    announcement_file_path: str | Path,
    ontology_lookup_file_path: None | str = None,
) -> list[str]:
    if isinstance(announcement_file_path, str):
        announcement_file_path = Path(announcement_file_path)
    json_data = load_json(announcement_file_path)
    dataset: ProfileEnabledDataset = ProfileEnabledDataset.model_validate(json_data)
    validator: BaseAnnouncementFileValidator = ANNOUNCEMENT_FILE_VALIDATORS[
        dataset.profile_uri
    ]()

    try:
        return validator.validate(
            json_data, ontology_lookup_file_path=ontology_lookup_file_path
        )
    except Exception as ex:
        traceback.print_exc()
        return [str(ex)]


def validate_announcement_file_json(
    input_json: dict,
    ontology_lookup_file_path: None | str = None,
) -> list[str]:
    dataset: ProfileEnabledDataset = ProfileEnabledDataset.model_validate(input_json)
    validator: BaseAnnouncementFileValidator = ANNOUNCEMENT_FILE_VALIDATORS[
        dataset.profile_uri
    ]()
    try:
        return validator.validate(
            input_json, ontology_lookup_file_path=ontology_lookup_file_path
        )
    except Exception as ex:
        traceback.print_exc()
        return [str(ex)]
