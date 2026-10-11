import datetime
from typing import Annotated

from pydantic import ConfigDict, Field

from mhd_model.shared.base import CvTermValue
from mhd_model.shared.model import (
    BaseMhDatasetProfile,
    CvEnabledDataset,
    MhdObjectType,
)


class BaseMhdFile(BaseMhDatasetProfile):
    model_config = ConfigDict(
        json_schema_extra={
            "unique_value_fields": ["uri"],
            "unique_value_alternatives": [
                ("doi",),
                ("mhd_identifier",),
                (
                    "repository_name",
                    "repository_identifier",
                ),
                ("additional_identifier_list",),
            ],
        }
    )
    type_: Annotated[MhdObjectType, Field(alias="type")] = MhdObjectType("default")
    mhd_identifier: Annotated[None | str, Field()] = None


class BaseAnnouncementFile(CvEnabledDataset):
    """Base Profile for dataset announcement files."""

    type_: Annotated[
        None | MhdObjectType,
        Field(
            frozen=True,
            description="The type property identifies type of the file",
            alias="type",
        ),
    ] = "default"

    mhd_identifier: Annotated[
        None | str,
        Field(
            description="Unique MetabolomicsHub Data (MHD) identifier for the dataset."
        ),
    ] = None
    mhd_metadata_file_url: Annotated[
        str,
        Field(description="URL to the primary MHD metadata file for this dataset."),
    ] = None
    mhd_metadata_file_hashes: Annotated[
        None | list[CvTermValue],
        Field(
            description="The cryptographic hash values of the MHD file content, "
            "used to verify file integrity and ensure that the file has not been altered. "
        ),
    ] = None
    submission_date: Annotated[
        None | datetime.datetime,
        Field(
            description="Date and time when the dataset was initially submitted to the repository."
        ),
    ] = None
    public_release_date: Annotated[
        None | datetime.datetime,
        Field(
            description="Date and time when the dataset was made publicly accessible."
        ),
    ] = None
