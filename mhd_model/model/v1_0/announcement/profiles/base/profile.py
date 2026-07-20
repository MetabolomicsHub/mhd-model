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
    """Base file model for files referenced in a dataset announcement."""

    name: Annotated[
        str,
        Field(min_length=1, description="Name of the file including extension."),
    ]
    url_list: Annotated[
        list[AnyUrl],
        Field(
            min_length=1,
            description="List of direct download or access URLs for the file.",
        ),
    ]
    compression_formats: Annotated[
        None | list[CvTerm],
        Field(
            description="List of compression format CV terms applied to the file (e.g. gzip, zip)."
        ),
    ] = None
    extension: Annotated[
        None | str,
        Field(description="File extension string (e.g., .mzML, .raw, .txt)."),
    ] = None
    format: Annotated[
        None | CvTerm,
        Field(
            description="File format specified as a Controlled Vocabulary (CV) term."
        ),
    ] = None


class AnnouncementMetadataFile(AnnouncementBaseFile):
    """Metadata file (e.g., SDRF, ISA-Tab) associated with the dataset announcement."""

    format: Annotated[
        None | CvTerm,
        Field(description="Format of the metadata file as a CV term."),
    ] = None


class AnnouncementRawDataFile(AnnouncementBaseFile):
    """Raw experimental data file (e.g., instrument vendor files) associated with the dataset."""

    format: Annotated[
        None | CvTerm,
        Field(description="Format of the raw data file as a CV term."),
    ] = None


class AnnouncementResultFile(AnnouncementBaseFile):
    """Processed result data file (e.g. identification or quantification results) in the dataset."""

    format: Annotated[
        None | CvTerm,
        Field(description="Format of the result data file as a CV term."),
    ] = None


class AnnouncementDerivedDataFile(AnnouncementBaseFile):
    """Derived or processed data file generated from raw data analysis."""

    format: Annotated[
        None | CvTerm,
        Field(description="Format of the derived data file as a CV term."),
    ] = None


class AnnouncementSupplementaryFile(AnnouncementBaseFile):
    """Supplementary file (e.g. documentation, protocols, figures) associated with the dataset."""

    format: Annotated[
        None | CvTerm,
        Field(description="Format of the supplementary file as a CV term."),
    ] = None


class AnnouncementContact(AnnouncementBaseModel):
    """A contact person associated with the dataset.
    This can be a submitter, author, or a principal investigator.
    """

    full_name: Annotated[
        None | str,
        Field(min_length=5, description="Full name of the contact person."),
    ] = None
    email_list: Annotated[
        None | list[str],
        Field(min_length=1, description="List of contact email addresses."),
    ] = None
    orcid: Annotated[
        None | str,
        Field(
            title="ORCID",
            description="ORCID digital identifier of the contact person.",
        ),
    ] = None
    affiliation_list: Annotated[
        None | list[str],
        Field(
            min_length=1,
            description="List of institutional affiliations for the contact.",
        ),
    ] = None


class AnnouncementPublication(AnnouncementBaseModel):
    """A publication associated with the dataset."""

    title: Annotated[
        str,
        Field(min_length=10, description="Title of the publication."),
    ]
    doi: Annotated[
        str,
        Field(description="Digital Object Identifier (DOI) for the publication."),
    ]
    pubmed_id: Annotated[
        None | str,
        Field(description="PubMed unique identifier (PMID) of the publication."),
    ] = None
    author_list: Annotated[
        None | list[str],
        Field(description="List of author names for the publication."),
    ] = None


class AnnouncementReportedMetabolite(AnnouncementBaseModel):
    """A metabolite reported as identified or quantified in the dataset."""

    name: Annotated[
        str,
        Field(
            min_length=1,
            description="Name or chemical label of the reported metabolite.",
        ),
    ]
    database_identifiers: Annotated[
        None | list[CvTermValue],
        Field(
            description="List of database identifiers (e.g., ChEBI, RefMet, HMDB, PubChem) "
            "for the metabolite as CV term values."
        ),
    ] = None


class AnnouncementProtocol(AnnouncementBaseModel):
    """A protocol is a defined and standardized procedure followed
    to collect, prepare, or analyze biological samples.
    """

    name: Annotated[
        str,
        Field(description="Name or title of the protocol."),
    ]
    protocol_type: Annotated[
        CvTerm,
        Field(
            description="Type of protocol specified as a Controlled Vocabulary (CV) term."
        ),
    ]
    description: Annotated[
        None | str,
        Field(description="Detailed description of the experimental protocol."),
    ] = None
    protocol_parameters: Annotated[
        None | list[CvTermKeyValue],
        Field(
            description="List of protocol parameters specified as key-value CV pairs."
        ),
    ] = None
    relates_assay_names: Annotated[
        None | list[str],
        Field(description="List of assay names that utilize this protocol."),
    ] = None


