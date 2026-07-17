from pydantic import AnyUrl, Field
from typing_extensions import Annotated

from mhd_model.shared.model import (
    CvTerm,
    MhdConfigModel,
    QuantitativeValue,
)


class SdrfKeyValue(MhdConfigModel):
    key: Annotated[CvTerm, Field()]
    value: Annotated[None | CvTerm | QuantitativeValue, Field()] = None


class SdrfFile(MhdConfigModel):
    name: Annotated[str, Field(min_length=1)]
    url_list: Annotated[None | list[AnyUrl], Field()] = None


class SdrfSampleProtocolDefinition(MhdConfigModel):
    protocol_name: Annotated[str, Field(min_length=1)]
    protocol_type: Annotated[CvTerm, Field()]
    parameter_values: Annotated[list[SdrfKeyValue], Field()]


class LegacySdrfRow(MhdConfigModel):
    sample_name: Annotated[str, Field()]
    characteristics: Annotated[list[SdrfKeyValue], Field()] = []
    assay_name: Annotated[str, Field()]
    protocol_parameters: Annotated[list[SdrfSampleProtocolDefinition], Field()] = []
    factors: Annotated[list[SdrfKeyValue], Field()] = []
    raw_data_files: Annotated[list[SdrfFile], Field()] = []
    derived_data_files: Annotated[list[SdrfFile], Field()] = []
    result_files: Annotated[list[SdrfFile], Field()] = []
    supplementary_files: Annotated[list[SdrfFile], Field()] = []


class LegacySdrf(MhdConfigModel):
    study_identifier: Annotated[str, Field(min_length=1)]
    assay_identifier: Annotated[str, Field(min_length=1)]
    sample_runs: Annotated[list[LegacySdrfRow], Field()] = []
