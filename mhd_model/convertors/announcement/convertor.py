from typing import Any

from mhd_model.convertors.announcement.v0_1.legacy import (
    mhd2announce as v0_1_mhd2announce_legacy,
)
from mhd_model.convertors.announcement.v0_1.ms import (
    mhd2announce as v0_1_mhd2announce_ms,
)
from mhd_model.convertors.announcement.v1_0.legacy import (
    mhd2announce as v1_0_mhd2announce_legacy,
)
from mhd_model.convertors.announcement.v1_0.ms import (
    mhd2announce as v1_0_mhd2announce_ms,
)
from mhd_model.model.definitions import (
    ANNOUNCEMENT_FILE_V0_1_LEGACY_PROFILE_NAME,
    ANNOUNCEMENT_FILE_V0_1_MS_PROFILE_NAME,
    ANNOUNCEMENT_FILE_V1_0_LEGACY_PROFILE_NAME,
    ANNOUNCEMENT_FILE_V1_0_MS_PROFILE_NAME,
    MHD_MODEL_ANNOUNCEMENT_FILE_PROFILE_MAP,
)
from mhd_model.shared.base import CvTermValue
from mhd_model.shared.model import ProfileEnabledDataset


def create_announcement_file(
    mhd_file: dict[str, Any],
    mhd_file_url: str,
    announcement_file_path: str,
    mhd_metadata_file_hashes: None | list[CvTermValue] = None,
):
    try:
        mhd_dataset = ProfileEnabledDataset.model_validate(mhd_file)
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
        return v0_1_mhd2announce_ms.create_ms_announcement_file(
            mhd_file, mhd_file_url, announcement_file_path
        )
    elif announcement_profile_uri == ANNOUNCEMENT_FILE_V0_1_LEGACY_PROFILE_NAME:
        return v0_1_mhd2announce_legacy.create_legacy_announcement_file(
            mhd_file, mhd_file_url, announcement_file_path
        )
    elif announcement_profile_uri == ANNOUNCEMENT_FILE_V1_0_LEGACY_PROFILE_NAME:
        return v1_0_mhd2announce_legacy.create_legacy_announcement_file(
            mhd_file,
            mhd_file_url,
            announcement_file_path,
            mhd_metadata_file_hashes=mhd_metadata_file_hashes,
        )
    elif announcement_profile_uri == ANNOUNCEMENT_FILE_V1_0_MS_PROFILE_NAME:
        return v1_0_mhd2announce_ms.create_ms_announcement_file(
            mhd_file,
            mhd_file_url,
            announcement_file_path,
            mhd_metadata_file_hashes=mhd_metadata_file_hashes,
        )
    raise ValueError("Invalid profile URI")
