import abc
import datetime
from typing import Annotated

from pydantic import AnyUrl, ConfigDict, EmailStr, Field, HttpUrl

from mhd_model.shared.base import (
    CvTermObjectId,
    CvTermValue,
    CvTermValueObjectId,
    KeyValue,
    MhdObjectId,
    MhdObjectType,
)
from mhd_model.shared.fields import (
    DOI,
    ORCID,
    Authors,
    GrantId,
    PubMedId,
)
from mhd_model.shared.model import (
    BaseCvTermModel,
    BaseCvTermValueModel,
    BaseMhdObjectModel,
    BaseReferencedObjectModel,
)

DEFAULT_CV_TERM_TYPES = {}


class Person(BaseMhdObjectModel):
    """An individual human being (e.g. author, submitter, principal investigator).
    Its meaning is based on Schema.org's ``Person`` type: https://schema.org/Person
    """

    model_config = ConfigDict(
        json_schema_extra={
            "iri": "https://schema.org/Person",
            "unique_value_alternatives": [
                ("orcid",),
                ("additional_identifier_list",),
                ("email_list",),
            ],
        }
    )
    type_: Annotated[
        None | MhdObjectType,
        Field(
            frozen=True,
            alias="type",
            description="The value of this property MUST be 'person'",
            json_schema_extra={"iri": "https://schema.org/DataType"},
        ),
    ] = "person"
    uri: Annotated[
        str,
        Field(
            description="URI of the person. e.g., urn:mhd:MTBLS:MTBLS1:person:submitter1@ebi.ac.uk",
            json_schema_extra={"iri": "https://schema.org/identifier"},
        ),
    ]
    full_name: Annotated[
        None | str,
        Field(
            min_length=2,
            description="Full name of person",
            json_schema_extra={"iri": "https://schema.org/name"},
        ),
    ] = None
    orcid: Annotated[
        None | ORCID,
        Field(
            title="ORCID",
            description="ORCID identifier of person",
            examples=["1234-0001-8473-1713", "1234-0001-8473-171X"],
            json_schema_extra={"iri": "http://edamontology.org/data_4022"},
        ),
    ] = None
    email_list: Annotated[
        None | list[EmailStr],
        Field(
            description="Email addresses of person.",
            json_schema_extra={"iri": "https://schema.org/email"},
        ),
    ] = None
    phone_list: Annotated[
        None | list[str],
        Field(
            description="Phone number of person (with international country code).",
            examples=[["+449999917271", "00449340917271"]],
            json_schema_extra={"iri": "https://schema.org/telephone"},
        ),
    ] = None
    address_list: Annotated[
        None | list[str],
        Field(
            description="Addresses of person.",
            json_schema_extra={"iri": "https://schema.org/PostalAddress"},
        ),
    ] = None

    def get_label(self):
        if self.orcid:
            return self.orcid
        if self.email_list and self.email_list[0]:
            return self.email_list[0]
        return self.full_name or self.id_


class Organization(BaseMhdObjectModel):
    """An institution, company, university, or department associated with a study or contact."""

    model_config = ConfigDict(
        json_schema_extra={
            "iri": "https://schema.org/Organization",
            "unique_value_alternatives": [
                ("ror_id",),
                ("additional_identifier_list",),
            ],
        }
    )
    type_: Annotated[
        None | MhdObjectType,
        Field(
            frozen=True,
            description="The type property identifies type of the object",
            alias="type",
            json_schema_extra={"iri": "https://schema.org/DataType"},
        ),
    ] = "organization"
    uri: Annotated[
        str,
        Field(
            description="URI of the person. e.g., urn:mhd:MTBLS:MTBLS1:organization:ROR_02catss52",
            json_schema_extra={"iri": "https://schema.org/identifier"},
        ),
    ]
    name: Annotated[
        str,
        Field(
            min_length=2,
            description="Name of the organization.",
            json_schema_extra={"iri": "https://schema.org/legalName"},
        ),
    ]
    ror_id: Annotated[
        None | str,
        Field(description="Research Organization Registry (ROR) identifier."),
    ] = None
    department: Annotated[
        None | str,
        Field(
            description="Department within the organization.",
            json_schema_extra={"iri": "https://schema.org/department"},
        ),
    ] = None
    unit: Annotated[
        None | str,
        Field(
            description="Sub-unit or division within the organization or department."
        ),
    ] = None
    address: Annotated[
        None | str,
        Field(
            description="Postal address of the organization.",
            json_schema_extra={"iri": "https://schema.org/PostalAddress"},
        ),
    ] = None


