import datetime

from pydantic import Field
from typing_extensions import Annotated

from mhd_model.model.v0_1.announcement.profiles.base import profile as base_profile
from mhd_model.model.v0_1.announcement.profiles.base.profile import (
    AnnouncementBaseProfile,
)


class AnnouncementContact(base_profile.AnnouncementContact):
    full_name: Annotated[str, Field(min_length=5)]


class AnnouncementLegacyProfile(AnnouncementBaseProfile):
    submitters: Annotated[list[AnnouncementContact], Field(min_length=1)]
    repository_metadata_file_list: Annotated[
        list[base_profile.AnnouncementMetadataFile], Field()
    ]
    description: Annotated[str, Field(min_length=60)]
    submission_date: Annotated[datetime.datetime, Field()]
    public_release_date: Annotated[datetime.datetime, Field()]
    submitters: Annotated[list[AnnouncementContact], Field(min_length=1)]
