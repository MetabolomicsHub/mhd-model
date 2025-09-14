from pydantic import EmailStr, Field
from typing_extensions import Annotated

from mhd_model.model.v0_1.announcement.profiles.base.fields import (
    MeasurementType,
    MissingPublicationReason,
    OmicsType,
)
from mhd_model.model.v0_1.announcement.profiles.base.profile import (
    AnnouncementBaseProfile,
    AnnouncementContact,
    AnnouncementPublication,
    AnnouncementRawDataFile,
    AnnouncementResultFile,
)
from mhd_model.model.v0_1.announcement.profiles.ms import fields
from mhd_model.model.v0_1.dataset.profiles.base.base import (
    CvTerm,
)


class MsAnnouncementContact(AnnouncementContact):
    full_name: Annotated[str, Field(min_length=5)] = None
    emails: Annotated[list[EmailStr], Field(min_length=1)] = None
    affiliations: Annotated[list[str], Field(min_length=1)] = None


class AnnouncementMsProfile(AnnouncementBaseProfile):
    submitters: Annotated[list[MsAnnouncementContact], Field(min_length=1)]
    principal_investigators: Annotated[list[MsAnnouncementContact], Field(min_length=1)]

    # NMR, MS, ...
    technology_type: Annotated[list[fields.MsTechnologyType], Field(min_length=1)] = [
        CvTerm(
            source="OBI",
            accession="OBI:0000470",
            name="mass spectrometry assay",
        )
    ]
    # Targeted metabolite profiling, Untargeted metabolite profiling, ...
    measurement_type: Annotated[list[MeasurementType], Field(min_length=1)]
    # Metabolomics, Lipidomics, Proteomics, ...
    omics_type: Annotated[list[OmicsType], Field(min_length=1)]
    # LC-MS, GC-MS, ...
    assay_type: Annotated[list[fields.MsAssayType], Field(min_length=1)]

    publications: Annotated[
        MissingPublicationReason | list[AnnouncementPublication], Field()
    ]
    study_factors: Annotated[fields.StudyFactors, Field()]
    characteristic_values: Annotated[fields.ExtendedCharacteristicValues, Field()]
    protocols: Annotated[None | fields.Protocols, Field()] = None

    raw_data_file_list: Annotated[list[AnnouncementRawDataFile], Field()]
    result_file_list: Annotated[list[AnnouncementResultFile], Field(min_length=1)]