class Project(BaseMhdObjectModel):
    """An overarching research project encompassing one or more studies."""

    model_config = ConfigDict(
        json_schema_extra={
            "unique_value_alternatives": [
                ("doi",),
                ("additional_identifier_list",),
            ]
        }
    )
    type_: Annotated[
        None | MhdObjectType,
        Field(
            frozen=True,
            description="The type property identifies type of the object",
            alias="type",
        ),
    ] = "project"
    title: Annotated[
        None | str,
        Field(min_length=2, description="Title of the project."),
    ] = None
    description: Annotated[
        None | str,
        Field(description="Summary description of the project goals and scope."),
    ] = None
    grant_identifier_list: Annotated[
        None | list[GrantId],
        Field(description="List of grant identifiers funding the project."),
    ] = None
    doi: Annotated[
        None | DOI,
        Field(description="Digital Object Identifier (DOI) assigned to the project."),
    ] = None

    def get_label(self):
        return self.doi or self.title or self.id_


class Study(BaseMhdObjectModel):
    """A biological research study or experiment comprising samples, protocols, and data."""

    model_config = ConfigDict(
        json_schema_extra={
            "unique_value_alternatives": [
                ("doi",),
                ("mhd_identifier",),
                ("repository_identifier",),
                ("additional_identifier_list",),
                ("url_list",),
            ]
        }
    )
    type_: Annotated[
        None | MhdObjectType,
        Field(
            frozen=True,
            description="The type property identifies type of the object",
            alias="type",
        ),
    ] = "study"
    mhd_identifier: Annotated[
        None | str,
        Field(
            description="Unique MetabolomicsHub Data (MHD) identifier for the study."
        ),
    ] = None
    doi: Annotated[
        None | DOI,
        Field(description="Digital Object Identifier (DOI) for the study."),
    ] = None
    repository_identifier: Annotated[
        None | str,
        Field(
            min_length=2,
            description="Accession number or identifier in the source repository. "
            "If there is no repository short name in identifier, "
            "repository short name MUST be defined as prefix, such as <repository>:<identifier>",
        ),
    ] = None
    title: Annotated[
        None | str,
        Field(description="Title of the study."),
    ] = None
    description: Annotated[
        None | str,
        Field(description="Detailed abstract or summary description of the study."),
    ] = None
    submission_date: Annotated[
        None | datetime.datetime,
        Field(description="Date and time when the study was submitted."),
    ] = None
    public_release_date: Annotated[
        None | datetime.datetime,
        Field(description="Date and time when the study was publicly released."),
    ] = None
    license: Annotated[
        None | HttpUrl,
        Field(
            description="Data license URL defining usage rights for the study.",
            examples=[HttpUrl("https://creativecommons.org/publicdomain/zero/1.0/")],
        ),
    ] = None
    license_name: Annotated[
        None | str,
        Field(description="Data license name.", examples=["CC0 v1.0"]),
    ] = None
    grant_identifier_list: Annotated[
        None | list[GrantId],
        Field(description="List of grant identifiers funding the study."),
    ] = None
    url_list: Annotated[
        None | list[AnyUrl],
        Field(description="List of dataset access or repository URLs."),
    ] = None
    related_dataset_list: Annotated[
        None | list[KeyValue],
        Field(description="List of related dataset key-value pairs."),
    ] = None
    protocol_refs: Annotated[
        None | list[MhdObjectId],
        Field(description="Ordered list of protocol object IDs used in the study."),
    ] = None

    def get_label(self):
        return (
            self.doi
            or self.mhd_identifier
            or self.repository_identifier
            or self.title
            or self.id_
        )


