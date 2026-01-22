import datetime

from pydantic import AnyUrl, EmailStr, Field, HttpUrl
from typing_extensions import Annotated

from mhd_model.model.v0_1.announcement.profiles.base.profile import (
    AnnouncementBaseProfile,
    AnnouncementContact,
    AnnouncementDerivedDataFile,
    AnnouncementMetadataFile,
    AnnouncementProtocol,
    AnnouncementPublication,
    AnnouncementRawDataFile,
    AnnouncementReportedMetabolite,
    AnnouncementResultFile,
    AnnouncementSupplementaryFile,
)
from mhd_model.model.v0_1.announcement.profiles.ms import fields as ms_fields
from mhd_model.shared.fields import Authors, MhdIdentifier
from mhd_model.shared.model import CvTerm


class MsAnnouncementMetadataFile(AnnouncementMetadataFile):
    format: Annotated[None | ms_fields.MetadataFileFormat, Field()] = None
    compression_formats: Annotated[
        None | list[ms_fields.CompressionFormat], Field()
    ] = None


class MsAnnouncementRawDataFile(AnnouncementRawDataFile):
    format: Annotated[None | ms_fields.RawDataFileFormat, Field()] = None
    format: Annotated[None | ms_fields.MetadataFileFormat, Field()] = None
    compression_formats: Annotated[
        None | list[ms_fields.CompressionFormat], Field()
    ] = None


class MsAnnouncementResultFile(AnnouncementResultFile):
    format: Annotated[None | ms_fields.ResultFileFormat, Field()] = None
    format: Annotated[None | ms_fields.MetadataFileFormat, Field()] = None
    compression_formats: Annotated[
        None | list[ms_fields.CompressionFormat], Field()
    ] = None


class MsAnnouncementDerivedDataFile(AnnouncementDerivedDataFile):
    format: Annotated[None | ms_fields.DerivedFileFormat, Field()] = None
    format: Annotated[None | ms_fields.MetadataFileFormat, Field()] = None
    compression_formats: Annotated[
        None | list[ms_fields.CompressionFormat], Field()
    ] = None


class MsAnnouncementSupplementaryFile(AnnouncementSupplementaryFile):
    format: Annotated[None | ms_fields.SupplementaryFileFormat, Field()] = None


class MsAnnouncementPublication(AnnouncementPublication):
    """A publication associated with the dataset."""

    title: Annotated[str, Field(min_length=10)]
    doi: Annotated[ms_fields.DOI, Field()]
    pubmed_id: Annotated[None | ms_fields.PubMedId, Field()] = None
    author_list: Annotated[None | Authors, Field()] = None


class MsAnnouncementContact(AnnouncementContact):
    """A contact associated with the dataset.
    This can be a submitter or a principal investigator.
    """

    full_name: Annotated[str, Field(min_length=5)]
    emails: Annotated[list[EmailStr], Field(min_length=1)] = None
    affiliations: Annotated[list[str], Field(min_length=1)] = None
    orcid: Annotated[None | ms_fields.ORCID, Field(title="ORCID")] = None


class MsAnnouncementReportedMetabolite(AnnouncementReportedMetabolite):
    name: Annotated[str, Field(min_length=1)]
    database_identifiers: Annotated[
        None | list[ms_fields.MetaboliteDatabaseId], Field()
    ] = None


class MsAnnouncementProtocol(AnnouncementProtocol):
    """A protocol is a defined and standardized procedure followed
    to collect, prepare, or analyze biological samples.
    """

    name: Annotated[str, Field()]
    protocol_type: Annotated[ms_fields.ProtocolType, Field()]
    description: Annotated[None | str, Field()] = None
    protocol_parameters: Annotated[
        None | list[ms_fields.ExtendedCvTermKeyValue], Field()
    ] = None
    relates_assay_names: Annotated[None | list[str], Field()] = None


class AnnouncementMsProfile(AnnouncementBaseProfile):
    mhd_identifier: Annotated[MhdIdentifier, Field()]
    repository_identifier: Annotated[str, Field()]
    mhd_metadata_file_url: Annotated[AnyUrl, Field()]
    dataset_url_list: Annotated[list[AnyUrl], Field(min_length=1)]

    license: Annotated[None | HttpUrl, Field()] = None
    title: Annotated[str, Field(min_length=25)]
    description: Annotated[None | str, Field(min_length=60)]
    submission_date: Annotated[None | datetime.datetime, Field()]
    public_release_date: Annotated[None | datetime.datetime, Field()]

    submitters: Annotated[list[MsAnnouncementContact], Field(min_length=1)]
    principal_investigators: Annotated[list[MsAnnouncementContact], Field(min_length=1)]

    # NMR, MS, ...
    technology_type: Annotated[
        list[ms_fields.MsTechnologyType], Field(min_length=1)
    ] = [
        CvTerm(
            source="OBI",
            accession="OBI:0000470",
            name="mass spectrometry assay",
        )
    ]
    # Targeted metabolite profiling, Untargeted metabolite profiling, ...
    measurement_type: Annotated[list[ms_fields.MeasurementType], Field(min_length=1)]
    # Metabolomics, Lipidomics, Proteomics, ...
    omics_type: Annotated[list[ms_fields.OmicsType], Field(min_length=1)]
    # LC-MS, GC-MS, ...
    assay_type: Annotated[list[ms_fields.MsAssayType], Field(min_length=1)]

    publications: Annotated[
        ms_fields.MissingPublicationReason | list[AnnouncementPublication],
        Field(),
    ]

    submitter_keywords: Annotated[None | list[ms_fields.CvTermOrStr], Field()] = None
    descriptors: Annotated[None | list[CvTerm], Field()] = None

    study_factors: Annotated[ms_fields.StudyFactors, Field()]
    characteristic_values: Annotated[ms_fields.ExtendedCharacteristicValues, Field()]
    protocols: Annotated[None | ms_fields.Protocols, Field()] = None

    reported_metabolites: Annotated[
        None | list[MsAnnouncementReportedMetabolite], Field()
    ] = None

    repository_metadata_file_list: Annotated[
        None | list[MsAnnouncementMetadataFile], Field(min_length=1)
    ] = None
    raw_data_file_list: Annotated[list[MsAnnouncementRawDataFile], Field()]
    derived_data_file_list: Annotated[
        None | list[MsAnnouncementDerivedDataFile], Field(min_length=1)
    ] = None
    supplementary_file_list: Annotated[
        None | list[MsAnnouncementSupplementaryFile],
        Field(min_length=1),
    ] = None
    result_file_list: Annotated[None | list[MsAnnouncementResultFile], Field()] = None
