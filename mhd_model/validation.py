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
from mhd_model.model.v0_1.announcement.validation.validator import (
    MhdAnnouncementFileValidator as MhdAnnouncementFileValidator_v0_1,
)
from mhd_model.model.v0_1.dataset.validation.validator import (
    MhdFileValidator_v0_1,
)
from mhd_model.model.v1_0.announcement.validation.validator import (
    MhdAnnouncementFileValidator as MhdAnnouncementFileValidator_v1_0,
)
from mhd_model.model.v1_0.dataset.validation.validator import (
    MhdFileValidator_v1_0,
)
from mhd_model.shared.model import ProfileEnabledDataset
from mhd_model.shared.validation.base import (
    BaseAnnouncementFileValidator,
    BaseMhdFileValidator,
)
from mhd_model.utils import load_json

MHD_VALIDATORS: dict[str, type[BaseMhdFileValidator]] = {
    MHD_MODEL_V0_1_LEGACY_PROFILE_NAME: MhdFileValidator_v0_1,
    MHD_MODEL_V0_1_MS_PROFILE_NAME: MhdFileValidator_v0_1,
    MHD_MODEL_V1_0_LEGACY_PROFILE_NAME: MhdFileValidator_v1_0,
    MHD_MODEL_V1_0_MS_PROFILE_NAME: MhdFileValidator_v1_0,
}

ANNOUNCEMENT_FILE_VALIDATORS: dict[str, type[BaseAnnouncementFileValidator]] = {
    ANNOUNCEMENT_FILE_V0_1_LEGACY_PROFILE_NAME: MhdAnnouncementFileValidator_v0_1,
    ANNOUNCEMENT_FILE_V0_1_MS_PROFILE_NAME: MhdAnnouncementFileValidator_v0_1,
    ANNOUNCEMENT_FILE_V1_0_LEGACY_PROFILE_NAME: MhdAnnouncementFileValidator_v1_0,
    ANNOUNCEMENT_FILE_V1_0_MS_PROFILE_NAME: MhdAnnouncementFileValidator_v1_0,
}


def validate_mhd_file_json(json_data: dict[str, Any]):
    dataset: ProfileEnabledDataset = ProfileEnabledDataset.model_validate(json_data)
    validator = MHD_VALIDATORS[dataset.profile_uri]()
    return validator.validate(mhd_file_json=json_data)


def validate_mhd_model(mhd_file_path: str | Path):
    if isinstance(mhd_file_path, str):
        mhd_file_path = Path(mhd_file_path)
    json_data = load_json(mhd_file_path)
    dataset: ProfileEnabledDataset = ProfileEnabledDataset.model_validate(json_data)

    validator = MHD_VALIDATORS[dataset.profile_uri]()
    return validator.validate(mhd_file_json=json_data)


def validate_announcement_file(announcement_file_path: str | Path) -> list[str]:
    if isinstance(announcement_file_path, str):
        announcement_file_path = Path(announcement_file_path)
    json_data = load_json(announcement_file_path)
    dataset: ProfileEnabledDataset = ProfileEnabledDataset.model_validate(json_data)
    validator: BaseAnnouncementFileValidator = ANNOUNCEMENT_FILE_VALIDATORS[
        dataset.profile_uri
    ]()
    return validator.validate(json_data)


def validate_announcement_file_json(input_json: dict) -> list[str]:
    dataset: ProfileEnabledDataset = ProfileEnabledDataset.model_validate(input_json)
    validator: BaseAnnouncementFileValidator = ANNOUNCEMENT_FILE_VALIDATORS[
        dataset.profile_uri
    ]()
    return validator.validate(input_json)