class Protocol(BaseMhdObjectModel):
    """A defined and standardized procedure followed to collect, prepare, or analyze samples."""

    model_config = ConfigDict(
        json_schema_extra={
            "unique_value_alternatives": [
                ("doi",),
                ("additional_identifier_list",),
            ]
        }
    )
    type_: Annotated[
        None | MhdObjectType,
        Field(
            frozen=True,
            description="The type property identifies type of the object",
            alias="type",
        ),
    ] = "protocol"
    doi: Annotated[
        None | DOI,
        Field(description="Digital Object Identifier (DOI) for the protocol."),
    ] = None
    name: Annotated[
        None | str,
        Field(description="Name or title of the protocol."),
    ] = None
    protocol_type_ref: Annotated[
        None | CvTermObjectId,
        Field(description="Reference ID to the protocol type CV term object."),
    ] = None
    description: Annotated[
        None | str,
        Field(description="Detailed description of the protocol procedure."),
    ] = None
    parameter_definition_refs: Annotated[
        None | list[MhdObjectId],
        Field(
            description="List of parameter definition object IDs associated with the protocol."
        ),
    ] = None

    def get_label(self) -> str:
        return self.doi or self.name or self.id_


class ParameterDefinition(BaseMhdObjectModel):
    """Definition of an experimental parameter used within a protocol."""

    type_: Annotated[
        None | MhdObjectType,
        Field(
            frozen=True,
            description="The type property identifies type of the object",
            alias="type",
        ),
    ] = "parameter-definition"
    name: Annotated[
        None | str,
        Field(description="Name of the parameter."),
    ] = None
    parameter_type_ref: Annotated[
        None | CvTermObjectId,
        Field(description="Reference ID to the parameter type CV term object."),
    ] = None

    def get_label(self):
        return self.name or self.id_


class FactorDefinition(BaseMhdObjectModel):
    """Definition of an experimental factor varied across samples in a study."""

    type_: Annotated[
        None | MhdObjectType,
        Field(
            frozen=True,
            description="The type property identifies type of the object",
            alias="type",
        ),
    ] = "factor-definition"
    name: Annotated[
        None | str,
        Field(description="Name of the factor (e.g. dose, time point)."),
    ] = None
    factor_type_ref: Annotated[
        None | CvTermObjectId,
        Field(description="Reference ID to the factor type CV term object."),
    ] = None

    def get_label(self):
        return self.name or self.id_


class CharacteristicDefinition(BaseMhdObjectModel):
    """Definition of a sample characteristic or attribute (e.g. organism, tissue)."""

    type_: Annotated[
        None | MhdObjectType,
        Field(
            frozen=True,
            description="The type property identifies type of the object",
            alias="type",
        ),
    ] = "characteristic-definition"
    name: Annotated[
        None | str,
        Field(description="Name of the characteristic attribute."),
    ] = None
    characteristic_type_ref: Annotated[
        None | CvTermObjectId,
        Field(description="Reference ID to the characteristic type CV term object."),
    ] = None

    def get_label(self):
        return self.name or self.id_


class Publication(BaseMhdObjectModel):
    """A document that is the output of a publishing process. [IAO, IAO:0000311, publication]"""

    model_config = ConfigDict(
        json_schema_extra={
            "unique_value_alternatives": [
                ("doi",),
                ("pubmed_id",),
                ("additional_identifier_list",),
            ]
        }
    )
    type_: Annotated[
        None | MhdObjectType,
        Field(
            frozen=True,
            description="The type property identifies type of the object",
            alias="type",
        ),
    ] = "publication"
    title: Annotated[
        str,
        Field(min_length=10, description="Title of the publication."),
    ]
    doi: Annotated[
        DOI,
        Field(description="Digital Object Identifier (DOI) for the publication."),
    ]
    pubmed_id: Annotated[
        None | PubMedId,
        Field(description="PubMed unique identifier (PMID) of the publication."),
    ] = None
    author_list: Annotated[
        None | Authors,
        Field(description="List of publication authors."),
    ] = None

    def get_label(self):
        return self.doi or self.pubmed_id or self.title or self.id_


