import datetime

from pydantic import EmailStr, Field, HttpUrl
from typing_extensions import Annotated

from mhd_model.model.v0_1.announcement.profiles.base import fields
from mhd_model.shared.fields import Authors
from mhd_model.shared.model import CvTerm, MhdConfigModel, ProfileEnabledDataset


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
    emails: Annotated[None | list[EmailStr], Field(min_length=1)] = None
    orcid: Annotated[None | fields.ORCID, Field(title="ORCID")] = None
    affiliations: Annotated[None | list[str], Field(min_length=1)] = None


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


class AnnouncementBaseProfile(ProfileEnabledDataset):
    mhd_identifier: Annotated[str, Field()]
    repository_identifier: Annotated[str, Field()]
    mhd_metadata_file_uri: Annotated[fields.CvTermUriValue, Field()]
    dataset_uri_list: Annotated[list[fields.CvTermUriValue], Field(min_length=1)]

    dataset_license: Annotated[HttpUrl, Field()]
    title: Annotated[str, Field(min_length=5)]
    description: Annotated[str, Field(min_length=5)]
    submission_date: Annotated[datetime.datetime, Field()]
    public_release_date: Annotated[datetime.datetime, Field()]

    submitters: Annotated[list[AnnouncementContact], Field(min_length=1)]
    principal_investigators: Annotated[None | list[AnnouncementContact], Field()] = None

    # Targeted metabolite profiling, Untargeted metabolite profiling, ...
    measurement_methodology: Annotated[
        None | list[fields.MeasurementMethodology], Field()
    ] = None
    # NMR, MS, ...
    technology_type: Annotated[list[fields.TechnologyType], Field(min_length=1)]

    # LC-MS, GC-MS, ...
    analysis_type: Annotated[list[fields.AnalysisType], Field(min_length=1)]

    submitter_keywords: Annotated[None | list[fields.CvTermOrStr], Field()] = None
    descriptors: Annotated[None | list[CvTerm], Field()] = None

    publications: Annotated[
        None | CvTerm | list[AnnouncementPublication],
        Field(),
    ] = None

    study_factors: Annotated[None | fields.StudyFactors, Field()] = None

    sample_characteristics: Annotated[None | fields.SampleCharacteristics, Field()] = (
        None
    )

    protocols: Annotated[None | fields.Protocols, Field()] = None

    reported_metabolites: Annotated[None | list[ReportedMetabolite], Field()] = None

    repository_metadata_file_uri_list: Annotated[None | list[MetadataFile], Field()]
    raw_data_file_uri_list: Annotated[None | list[RawDataFile], Field()] = None
    derived_data_file_uri_list: Annotated[None | list[DerivedDataFile], Field()] = None
    supplementary_file_uri_list: Annotated[
        None | list[SupplementaryFile],
        Field(),
    ] = None
    result_file_uri_list: Annotated[None | list[ResultFile], Field()] = None
