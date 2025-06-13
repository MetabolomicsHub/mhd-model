import json
import logging
import pathlib

from mhd_model.model.v0_1.announcement.profiles.base.profile import (
    Announcement,
)
from mhd_model.model.v0_1.announcement.profiles.ms.profile import (
    AnnouncementMsProfile,
)

logger = logging.getLogger(__name__)


def update_annoucement_profiles():
    profile_path = "mhd_model/schemas/mhd/announcement-v0.1.schema.json"
    with pathlib.Path(profile_path).open("w") as f:
        json.dump(Announcement.model_json_schema(), f, indent=2)
    logger.info(
        "Base announcement profile file on directory '%s' is updated.",
        profile_path,
    )

    profile_path = "mhd_model/schemas/mhd/announcement-v0.1.schema.ms-profile.json"
    with pathlib.Path(profile_path).open("w") as f:
        json.dump(AnnouncementMsProfile.model_json_schema(), f, indent=2)
    logger.info(
        "MS announcement profile file on directory '%s' is updated.",
        profile_path,
    )