class BasicAssay(BaseMhdObjectModel, abc.ABC):
    """Basic analytical assay node representing an experimental measurement procedure."""

    type_: Annotated[None | MhdObjectType, Field(..., frozen=True, alias="type")] = (
        "assay"
    )
    name: Annotated[
        None | str,
        Field(description="Name of the assay. It SHOULD be unique in a study."),
    ] = None
    metadata_file_ref: Annotated[
        None | MhdObjectId,
        Field(description="Reference ID to the metadata file describing the assay."),
    ] = None

    technology_type_ref: Annotated[
        None | CvTermObjectId,
        Field(description="Reference ID to the technology type CV term object."),
    ] = None
    assay_type_ref: Annotated[
        None | CvTermObjectId,
        Field(description="Reference ID to the assay type CV term object."),
    ] = None
    measurement_type_ref: Annotated[
        None | CvTermObjectId,
        Field(description="Reference ID to the measurement type CV term object."),
    ] = None
    omics_type_ref: Annotated[
        None | CvTermObjectId,
        Field(description="Reference ID to the omics type CV term object."),
    ] = None
    protocol_refs: Annotated[
        None | list[MhdObjectId],
        Field(
            description="The id properties of protocols used in assay. A protocol "
            "is a defined and standardized procedure followed to collect, prepare, "
            "or analyze biological samples.",
        ),
    ] = None

    def get_label(self):
        return self.name or self.id_


class Assay(BasicAssay):
    """[OBI, OBI:0000070, assay] A planned process that has the objective to produce information
    about a material entity by examining it.
    """

    type_: Annotated[None | MhdObjectType, Field(..., frozen=True, alias="type")] = (
        "assay"
    )
    sample_run_refs: Annotated[
        None | list[MhdObjectId],
        Field(description="List of sample run object IDs associated with the assay."),
    ] = None

    def get_label(self):
        return self.name or self.id_


class Subject(BaseMhdObjectModel):
    """An individual organism or subject from which biological samples are derived."""

    type_: Annotated[
        None | MhdObjectType,
        Field(
            frozen=True,
            description="The type property identifies type of the object",
            alias="type",
        ),
    ] = "subject"
    name: Annotated[
        None | str,
        Field(description="Name or identifier of the subject."),
    ] = None
    subject_type_ref: Annotated[
        None | CvTermObjectId,
        Field(description="Reference ID to the subject type CV term object."),
    ] = None
    additional_identifier_list: Annotated[
        None | list[CvTermValue],
        Field(description="List of additional identifiers for the subject."),
    ] = None

    def get_label(self):
        return self.name or self.id_


class Specimen(BaseMhdObjectModel):
    """A biological specimen collected from a subject."""

    type_: Annotated[
        None | MhdObjectType,
        Field(
            frozen=True,
            description="The type property identifies type of the object",
            alias="type",
        ),
    ] = "specimen"
    name: Annotated[
        None | str,
        Field(description="Name or identifier of the specimen."),
    ] = None
    additional_identifier_list: Annotated[
        None | list[CvTermValue],
        Field(description="List of additional identifiers for the specimen."),
    ] = None

    def get_label(self):
        return self.name or self.id_


class Sample(BaseMhdObjectModel):
    """A biological sample prepared for analytical measurement."""

    model_config = ConfigDict(
        json_schema_extra={
            "unique_value_alternatives": [
                ("biosamples_accession",),
                ("additional_identifier_list",),
            ]
        }
    )
    type_: Annotated[
        None | MhdObjectType,
        Field(
            frozen=True,
            description="The type property identifies type of the object",
            alias="type",
        ),
    ] = "sample"
    name: Annotated[
        None | str,
        Field(description="Name or identifier of the sample."),
    ] = None
    biosamples_accession: Annotated[
        None | str,
        Field(description="Biosamples accession of the sample."),
    ] = None
    additional_identifier_list: Annotated[
        None | list[CvTermValue],
        Field(description="List of additional identifiers for the sample."),
    ] = None

    def get_label(self):
        return self.name or self.id_


