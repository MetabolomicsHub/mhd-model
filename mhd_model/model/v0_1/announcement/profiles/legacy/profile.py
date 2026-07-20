import datetime

from pydantic import Field
from typing_extensions import Annotated

from mhd_model.model.v0_1.announcement.profiles.base import profile as base_profile
from mhd_model.model.v0_1.announcement.profiles.base.profile import (
    AnnouncementBaseProfile,
)


class AnnouncementContact(base_profile.AnnouncementContact):
    """Contact person associated with a legacy dataset announcement."""

    full_name: Annotated[
        str,
        Field(min_length=5, description="Full name of the contact person."),
    ]


class AnnouncementLegacyProfile(AnnouncementBaseProfile):
    """Legacy profile for dataset announcements.

    Main differences from Base Profile:
    - Required Fields: Enforces strict non-null values for submission_date, public_release_date,
      submitters, and repository_metadata_file_list.
    - Contact Constraints: Requires non-null full_name (min_length=5) on AnnouncementContact.
    - Relaxed Length Constraints: Reduces minimum length restrictions for title (min 1 vs 25)
      and description (min 1 vs 60) to accommodate legacy repository data.
    """

    submitters: Annotated[
        list[AnnouncementContact],
        Field(
            min_length=1,
            description="List of submitters who registered or submitted the dataset.",
        ),
    ]
    repository_metadata_file_list: Annotated[
        list[base_profile.AnnouncementMetadataFile],
        Field(
            description="List of repository metadata files included in the legacy dataset announcement."
        ),
    ]
    title: Annotated[
        str,
        Field(
            min_length=1,
            description="Title describing the dataset and underlying study.",
        ),
    ]
    description: Annotated[
        None | str,
        Field(
            min_length=1,
            description="Description or summary abstract of the dataset.",
        ),
    ]
    submission_date: Annotated[
        datetime.datetime,
        Field(description="Date and time when the dataset was initially submitted."),
    ]
    public_release_date: Annotated[
        datetime.datetime,
        Field(
            description="Date and time when the dataset was made publicly accessible."
        ),
    ]
