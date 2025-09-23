import datetime

from pydantic import AnyUrl, EmailStr, Field, HttpUrl
from typing_extensions import Annotated

from mhd_model.model.v0_1.dataset.profiles.base.base import (
    BaseLabeledMhdModel,
    BasicCvTermModel,
    BasicCvTermValueModel,
    CvTermObjectId,
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
from mhd_model.shared.model import CvTermValue


class Person(BaseLabeledMhdModel):
    type_: Annotated[
        None | MhdObjectType,
        Field(
            frozen=True,
            alias="type",
            description="The value of this property MUST be 'person'",
        ),
    ] = "person"
    full_name: Annotated[
        None | str, Field(min_length=2, description="Full name of person")
    ] = None
    orcid: Annotated[
        None | ORCID,
        Field(
            title="ORCID",
            description="ORCID identifier of person",
            examples=["1234-0001-8473-1713", "1234-0001-8473-171X"],
        ),
    ] = None
    email_list: Annotated[
        None | list[EmailStr], Field(description="Email addresses of person")
    ] = None
    phone_list: Annotated[
        None | list[str],
        Field(
            description="Phone number of person (with international country code)",
            examples=[["+449340917271", "00449340917271"]],
        ),
    ] = None
    address_list: Annotated[
        None | list[str], Field(description="Addresses of person")
    ] = None

    def get_label(self):
        if self.orcid:
            return self.orcid
        if self.email_list and self.email_list[0]:
            return self.email_list[0]
        return self.full_name or self.id_


class Organization(BaseLabeledMhdModel):
    type_: Annotated[
        None | MhdObjectType,
        Field(
            frozen=True,
            description="The type property identifies type of the object",
            alias="type",
        ),
    ] = "organization"
    repository_identifier: Annotated[None | str, Field()] = None
    name: Annotated[str, Field(min_length=2)]
    department: Annotated[None | str, Field()] = None
    unit: Annotated[None | str, Field()] = None
    address: Annotated[None | str, Field()] = None


class Project(BaseLabeledMhdModel):
    type_: Annotated[
        None | MhdObjectType,
        Field(
            frozen=True,
            description="The type property identifies type of the object",
            alias="type",
        ),
    ] = "project"
    title: Annotated[None | str, Field(min_length=2)] = None
    description: Annotated[None | str, Field()] = None
    grant_identifier_list: Annotated[None | list[GrantId], Field()] = None
    doi: Annotated[None | DOI, Field()] = None

    def get_label(self):
        return self.title or self.id_


class Study(BaseLabeledMhdModel):
    type_: Annotated[
        None | MhdObjectType,
        Field(
            frozen=True,
            description="The type property identifies type of the object",
            alias="type",
        ),
    ] = "study"
    mhd_identifier: Annotated[None | str, Field()] = None
    repository_identifier: Annotated[None | str, Field(min_length=2)] = None
    additional_identifier_list: Annotated[None | list[CvTermValue], Field()] = None
    title: Annotated[None | str, Field()] = None
    description: Annotated[None | str, Field()] = None
    submission_date: None | datetime.datetime = None
    public_release_date: None | datetime.datetime = None
    license: Annotated[
        None | HttpUrl,
        Field(examples=[HttpUrl("https://creativecommons.org/publicdomain/zero/1.0/")]),
    ] = None
    grant_identifier_list: Annotated[None | list[GrantId], Field()] = None
    dataset_url_list: Annotated[None | list[AnyUrl], Field()] = None
    related_dataset_list: Annotated[None | list[KeyValue], Field()] = None
    protocol_refs: Annotated[None | list[MhdObjectId], Field()] = None

    def get_label(self):
        return self.mhd_identifier or self.title or self.id_


class Protocol(BaseLabeledMhdModel):
    type_: Annotated[
        None | MhdObjectType,
        Field(
            frozen=True,
            description="The type property identifies type of the object",
            alias="type",
        ),
    ] = "protocol"
    name: Annotated[None | str, Field()] = None
    protocol_type_ref: Annotated[None | CvTermObjectId, Field()] = None
    description: Annotated[None | str, Field()] = None
    parameter_definition_refs: Annotated[None | list[MhdObjectId], Field()] = None

    def get_label(self) -> str:
        return self.name or self.id_


class ParameterDefinition(BaseLabeledMhdModel):
    type_: Annotated[
        None | MhdObjectType,
        Field(
            frozen=True,
            description="The type property identifies type of the object",
            alias="type",
        ),
    ] = "parameter-definition"
    name: Annotated[None | str, Field()] = None
    parameter_type_ref: Annotated[None | CvTermObjectId, Field()] = None

    def get_label(self):
        return self.name or self.id_


class FactorDefinition(BaseLabeledMhdModel):
    type_: Annotated[
        None | MhdObjectType,
        Field(
            frozen=True,
            description="The type property identifies type of the object",
            alias="type",
        ),
    ] = "factor-definition"
    name: Annotated[None | str, Field()] = None
    factor_type_ref: Annotated[None | CvTermObjectId, Field()] = None

    def get_label(self):
        return self.name or self.id_


class CharacteristicDefinition(BaseLabeledMhdModel):
    type_: Annotated[
        None | MhdObjectType,
        Field(
            frozen=True,
            description="The type property identifies type of the object",
            alias="type",
        ),
    ] = "characteristic-definition"
    name: Annotated[None | str, Field()] = None
    characteristic_type_ref: Annotated[None | CvTermObjectId, Field()] = None

    def get_label(self):
        return self.name or self.id_


class Publication(BaseLabeledMhdModel):
    """
    A document that is the output of a publishing process. [IAO, IAO:0000311, publication]
    """

    type_: Annotated[
        None | MhdObjectType,
        Field(
            frozen=True,
            description="The type property identifies type of the object",
            alias="type",
        ),
    ] = "publication"
    title: Annotated[str, Field(min_length=10)]
    doi: Annotated[DOI, Field()]
    pubmed_id: Annotated[None | PubMedId, Field()] = None
    author_list: Annotated[None | Authors, Field()] = None

    def get_label(self):
        return self.doi or self.title or self.id_


class BasicAssay(BaseLabeledMhdModel):
    type_: Annotated[None | MhdObjectType, Field(..., frozen=True, alias="type")] = (
        "assay"
    )
    repository_identifier: Annotated[
        None | str,
        Field(
            description="An assay identifier that uniquely identifies the assay in repository."
        ),
    ] = None
    name: Annotated[
        None | str,
        Field(description="Name of the assay. It SHOULD be unique in a study."),
    ] = None
    metadata_file_ref: Annotated[
        None | MhdObjectId,
        Field(),
    ] = None

    technology_type_ref: Annotated[
        None | CvTermObjectId,
        Field(),
    ] = None
    assay_type_ref: Annotated[
        None | CvTermObjectId,
        Field(),
    ] = None
    measurement_type_ref: Annotated[
        None | CvTermObjectId,
        Field(),
    ] = None
    omics_type_ref: Annotated[
        None | CvTermObjectId,
        Field(),
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
        Field(),
    ] = None

    def get_label(self):
        return self.name or self.id_


class Subject(BaseLabeledMhdModel):
    type_: Annotated[
        None | MhdObjectType,
        Field(
            frozen=True,
            description="The type property identifies type of the object",
            alias="type",
        ),
    ] = "subject"
    name: Annotated[None | str, Field()] = None
    subject_type_ref: Annotated[None | CvTermObjectId, Field()] = None
    repository_identifier: Annotated[None | str, Field()] = None
    additional_identifier_list: Annotated[None | list[CvTermValue], Field()] = None

    def get_label(self):
        return self.name or self.id_


class Specimen(BaseLabeledMhdModel):
    type_: Annotated[
        None | MhdObjectType,
        Field(
            frozen=True,
            description="The type property identifies type of the object",
            alias="type",
        ),
    ] = "specimen"
    name: Annotated[None | str, Field()] = None
    repository_identifier: Annotated[None | str, Field()] = None
    additional_identifier_list: Annotated[None | list[CvTermValue], Field()] = None

    def get_label(self):
        return self.name or self.id_


class Sample(BaseLabeledMhdModel):
    type_: Annotated[
        None | MhdObjectType,
        Field(
            frozen=True,
            description="The type property identifies type of the object",
            alias="type",
        ),
    ] = "sample"
    name: Annotated[None | str, Field()] = None
    repository_identifier: Annotated[None | str, Field()] = None
    additional_identifier_list: Annotated[None | list[CvTermValue], Field()] = None

    def get_label(self):
        return self.name or self.id_


class SampleRun(BaseLabeledMhdModel):
    type_: Annotated[
        None | MhdObjectType,
        Field(
            frozen=True,
            description="The type property identifies type of the object",
            alias="type",
        ),
    ] = "sample-run"
    name: Annotated[None | str, Field()] = None
    sample_ref: Annotated[
        None | MhdObjectId,
        Field(),
    ] = None
    sample_run_configuration_refs: Annotated[
        None | list[MhdObjectId],
        Field(),
    ] = None
    raw_data_file_refs: Annotated[
        None | list[MhdObjectId],
        Field(),
    ] = None
    derived_data_file_refs: Annotated[
        None | list[MhdObjectId],
        Field(),
    ] = None
    result_file_refs: Annotated[
        None | list[MhdObjectId],
        Field(),
    ] = None
    supplementary_file_refs: Annotated[
        None | list[MhdObjectId],
        Field(),
    ] = None

    def get_label(self):
        return self.name or self.id_


class SampleRunConfiguration(BaseLabeledMhdModel):
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
        Field(),
    ] = None
    parameter_value_refs: Annotated[
        None | list[MhdObjectId | CvTermObjectId | CvTermValueObjectId],
        Field(),
    ] = None