class SampleRun(BaseMhdObjectModel):
    """An analytical run representing the measurement of a sample on an instrument."""

    type_: Annotated[
        None | MhdObjectType,
        Field(
            frozen=True,
            description="The type property identifies type of the object",
            alias="type",
        ),
    ] = "sample-run"
    name: Annotated[
        None | str,
        Field(description="Name or label of the sample run."),
    ] = None
    sample_ref: Annotated[
        None | MhdObjectId,
        Field(description="Reference ID to the sample object measured in this run."),
    ] = None
    sample_run_configuration_refs: Annotated[
        None | list[MhdObjectId],
        Field(description="List of configuration object IDs for the sample run."),
    ] = None
    raw_data_file_refs: Annotated[
        None | list[MhdObjectId],
        Field(
            description="List of raw data file object IDs produced by the sample run."
        ),
    ] = None
    derived_data_file_refs: Annotated[
        None | list[MhdObjectId],
        Field(
            description="List of derived data file object IDs generated from the sample run."
        ),
    ] = None
    result_file_refs: Annotated[
        None | list[MhdObjectId],
        Field(
            description="List of result file object IDs produced from the sample run."
        ),
    ] = None
    supplementary_file_refs: Annotated[
        None | list[MhdObjectId],
        Field(
            description="List of supplementary file object IDs associated with the sample run."
        ),
    ] = None

    def get_label(self):
        return self.name or self.id_


class SampleRunConfiguration(BaseMhdObjectModel):
    """Configuration settings and instrument parameters used for a sample run."""

    type_: Annotated[
        None | MhdObjectType,
        Field(
            frozen=True,
            description="The type property identifies type of the object",
            alias="type",
        ),
    ] = "sample-run-configuration"
    protocol_ref: Annotated[
        None | MhdObjectId,
        Field(
            description="Reference ID to the protocol object defining the run configuration."
        ),
    ] = None
    parameter_value_refs: Annotated[
        None | list[MhdObjectId | CvTermObjectId | CvTermValueObjectId],
        Field(
            description="List of parameter value object IDs specifying run parameters."
        ),
    ] = None


class MolecularEntity(BaseMhdObjectModel):
    """Any constitutionally or isotopically distinct atom, molecule, ion,
    ion pair, radical, radical ion, complex, conformer etc.,
    identifiable as a separately distinguishable entity. [CHEBI, CHEBI:23367, molecular entity]
    """

    model_config = ConfigDict(
        json_schema_extra={
            "unique_value_alternatives": [
                ("name",),
                ("additional_identifier_list",),
            ],
            "type_aliases": ["metabolite"],
        }
    )
    type_: Annotated[
        None | MhdObjectType,
        Field(
            description="The type property identifies type of the object", alias="type"
        ),
    ] = "molecular-entity"
    name: Annotated[
        None | str,
        Field(description="Name or chemical label of the molecular entity."),
    ] = None

    def get_label(self):
        return self.name or self.id_


