from pydantic import EmailStr, Field
from typing_extensions import Annotated

from mhd_model.model.v0_1.announcement.profiles.base import fields
from mhd_model.model.v0_1.announcement.profiles.base.profile import (
    AnnouncementBaseProfile,
)
from mhd_model.shared.fields import Authors
from mhd_model.shared.model import MhdConfigModel


class BaseFile(MhdConfigModel):
    name: Annotated[str, Field(min_length=2)]
    file_uri_list: Annotated[list[fields.CvTermUriValue], Field(min_length=1)]
    compression_format: Annotated[None | fields.CompressionFormat, Field()] = None


class MetadataFile(BaseFile):
    format: Annotated[fields.MetadataFileFormat, Field()]


class RawDataFile(BaseFile):
    format: Annotated[fields.RawDataFileFormat, Field()]


class ResultFile(BaseFile):
    format: Annotated[fields.ResultFileFormat, Field()]


class DerivedDataFile(BaseFile):
    format: Annotated[fields.DerivedFileFormat, Field()]


class SupplementaryFile(BaseFile):
    format: Annotated[fields.SupplementaryFileFormat, Field()]


class AnnouncementContact(MhdConfigModel):
    full_name: Annotated[str, Field(min_length=2)]
    emails: Annotated[list[EmailStr], Field(min_length=1)]
    orcid: Annotated[None | fields.ORCID, Field(title="ORCID")] = None
    affiliations: Annotated[None | str, Field(min_length=1)] = None


class AnnouncementPublication(MhdConfigModel):
    title: Annotated[str, Field(min_length=5)]
    doi: Annotated[fields.DOI, Field()]
    pub_med_id: Annotated[None | fields.PubMedId, Field()] = None
    authors: Annotated[None | Authors, Field()] = None


class ReportedMetabolite(MhdConfigModel):
    name: Annotated[str, Field(min_length=1)]
    database_identifiers: Annotated[
        None | list[fields.MetaboliteDatabaseId], Field()
    ] = None


class AnnouncementLegacyProfile(AnnouncementBaseProfile): ...
