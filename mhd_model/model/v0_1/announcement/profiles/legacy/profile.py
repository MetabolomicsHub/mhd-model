from pydantic import AnyUrl, Field
from typing_extensions import Annotated

from mhd_model.model.v0_1.announcement.profiles.base import fields
from mhd_model.model.v0_1.announcement.profiles.base.profile import (
    AnnouncementBaseProfile,
)
from mhd_model.shared.model import MhdConfigModel


class BaseFile(MhdConfigModel):
    name: Annotated[str, Field(min_length=2)]
    url_list: Annotated[list[AnyUrl], Field(min_length=1)]
    compression_format: Annotated[None | fields.CompressionFormat, Field()] = None


class MetadataFile(BaseFile):
    format: Annotated[None | fields.MetadataFileFormat, Field()] = None
    extension: Annotated[None | str, Field(min_length=2)] = None


class AnnouncementLegacyProfile(AnnouncementBaseProfile):
    repository_metadata_file_list: Annotated[list[MetadataFile], Field()]