class BaseFile(BaseMhdObjectModel, abc.ABC):
    """Base model for file objects in the dataset graph."""

    model_config = ConfigDict(
        json_schema_extra={
            "unique_value_alternatives": [
                ("url_list",),
                ("additional_identifier_list",),
            ]
        }
    )
    name: Annotated[
        None | str,
        Field(
            description="Name of the file. File MUST be a file (not folder or link)."
            "It MAY be relative path "
            "(e.g., FILES/study.txt) or a file in a compressed file "
            "(e.g., FILES/study.zip#data/metadata.tsv)."
        ),
    ] = None
    size: Annotated[
        None | int,
        Field(
            description="The size of the file in bytes, "
            "representing the total amount of data contained in the file."
        ),
    ] = None
    file_hashes: Annotated[
        None | list[CvTermValue],
        Field(
            description="The cryptographic hash value of the file content, "
            "used to verify file integrity and ensure that the file has not been altered. "
            "e.g., [MS,  MS:1003151, SHA-256, 414e1797ec75b9dd6ce6ad33fb73f4b8cea2523c68bf14027dcd1d54ff953eba]"
        ),
    ] = None
    format_ref: Annotated[
        None | CvTermObjectId,
        Field(
            description="The structure or encoding used to store the contents of the file, "
            "typically indicated by its extension (e.g., .txt, .csv, .mzML, .raw, etc.)."
        ),
    ] = None
    compression_format_refs: Annotated[
        None | list[CvTermObjectId],
        Field(
            description="The structure or encoding used to compress the contents of the file, "
            "typically indicated by its extension (e.g., .zip, .tar, .gz, etc.)."
            " List item order shows order of compressions. e.g. [tar format, gzip format] for tar.gz"
        ),
    ] = None
    extension: Annotated[
        None | str,
        Field(
            description="The extension of file. It MUST contain all extensions "
            "(e.g., .raw, .mzML, .d.zip, .raw.zip, etc.)."
        ),
    ] = None

    def get_label(self):
        return self.name or self.id_


class ReferencedDataFile(BaseFile):
    """Base model for data files referenced within the dataset."""


class RawDataFile(ReferencedDataFile):
    """[MS, MS:1003083, raw data file]
    Data file that contains original data as generated by an instrument,
    although not necessarily in the original data format
    (i.e. an original raw file converted to a different format is still a raw data file)
    """

    type_: Annotated[
        None | MhdObjectType,
        Field(
            frozen=True,
            description="The type property identifies type of the object",
            alias="type",
        ),
    ] = "raw-data-file"


class DerivedDataFile(ReferencedDataFile):
    """[MS, MS:1003084, processed data file]
    File that contains data that has been substantially processed or
    transformed from what was originally acquired by an instrument.
    """

    type_: Annotated[
        None | MhdObjectType,
        Field(
            frozen=True,
            description="The type property identifies type of the object",
            alias="type",
        ),
    ] = "derived-data-file"


class MetadataFile(BaseFile):
    """Metadata file (e.g., SDRF, ISA-Tab) describing experimental design and samples."""

    type_: Annotated[
        None | MhdObjectType,
        Field(
            frozen=True,
            description="The type property identifies type of the object",
            alias="type",
        ),
    ] = "metadata-file"


class ResultFile(BaseFile):
    """Processed result file (e.g. quantification or identification matrix)."""

    type_: Annotated[
        None | MhdObjectType,
        Field(
            frozen=True,
            description="The type property identifies type of the object",
            alias="type",
        ),
    ] = "result-file"


class SupplementaryFile(BaseFile):
    """Supplementary document or asset file associated with the dataset."""

    type_: Annotated[
        None | MhdObjectType,
        Field(
            frozen=True,
            description="The type property identifies type of the object",
            alias="type",
        ),
    ] = "supplementary-file"


class Spectra(BaseMhdObjectModel):
    """Signal, peak, or pattern data
    that represents the types and amounts of small-molecule  present in a sample
    """

    type_: Annotated[
        None | MhdObjectType,
        Field(
            alias="type",
            description="The type property identifies the type of MHD Object. It must be `spectra`",
        ),
    ] = "spectra"
    uri: Annotated[
        None | str,
        Field(description="Unique identifier of spectra. e.g. USI"),
    ] = None


class CvTermObject(BaseCvTermModel):
    """Controlled Vocabulary (CV) term object node in the dataset graph."""


class CvTermValueObject(BaseCvTermValueModel):
    """Controlled Vocabulary (CV) term value object node with quantitative or string value."""


class ReferencedObject(BaseReferencedObjectModel):
    """Node or link reference defined in other MHD common data model file.
    The specified referenced_id must be already defined in the referenced file.
    """