class Metabolite(BaseLabeledMhdModel):
    """
    Any intermediate or product resulting from metabolism.
    The term 'metabolite' subsumes the classes commonly known as primary and secondary metabolites. [CHEBI, CHEBI:25212, metabolite]
    """

    type_: Annotated[
        None | MhdObjectType,
        Field(
            frozen=True,
            description="The type property identifies type of the object",
            alias="type",
        ),
    ] = "metabolite"
    name: Annotated[None | str, Field()] = None

    def get_label(self):
        return self.name or self.id_


class BaseFile(BaseLabeledMhdModel):
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
    hash_sha256: Annotated[
        None | str,
        Field(
            description="The SHA-256 cryptographic hash of the file content, "
            "used to verify file integrity and ensure that the file has not been altered."
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
    pass
    # metadata_file_refs: Annotated[
    #     None | list[MhdObjectId],
    #     Field(
    #         description="The id properties of metadata file that references or describes the file."
    #     ),
    # ] = None


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
    type_: Annotated[
        None | MhdObjectType,
        Field(
            frozen=True,
            description="The type property identifies type of the object",
            alias="type",
        ),
    ] = "metadata-file"


class ResultFile(BaseFile):
    type_: Annotated[
        None | MhdObjectType,
        Field(
            frozen=True,
            description="The type property identifies type of the object",
            alias="type",
        ),
    ] = "result-file"
    # metadata_file_refs: Annotated[None | list[MhdObjectId], Field()] = None


class SupplementaryFile(BaseFile):
    type_: Annotated[
        None | MhdObjectType,
        Field(
            frozen=True,
            description="The type property identifies type of the object",
            alias="type",
        ),
    ] = "supplementary-file"


class CvTermObject(BasicCvTermModel):
    type_: Annotated[
        None | MhdObjectType,
        Field(
            alias="type",
            description="The type property identifies type of the CV Term object",
        ),
    ] = "cv-term"


class CvTermValueObject(BasicCvTermValueModel):
    type_: Annotated[
        None | MhdObjectType,
        Field(
            alias="type",
            description="The type property identifies type of the CV Term Value object",
        ),
    ] = "cv-term-value"
