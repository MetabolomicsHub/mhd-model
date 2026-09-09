from pathlib import Path

from mhd_model.model.definitions import (
    MHD_MODEL_V0_1_LEGACY_PROFILE_NAME,
    MHD_MODEL_V0_1_MS_PROFILE_NAME,
    MHD_MODEL_V1_0_LEGACY_PROFILE_NAME,
    MHD_MODEL_V1_0_MS_PROFILE_NAME,
    ANNOUNCEMENT_FILE_V1_0_MS_PROFILE_NAME,
    ANNOUNCEMENT_FILE_V1_0_LEGACY_PROFILE_NAME,
    ANNOUNCEMENT_FILE_V0_1_MS_PROFILE_NAME,
    ANNOUNCEMENT_FILE_V0_1_LEGACY_PROFILE_NAME,
)
from mhd_model.model.v0_1.announcement.validation.validator import (
    MhdAnnouncementFileValidator as MhdAnnouncementFileValidator_v0_1,
)
from mhd_model.model.v0_1.dataset.validation.validator import (
    validate_mhd_model as validate_mhd_model_v0_1,
)
from mhd_model.model.v1_0.announcement.validation.validator import (
    MhdAnnouncementFileValidator as MhdAnnouncementFileValidator_v1_0,
)
from mhd_model.model.v1_0.dataset.validation.validator import (
    validate_mhd_model as validate_mhd_model_v1_0,
)
from mhd_model.shared.model import ProfileEnabledDataset
from mhd_model.utils import load_json

MHD_VALIDATORS = {
    MHD_MODEL_V0_1_LEGACY_PROFILE_NAME: validate_mhd_model_v0_1,
    MHD_MODEL_V0_1_MS_PROFILE_NAME: validate_mhd_model_v0_1,
    MHD_MODEL_V1_0_LEGACY_PROFILE_NAME: validate_mhd_model_v1_0,
    MHD_MODEL_V1_0_MS_PROFILE_NAME: validate_mhd_model_v1_0,
}

ANNOUNCEMENT_FILE_VALIDATORS = {
    ANNOUNCEMENT_FILE_V0_1_LEGACY_PROFILE_NAME: MhdAnnouncementFileValidator_v0_1,
    ANNOUNCEMENT_FILE_V0_1_MS_PROFILE_NAME: MhdAnnouncementFileValidator_v0_1,
    ANNOUNCEMENT_FILE_V1_0_LEGACY_PROFILE_NAME: MhdAnnouncementFileValidator_v1_0,
    ANNOUNCEMENT_FILE_V1_0_MS_PROFILE_NAME: MhdAnnouncementFileValidator_v1_0,
}


def validate_mhd_model(
    repository_study_id: str,
    mhd_file_path: Path,
    validate_announcement_file: bool = True,
    announcement_file_path: None | Path = None,
    mhd_file_url: None | str = None,
):
    json_data = load_json(mhd_file_path)
    dataset: ProfileEnabledDataset = ProfileEnabledDataset.model_validate(json_data)

    validation_method = MHD_VALIDATORS[dataset.profile_uri]
    return validation_method(
        repository_study_id=repository_study_id,
        mhd_file_path=mhd_file_path,
        validate_announcement_file=validate_announcement_file,
        announcement_file_path=announcement_file_path,
        mhd_file_url=mhd_file_url,
    )


def validate_announcement_file(announcement_file_path: Path):
    json_data = load_json(announcement_file_path)
    dataset: ProfileEnabledDataset = ProfileEnabledDataset.model_validate(json_data)
    validator = ANNOUNCEMENT_FILE_VALIDATORS[dataset.profile_uri]()
    return validator.validate_json_file(json_data)
