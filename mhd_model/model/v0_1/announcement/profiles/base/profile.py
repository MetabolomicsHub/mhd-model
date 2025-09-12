import datetime

from pydantic import AnyUrl, EmailStr, Field, HttpUrl
from typing_extensions import Annotated

from mhd_model.model.v0_1.announcement.profiles.base import fields
from mhd_model.shared.fields import Authors
from mhd_model.shared.model import CvEnabledDataset, CvTerm, MhdConfigModel


class BaseFile(MhdConfigModel):
    name: Annotated[str, Field(min_length=2)]
    url_list: Annotated[list[AnyUrl], Field(min_length=1)]
    compression_format: Annotated[None | fields.CompressionFormat, Field()] = None


class MetadataFile(BaseFile):
    format: Annotated[None | fields.MetadataFileFormat, Field()] = None


class RawDataFile(BaseFile):
    format: Annotated[fields.RawDataFileFormat, Field()]


class ResultFile(BaseFile):
    format: Annotated[None | fields.ResultFileFormat, Field()]


class DerivedDataFile(BaseFile):
    format: Annotated[None | fields.DerivedFileFormat, Field()]


class SupplementaryFile(BaseFile):
    format: Annotated[None | fields.SupplementaryFileFormat, Field()]


class AnnouncementContact(MhdConfigModel):
    full_name: Annotated[None | str, Field(min_length=5)] = None
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


class AnnouncementBaseProfile(CvEnabledDataset):
    mhd_identifier: Annotated[None | str, Field()]
    repository_identifier: Annotated[str, Field()]
    mhd_metadata_file_url: Annotated[AnyUrl, Field()]
    dataset_url_list: Annotated[list[AnyUrl], Field(min_length=1)]

    license: Annotated[None | HttpUrl, Field()]
    title: Annotated[str, Field(min_length=25)]
    description: Annotated[str, Field(min_length=60)]
    submission_date: Annotated[datetime.datetime, Field()]
    public_release_date: Annotated[datetime.datetime, Field()]

    submitters: Annotated[None | list[AnnouncementContact], Field(min_length=1)]
    principal_investigators: Annotated[None | list[AnnouncementContact], Field()] = None

    # Targeted metabolite profiling, Untargeted metabolite profiling, ...
    measurement_type: Annotated[None | list[fields.MeasurementType], Field()] = None
    # NMR, MS, ...
    technology_type: Annotated[None | list[fields.TechnologyType], Field(min_length=1)]

    # Metabolomics, Lipidomics, Proteomics, ...
    omics_type: Annotated[None | list[fields.OmicsType], Field(min_length=1)]

    # LC-MS, GC-MS, ...
    assay_type: Annotated[None | list[fields.AnalysisType], Field(min_length=1)]

    submitter_keywords: Annotated[None | list[fields.CvTermOrStr], Field()] = None
    descriptors: Annotated[None | list[CvTerm], Field()] = None

    publications: Annotated[
        None | CvTerm | list[AnnouncementPublication],
        Field(),
    ] = None

    study_factors: Annotated[None | fields.StudyFactors, Field()] = None

    characteristic_values: Annotated[None | fields.CharacteristicValues, Field()] = None

    protocols: Annotated[None | fields.Protocols, Field()] = None

    reported_metabolites: Annotated[None | list[ReportedMetabolite], Field()] = None

    repository_metadata_file_list: Annotated[None | list[MetadataFile], Field()]
    raw_data_file_list: Annotated[None | list[RawDataFile], Field()] = None
    derived_data_file_list: Annotated[None | list[DerivedDataFile], Field()] = None
    supplementary_file_list: Annotated[
        None | list[SupplementaryFile],
        Field(),
    ] = None
    result_file_list: Annotated[None | list[ResultFile], Field()] = None
