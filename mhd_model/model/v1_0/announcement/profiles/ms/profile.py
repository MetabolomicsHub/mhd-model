import datetime

from pydantic import AnyUrl, EmailStr, Field, HttpUrl
from typing_extensions import Annotated

from mhd_model.model.v1_0.announcement.profiles.base.profile import (
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
from mhd_model.model.v1_0.announcement.profiles.ms import fields as ms_fields
from mhd_model.shared.fields import Authors, MhdIdentifier
from mhd_model.shared.model import CvTerm


class MsAnnouncementMetadataFile(AnnouncementMetadataFile):
    """Metadata file associated with a mass spectrometry dataset announcement."""

    # format: Annotated[None | ms_fields.MetadataFileFormat, Field()] = None
    extension: Annotated[
        None | str,
        Field(
            min_length=2,
            description="File extension string (e.g. .sdrf, .tsv, .txt).",
        ),
    ] = None
    compression_formats: Annotated[
        None | list[ms_fields.CompressionFormat],
        Field(
            description="List of MS-specific compression formats applied to the metadata file."
        ),
    ] = None


class MsAnnouncementRawDataFile(AnnouncementRawDataFile):
    """Raw experimental data file associated with a mass spectrometry dataset."""

    # format: Annotated[None | ms_fields.RawDataFileFormat, Field()] = None
    compression_formats: Annotated[
        None | list[ms_fields.CompressionFormat],
        Field(
            description="List of MS-specific compression formats applied to the raw data file."
        ),
    ] = None


class MsAnnouncementResultFile(AnnouncementResultFile):
    """Processed result file associated with a mass spectrometry dataset."""

    # format: Annotated[None | ms_fields.ResultFileFormat, Field()] = None
    compression_formats: Annotated[
        None | list[ms_fields.CompressionFormat],
        Field(
            description="List of MS-specific compression formats applied to the result file."
        ),
    ] = None


class MsAnnouncementDerivedDataFile(AnnouncementDerivedDataFile):
    """Derived or processed data file in a mass spectrometry dataset."""

    # format: Annotated[None | ms_fields.DerivedFileFormat, Field()] = None
    compression_formats: Annotated[
        None | list[ms_fields.CompressionFormat],
        Field(
            description="List of MS-specific compression formats applied to the derived data file."
        ),
    ] = None


class MsAnnouncementSupplementaryFile(AnnouncementSupplementaryFile):
    """Supplementary file associated with a mass spectrometry dataset."""

    # format: Annotated[None | ms_fields.SupplementaryFileFormat, Field()] = None
    compression_formats: Annotated[
        None | list[ms_fields.CompressionFormat],
        Field(
            description="List of MS-specific compression formats applied to the supplementary file."
        ),
    ] = None


class MsAnnouncementPublication(AnnouncementPublication):
    """A publication associated with the mass spectrometry dataset."""

    title: Annotated[
        str,
        Field(min_length=10, description="Title of the publication."),
    ]
    doi: Annotated[
        ms_fields.DOI,
        Field(description="Formatted DOI for the mass spectrometry study publication."),
    ]
    pubmed_id: Annotated[
        None | ms_fields.PubMedId,
        Field(description="PubMed unique identifier (PMID) of the publication."),
    ] = None
    author_list: Annotated[
        None | Authors,
        Field(description="List of authors of the publication."),
    ] = None


class MsAnnouncementContact(AnnouncementContact):
    """A contact person associated with the mass spectrometry dataset.
    This can be a submitter or a principal investigator.
    """

    full_name: Annotated[
        str,
        Field(min_length=5, description="Full name of the contact person."),
    ]
    email_list: Annotated[
        list[EmailStr],
        Field(
            min_length=1,
            description="List of validated email addresses for the contact.",
        ),
    ] = None
    affiliation_list: Annotated[
        list[str],
        Field(
            min_length=1,
            description="List of institutional affiliations for the contact.",
        ),
    ] = None
    orcid: Annotated[
        None | ms_fields.ORCID,
        Field(
            title="ORCID",
            description="ORCID digital identifier of the contact person.",
        ),
    ] = None


class MsAnnouncementReportedMetabolite(AnnouncementReportedMetabolite):
    """A metabolite reported as identified or quantified in the mass spectrometry study."""

    name: Annotated[
        str,
        Field(
            min_length=1,
            description="Name or chemical label of the reported metabolite.",
        ),
    ]
    database_identifiers: Annotated[
        None | list[ms_fields.MetaboliteDatabaseId],
        Field(
            description="List of database identifiers (e.g., ChEBI, HMDB, PubChem) for the metabolite."
        ),
    ] = None


class MsAnnouncementProtocol(AnnouncementProtocol):
    """A protocol is a defined and standardized procedure followed
    to collect, prepare, or analyze biological samples in mass spectrometry studies.
    """

    name: Annotated[
        str,
        Field(description="Name or title of the protocol."),
    ]
    protocol_type: Annotated[
        ms_fields.ProtocolType,
        Field(
            description="Type of protocol specified as an MS Controlled Vocabulary term."
        ),
    ]
    description: Annotated[
        None | str,
        Field(description="Detailed description of the experimental protocol."),
    ] = None
    protocol_parameters: Annotated[
        None | list[ms_fields.ExtendedCvTermKeyValue],
        Field(
            description="List of protocol parameters specified as extended CV key-value pairs."
        ),
    ] = None
    relates_assay_names: Annotated[
        None | list[str],
        Field(description="List of assay names that utilize this protocol."),
    ] = None


class AnnouncementMsProfile(AnnouncementBaseProfile):
    """Mass spectrometry profile for dataset announcements.

    Main differences from Base Profile:
    - Mass Spectrometry Specialization: Restricts technology_type, measurement_type, omics_type,
      and assay_type to controlled mass spectrometry terms (defaults technology_type to OBI:0000470).
    - Required Fields: Enforces strict non-null values for mhd_identifier, submitters, principal_investigators,
      measurement_type, omics_type, assay_type, publications (or missing publication reason),
      study_factors, characteristic_values, and raw_data_file_list.
    - Enhanced Validation: Uses specialized MS models for contacts (requiring email and affiliation),
      publications (formatted DOI and PubMed IDs), metabolites, and protocols.
    """

    mhd_identifier: Annotated[
        MhdIdentifier,
        Field(
            description="Unique MetabolomicsHub Data (MHD) identifier for the dataset."
        ),
    ]
    repository_identifier: Annotated[
        str,
        Field(
            description="Original dataset accession number or identifier in the source repository."
        ),
    ]
    mhd_metadata_file_url: Annotated[
        AnyUrl,
        Field(description="URL to the primary MHD metadata file for this dataset."),
    ]
    dataset_url_list: Annotated[
        list[AnyUrl],
        Field(
            min_length=1,
            description="List of web page or repository URLs for accessing the dataset.",
        ),
    ]

    license: Annotated[
        None | HttpUrl,
        Field(
            description="Data usage license or URL defining licensing terms for the dataset."
        ),
    ] = None
    title: Annotated[
        str,
        Field(
            min_length=25,
            description="Title describing the mass spectrometry study or dataset.",
        ),
    ]
    description: Annotated[
        None | str,
        Field(
            min_length=60,
            description="Comprehensive description or summary abstract of the mass spectrometry study.",
        ),
    ]
    submission_date: Annotated[
        None | datetime.datetime,
        Field(
            description="Date and time when the dataset was initially submitted to the repository."
        ),
    ]
    public_release_date: Annotated[
        None | datetime.datetime,
        Field(
            description="Date and time when the dataset was made publicly accessible."
        ),
    ]

    submitters: Annotated[
        list[MsAnnouncementContact],
        Field(
            min_length=1,
            description="List of submitters who registered or submitted the dataset.",
        ),
    ]
    principal_investigators: Annotated[
        list[MsAnnouncementContact],
        Field(
            min_length=1,
            description="List of principal investigators leading the research study.",
        ),
    ]

    # NMR, MS, ...
    technology_type: Annotated[
        list[ms_fields.MsTechnologyType],
        Field(
            min_length=1,
            description="Analytical technology platform (defaults to mass spectrometry assay OBI:0000470).",
        ),
    ] = [
        CvTerm(
            source="OBI",
            accession="OBI:0000470",
            name="mass spectrometry assay",
        )
    ]
    # Targeted metabolite profiling, Untargeted metabolite profiling, ...
    measurement_type: Annotated[
        list[ms_fields.MeasurementType],
        Field(
            min_length=1,
            description="Types of MS measurements performed (e.g., Targeted or Untargeted metabolite profiling).",
        ),
    ]
    # Metabolomics, Lipidomics, Proteomics, ...
    omics_type: Annotated[
        list[ms_fields.OmicsType],
        Field(
            min_length=1,
            description="Omics domains involved in the mass spectrometry study.",
        ),
    ]
    # LC-MS, GC-MS, ...
    assay_type: Annotated[
        list[ms_fields.MsAssayType],
        Field(
            min_length=1,
            description="Mass spectrometry assay techniques employed (e.g., LC-MS, GC-MS).",
        ),
    ]

    publications: Annotated[
        ms_fields.MissingPublicationReason | list[AnnouncementPublication],
        Field(
            description="Publications or specified reason for missing publication in the dataset."
        ),
    ]

    submitter_keywords: Annotated[
        None | list[ms_fields.CvTermOrStr],
        Field(
            description="Keywords provided by the dataset submitter as CV terms or strings."
        ),
    ] = None
    descriptors: Annotated[
        None | list[CvTerm],
        Field(
            description="Subject descriptors or tags characterizing the dataset as CV terms."
        ),
    ] = None

    study_factors: Annotated[
        ms_fields.StudyFactors,
        Field(
            description="Experimental study factors varied across mass spectrometry samples."
        ),
    ]
    characteristic_values: Annotated[
        ms_fields.ExtendedCharacteristicValues,
        Field(
            description="Sample characteristics and metadata attributes for mass spectrometry samples."
        ),
    ]
    protocols: Annotated[
        None | ms_fields.Protocols,
        Field(
            description="List of experimental protocols used in sample preparation and analysis."
        ),
    ] = None

    reported_metabolites: Annotated[
        None | list[MsAnnouncementReportedMetabolite],
        Field(
            description="List of metabolites reported as identified or quantified in the dataset."
        ),
    ] = None

    repository_metadata_file_list: Annotated[
        None | list[MsAnnouncementMetadataFile],
        Field(
            min_length=1,
            description="List of repository metadata files included in the dataset announcement.",
        ),
    ] = None
    raw_data_file_list: Annotated[
        list[MsAnnouncementRawDataFile],
        Field(
            description="List of mass spectrometry raw data files included in the dataset announcement."
        ),
    ]
    derived_data_file_list: Annotated[
        None | list[MsAnnouncementDerivedDataFile],
        Field(
            min_length=1,
            description="List of derived data files included in the dataset announcement.",
        ),
    ] = None
    supplementary_file_list: Annotated[
        None | list[MsAnnouncementSupplementaryFile],
        Field(
            min_length=1,
            description="List of supplementary files included in the dataset announcement.",
        ),
    ] = None
    result_file_list: Annotated[
        None | list[MsAnnouncementResultFile],
        Field(
            description="List of result data files included in the dataset announcement."
        ),
    ] = None
