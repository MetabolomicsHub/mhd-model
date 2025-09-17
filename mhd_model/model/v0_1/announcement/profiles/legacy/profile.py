import datetime

from pydantic import Field
from typing_extensions import Annotated

from mhd_model.model.v0_1.announcement.profiles.base import profile as base_profile
from mhd_model.model.v0_1.announcement.profiles.base.profile import (
    AnnouncementBaseProfile,
)
from mhd_model.model.v0_1.announcement.profiles.legacy import fields as legacy_fields


class AnnouncementContact(base_profile.AnnouncementContact):
    full_name: Annotated[str, Field(min_length=5)]


class AnnouncementLegacyProfile(AnnouncementBaseProfile):
    submitters: Annotated[list[AnnouncementContact], Field(min_length=1)]
    repository_metadata_file_list: Annotated[
        list[base_profile.AnnouncementBaseFile], Field()
    ]
    protocols: Annotated[None | legacy_fields.Protocols, Field()] = None
    characteristic_values: Annotated[legacy_fields.CharacteristicValues, Field()] = None
    description: Annotated[str, Field(min_length=60)]
    submission_date: Annotated[datetime.datetime, Field()]
    public_release_date: Annotated[datetime.datetime, Field()]
    submitters: Annotated[list[AnnouncementContact], Field(min_length=1)]
