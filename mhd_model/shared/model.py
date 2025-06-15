import datetime
import decimal

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_pascal
from typing_extensions import Annotated


class MhdConfigModel(BaseModel):
    """Base model class to convert python attributes to camel case"""

    model_config = ConfigDict(
        populate_by_name=True,
        JSON_schema_serialization_defaults_required=True,
        field_title_generator=lambda field_name, field_info: to_pascal(
            field_name.replace("_", " ").strip()
        ),
        # alias_generator=to_camel,
    )


class CvTerm(MhdConfigModel):
    source: Annotated[
        str,
        Field(description="Ontology source name."),
    ] = ""
    accession: Annotated[
        str,
        Field(description="Accession number of CV term in compact URI format."),
    ] = ""
    name: Annotated[
        str,
        Field(description="Label of CV term."),
    ] = ""

    def get_unique_id(self):
        return f"{self.source or ''},{self.accession or ''},{self.name or ''}"

    def __hash__(self):
        return hash(self.get_unique_id())

    def __lt__(self, other):
        if isinstance(other, CvTerm):
            return self.get_unique_id() < other.get_unique_id()
        return NotImplemented

    def get_label(self):
        return f"[{self.source or ''}, {self.accession or ''}, {self.name or ''}]"

    def __str__(self):
        return self.get_label()


class UnitCvTerm(CvTerm): ...


class QuantitativeValue(MhdConfigModel):
    value: None | str | int | float | decimal.Decimal = None
    unit: None | UnitCvTerm = None


class CvTermValue(CvTerm, QuantitativeValue):
    def get_unique_id(self):
        unit_key = self.unit.get_unique_id() if self.unit else ""
        value_key = (
            self.value.get_unique_id()
            if isinstance(self.value, CvTerm)
            else str(self.value) if self.value is not None else ""
        )

        return f"{super().get_unique_id()},{value_key or ''},{unit_key or ''}"

    def get_label(self):
        unit_key = self.unit.get_label() if self.unit else ""
        value_key = (
            self.value.get_label()
            if isinstance(self.unit, CvTerm) and self.value
            else str(self.value) if self.value is not None else ""
        )

        return f"[{self.source or ''}, {self.accession or ''}, {self.name or ''}, {value_key or ''}, {unit_key or ''}]"


class CvDefinition(MhdConfigModel):
    label: str = ""
    name: str = ""
    uri: str = ""
    prefix: str = ""
    alternative_labels: None | list[str] = None
    alternative_prefixes: None | list[str] = None


class Revision(MhdConfigModel):
    revision: Annotated[int, Field()]
    revision_datetime: datetime.datetime
    comment: str


class BaseMhdDataset(MhdConfigModel):
    repository_name: Annotated[None | str, Field()] = None
    mhd_identifier: Annotated[None | str, Field()] = None
    repository_identifier: Annotated[None | str, Field()] = None
    revision: Annotated[None | int, Field()] = None
    revision_datetime: Annotated[None | datetime.datetime, Field()] = None
    repository_revision: Annotated[None | int, Field()] = None
    repository_revision_datetime: Annotated[None | datetime.datetime, Field()] = None

    change_log: Annotated[
        None | list[Revision], Field(min_length=1, description="Revision")
    ] = None


class ProfileEnabledDataset(BaseMhdDataset):
    schema_name: Annotated[
        str, Field(alias="$schema", description="Schema name of the file")
    ]
    profile_uri: Annotated[str, Field(description="Validation Profiles")]


class CvEnabledDataset(BaseMhdDataset):
    cv_definitions: Annotated[list[CvDefinition], Field()] = []
