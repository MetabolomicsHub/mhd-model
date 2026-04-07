from typing import Any

from mhd_model.convertors.announcement.v0_1.legacy import (
    mhd2announce as mhd2announce_legacy,
)
from mhd_model.convertors.announcement.v0_1.ms import mhd2announce as mhd2announce_ms
from mhd_model.model.definitions import (
    ANNOUNCEMENT_FILE_V0_1_LEGACY_PROFILE_NAME,
    ANNOUNCEMENT_FILE_V0_1_MS_PROFILE_NAME,
    MHD_MODEL_ANNOUNCEMENT_FILE_PROFILE_MAP,
)
from mhd_model.model.v0_1.dataset.profiles.base.profile import MhDatasetBaseProfile


def create_announcement_file(
    mhd_file: dict[str, Any], mhd_file_url: str, announcement_file_path: str
):
    try:
        mhd_dataset = MhDatasetBaseProfile.model_validate(mhd_file)
    except Exception as e:
        raise e
    announcement_schema_name, announcement_profile_uri = (
        MHD_MODEL_ANNOUNCEMENT_FILE_PROFILE_MAP.get(
            mhd_dataset.profile_uri, (None, None)
        )
    )
    if not announcement_schema_name or not announcement_profile_uri:
        raise ValueError("Invalid profile URI")
    if announcement_profile_uri == ANNOUNCEMENT_FILE_V0_1_MS_PROFILE_NAME:
        return mhd2announce_ms.create_ms_announcement_file(
            mhd_file, mhd_file_url, announcement_file_path
        )
    elif announcement_profile_uri == ANNOUNCEMENT_FILE_V0_1_LEGACY_PROFILE_NAME:
        return mhd2announce_legacy.create_legacy_announcement_file(
            mhd_file, mhd_file_url, announcement_file_path
        )
    raise ValueError("Invalid profile URI")
