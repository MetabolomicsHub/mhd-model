from pydantic import Field
from typing_extensions import Annotated

from mhd_model.model.v0_1.announcement.profiles.base.fields import (
    Protocols,
    StudyFactors,
)
from mhd_model.model.v0_1.announcement.profiles.base.profile import (
    AnnouncementBaseProfile,
    AnnouncementContact,
    AnnouncementPublication,
    RawDataFile,
    ResultFile,
)
from mhd_model.model.v0_1.announcement.profiles.legacy.fields import (
    MissingPublicationReason,
)
from mhd_model.model.v0_1.announcement.profiles.ms import fields
from mhd_model.model.v0_1.dataset.profiles.base.base import (
    CvTerm,
)


class AnnouncementMsProfile(AnnouncementBaseProfile):
    principal_investigators: Annotated[list[AnnouncementContact], Field(min_length=1)]

    # NMR, MS, ...
    technology_type: Annotated[list[fields.MsTechnologyType], Field(min_length=1)] = [
        CvTerm(
            source="OBI",
            accession="OBI:0000470",
            name="mass spectrometry assay",
        )
    ]
    publications: Annotated[
        MissingPublicationReason | list[AnnouncementPublication], Field()
    ]
    # LC-MS, GC-MS, ...
    assay_type: Annotated[list[fields.MsAnalysisType], Field(min_length=1)]

    study_factors: Annotated[StudyFactors, Field()]
    characteristic_values: Annotated[fields.ExtendedCharacteristicValues, Field()]
    protocols: Annotated[None | Protocols, Field()] = None

    raw_data_file_list: Annotated[list[RawDataFile], Field(min_length=1)]
    result_file_list: Annotated[list[ResultFile], Field(min_length=1)]
