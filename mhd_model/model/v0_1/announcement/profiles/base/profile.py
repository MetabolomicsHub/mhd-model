import datetime

from pydantic import AnyUrl, Field, HttpUrl
from typing_extensions import Annotated

from mhd_model.shared.model import (
    CvEnabledDataset,
    CvTerm,
    CvTermKeyValue,
    CvTermValue,
    MhdConfigModel,
)


class AnnouncementBaseModel(MhdConfigModel):
    """Base model for announcement-related models."""

    pass


class AnnouncementBaseFile(AnnouncementBaseModel):
    name: Annotated[str, Field(min_length=1)]
    url_list: Annotated[list[AnyUrl], Field(min_length=1)]
    compression_formats: Annotated[None | list[CvTerm], Field()] = None
    extension: Annotated[None | str, Field(min_length=2)] = None
    format: Annotated[None | CvTerm, Field()] = None


class AnnouncementMetadataFile(AnnouncementBaseFile):
    format: Annotated[None | CvTerm, Field()] = None


class AnnouncementRawDataFile(AnnouncementBaseFile):
    format: Annotated[None | CvTerm, Field()] = None


class AnnouncementResultFile(AnnouncementBaseFile):
    format: Annotated[None | CvTerm, Field()] = None


class AnnouncementDerivedDataFile(AnnouncementBaseFile):
    format: Annotated[None | CvTerm, Field()] = None


class AnnouncementSupplementaryFile(AnnouncementBaseFile):
    format: Annotated[None | CvTerm, Field()] = None


class AnnouncementContact(AnnouncementBaseModel):
    """A contact associated with the dataset.
    This can be a submitter or a principal investigator.
    """

    full_name: Annotated[None | str, Field(min_length=5)] = None
    emails: Annotated[None | list[str], Field(min_length=1)] = None
    orcid: Annotated[None | str, Field(title="ORCID")] = None
    affiliations: Annotated[None | list[str], Field(min_length=1)] = None


class AnnouncementPublication(AnnouncementBaseModel):
    """A publication associated with the dataset."""

    title: Annotated[str, Field(min_length=10)]
    doi: Annotated[str, Field()]
    pubmed_id: Annotated[None | str, Field()] = None
    author_list: Annotated[None | list[str], Field()] = None


class AnnouncementReportedMetabolite(AnnouncementBaseModel):
    name: Annotated[str, Field(min_length=1)]
    database_identifiers: Annotated[None | list[CvTermValue], Field()] = None


class AnnouncementProtocol(AnnouncementBaseModel):
    """A protocol is a defined and standardized procedure followed
    to collect, prepare, or analyze biological samples.
    """

    name: Annotated[str, Field()]
    protocol_type: Annotated[CvTerm, Field()]
    description: Annotated[None | str, Field()] = None
    protocol_parameters: Annotated[None | list[CvTermKeyValue], Field()] = None
    relates_assay_names: Annotated[None | list[str], Field()] = None


class AnnouncementBaseProfile(CvEnabledDataset, AnnouncementBaseModel):
    """Base profile for announcement files."""

    mhd_identifier: Annotated[None | str, Field()] = None
    repository_identifier: Annotated[str, Field()]
    mhd_metadata_file_url: Annotated[AnyUrl, Field()]
    dataset_url_list: Annotated[list[AnyUrl], Field(min_length=1)]

    license: Annotated[None | HttpUrl | str, Field()] = None
    title: Annotated[str, Field(min_length=25)]
    description: Annotated[None | str, Field(min_length=60)]
    submission_date: Annotated[None | datetime.datetime, Field()]
    public_release_date: Annotated[None | datetime.datetime, Field()]

    submitters: Annotated[None | list[AnnouncementContact], Field(min_length=1)]
    principal_investigators: Annotated[None | list[AnnouncementContact], Field()] = None

    # Metabolomics, Lipidomics, Proteomics, ...
    omics_type: Annotated[None | list[CvTerm], Field(min_length=1)] = None
    # NMR, MS, ...
    technology_type: Annotated[None | list[CvTerm], Field(min_length=1)] = None
    # Targeted metabolite profiling, Untargeted metabolite profiling, ...
    measurement_type: Annotated[None | list[CvTerm], Field()] = None
    # LC-MS, GC-MS, ...
    assay_type: Annotated[None | list[CvTerm], Field(min_length=1)] = None

    submitter_keywords: Annotated[None | list[CvTerm], Field()] = None
    descriptors: Annotated[None | list[CvTerm], Field()] = None

    publications: Annotated[
        None | CvTerm | list[AnnouncementPublication],
        Field(),
    ] = None

    study_factors: Annotated[None | list[CvTermKeyValue], Field()] = None

    characteristic_values: Annotated[None | list[CvTermKeyValue], Field()] = None

    protocols: Annotated[
        None | list[AnnouncementProtocol],
        Field(description="The protocols used in the study."),
    ] = None

    reported_metabolites: Annotated[
        None | list[AnnouncementReportedMetabolite], Field()
    ] = None

    repository_metadata_file_list: Annotated[
        None | list[AnnouncementMetadataFile], Field(min_length=1)
    ] = None
    raw_data_file_list: Annotated[
        None | list[AnnouncementRawDataFile], Field(min_length=1)
    ] = None
    derived_data_file_list: Annotated[
        None | list[AnnouncementDerivedDataFile], Field(min_length=1)
    ] = None
    supplementary_file_list: Annotated[
        None | list[AnnouncementSupplementaryFile],
        Field(min_length=1),
    ] = None
    result_file_list: Annotated[
        None | list[AnnouncementResultFile], Field(min_length=1)
    ] = None