class AnnouncementBaseProfile(CvEnabledDataset, AnnouncementBaseModel):
    """Base Profile for dataset announcement files."""

    mhd_identifier: Annotated[
        None | str,
        Field(
            description="Unique MetabolomicsHub Data (MHD) identifier for the dataset."
        ),
    ] = None
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
    doi: Annotated[
        None | str,
        Field(description="Digital Object Identifier (DOI) assigned to the dataset."),
    ] = None
    license: Annotated[
        None | HttpUrl | str,
        Field(
            description="Data usage license or URL defining licensing terms for the dataset."
        ),
    ] = None
    title: Annotated[
        str,
        Field(
            min_length=25,
            description="Title describing the dataset and underlying study.",
        ),
    ]
    description: Annotated[
        None | str,
        Field(
            min_length=60,
            description="Comprehensive description or summary abstract of the dataset.",
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
        None | list[AnnouncementContact],
        Field(
            min_length=1,
            description="List of submitters who registered or submitted the dataset.",
        ),
    ]
    principal_investigators: Annotated[
        None | list[AnnouncementContact],
        Field(
            description="List of principal investigators leading the research study."
        ),
    ] = None

    # Metabolomics, Lipidomics, Proteomics, ...
    omics_type: Annotated[
        None | list[CvTerm],
        Field(
            min_length=1,
            description="Omics domains involved in the study (e.g., Metabolomics, Lipidomics).",
        ),
    ] = None
    # NMR, MS, ...
    technology_type: Annotated[
        None | list[CvTerm],
        Field(
            min_length=1,
            description="Analytical technology platforms used (e.g., Mass Spectrometry, NMR).",
        ),
    ] = None
    # Targeted metabolite profiling, Untargeted metabolite profiling, ...
    measurement_type: Annotated[
        None | list[CvTerm],
        Field(
            description="Types of measurements performed (e.g., Targeted or Untargeted metabolite profiling)."
        ),
    ] = None
    # LC-MS, GC-MS, ...
    assay_type: Annotated[
        None | list[CvTerm],
        Field(
            min_length=1,
            description="Assay techniques employed (e.g., LC-MS, GC-MS).",
        ),
    ] = None

    submitter_keywords: Annotated[
        None | list[CvTerm],
        Field(description="Keywords provided by the dataset submitter as CV terms."),
    ] = None
    descriptors: Annotated[
        None | list[CvTerm],
        Field(
            description="Subject descriptors or tags characterizing the dataset as CV terms."
        ),
    ] = None

    publications: Annotated[
        None | CvTerm | list[AnnouncementPublication],
        Field(
            description="Publications or scientific literature associated with the dataset."
        ),
    ] = None

    study_factors: Annotated[
        None | list[CvTermKeyValue],
        Field(
            description="Experimental study factors varied across samples as CV key-value pairs."
        ),
    ] = None

    characteristic_values: Annotated[
        None | list[CvTermKeyValue],
        Field(
            description="Sample characteristics and metadata attributes as CV key-value pairs."
        ),
    ] = None

    protocols: Annotated[
        None | list[AnnouncementProtocol],
        Field(
            description="List of experimental protocols used in sample preparation and analysis."
        ),
    ] = None

    reported_metabolites: Annotated[
        None | list[AnnouncementReportedMetabolite],
        Field(
            description="List of metabolites reported as identified or quantified in the dataset."
        ),
    ] = None

    repository_metadata_file_list: Annotated[
        None | list[AnnouncementMetadataFile],
        Field(
            min_length=1,
            description="List of repository metadata files included in the dataset announcement.",
        ),
    ] = None
    raw_data_file_list: Annotated[
        None | list[AnnouncementRawDataFile],
        Field(
            min_length=1,
            description="List of raw data files included in the dataset announcement.",
        ),
    ] = None
    derived_data_file_list: Annotated[
        None | list[AnnouncementDerivedDataFile],
        Field(
            min_length=1,
            description="List of derived data files included in the dataset announcement.",
        ),
    ] = None
    supplementary_file_list: Annotated[
        None | list[AnnouncementSupplementaryFile],
        Field(
            min_length=1,
            description="List of supplementary files included in the dataset announcement.",
        ),
    ] = None
    result_file_list: Annotated[
        None | list[AnnouncementResultFile],
        Field(
            min_length=1,
            description="List of result data files included in the dataset announcement.",
        ),
    ] = None
