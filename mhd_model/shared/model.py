import datetime
import decimal
import logging
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_pascal

logger = logging.getLogger(__name__)


class MhdConfigModel(BaseModel):
    """Base model class to convert python attributes to camel case"""

    model_config = ConfigDict(
        populate_by_name=True,
        json_schema_serialization_defaults_required=True,
        field_title_generator=lambda field_name, field_info: to_pascal(
            field_name.replace("_", " ").strip()
        ),
        # alias_generator=to_camel,
    )

    def get_unique_id(self, type_: None | str = None):
        extra = self.model_config.get("json_schema_extra", {})
        contribution: list[str] = extra.get("unique_value_contribution") or []
        values = [type_] if type_ else []
        if contribution:
            for field_name in contribution:
                value = ""
                if hasattr(self, field_name):
                    value = getattr(self, field_name) or ""
                    if isinstance(value, (dict, list)):
                        logger.warning(
                            "%s %s value is dict or list. It is not used to create unique id",
                            self.__class__,
                            field_name,
                        )
                        continue
                    if isinstance(value, MhdConfigModel):
                        sub_type = value.type_ if hasattr(value, "type_") else None
                        value = f"[{value.get_unique_id(sub_type)}]"
                    elif isinstance(value, datetime.datetime):
                        value = str(value.timestamp()).lower()
                    else:
                        value = str(value).lower()
                else:
                    logger.warning(
                        "%s has no field named %s", self.__class__, field_name
                    )

                values.append(f"{field_name.lower()}={value}")

        return "&".join(values)


class CvTerm(MhdConfigModel):
    model_config = ConfigDict(
        json_schema_extra={"unique_value_contribution": ["source", "accession", "name"]}
    )
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

    def __hash__(self) -> int:
        return hash(self.get_unique_id())

    def __lt__(self, other: "CvTerm") -> bool:
        if isinstance(other, CvTerm):
            return self.get_unique_id() < other.get_unique_id()
        return NotImplemented

    def get_label(self) -> str:
        return f"[{self.source or ''}, {self.accession or ''}, {self.name or ''}]"

    def __str__(self) -> str:
        return self.get_label()


class UnitCvTerm(CvTerm): ...


class QuantitativeValue(MhdConfigModel):
    value: None | str | int | float | decimal.Decimal = None
    unit: None | UnitCvTerm = None


class CvTermValue(CvTerm, QuantitativeValue):
    model_config = ConfigDict(
        json_schema_extra={
            "unique_value_contribution": [
                "source",
                "accession",
                "name",
                "value",
                "unit",
            ]
        }
    )
    value: Annotated[
        None | str | int | float | decimal.Decimal,
        Field(description="Value of CV term."),
    ] = None
    unit: Annotated[
        None | UnitCvTerm,
        Field(description="Unit CV term if value has a unit."),
    ] = None

    def get_label(self) -> str:
        unit_key = self.unit.get_label() if self.unit else ""
        value_key = (
            self.value.get_label()
            if isinstance(self.unit, CvTerm) and self.value
            else str(self.value)
            if self.value is not None
            else ""
        )

        return f"[{self.source or ''}, {self.accession or ''}, {self.name or ''}, {value_key or ''}, {unit_key or ''}]"


class CvTermKeyValue(MhdConfigModel):
    key: Annotated[CvTerm, Field()]
    values: Annotated[None | list[QuantitativeValue] | list[CvTerm], Field()] = None


class CvDefinition(MhdConfigModel):
    label: None | str = None
    name: None | str = None
    uri: None | str = None
    prefix: None | str = None
    version: None | str = None
    alternative_labels: Annotated[None | list[str], Field(exclude=True)] = None
    alternative_prefixes: Annotated[None | list[str], Field(exclude=True)] = None


class Revision(MhdConfigModel):
    revision: Annotated[int, Field()]
    revision_datetime: datetime.datetime
    comment: str


class BaseMhdDataset(MhdConfigModel):
    mhd_identifier: Annotated[None | str, Field()] = None
    revision: Annotated[None | int, Field()] = None
    revision_comment: Annotated[None | str, Field()] = None
    revision_datetime: Annotated[None | datetime.datetime, Field()] = None
    repository_name: Annotated[None | str, Field()] = None
    repository_identifier: Annotated[None | str, Field()] = None
    repository_revision: Annotated[None | int, Field()] = None
    repository_revision_comment: Annotated[None | str, Field()] = None
    repository_revision_datetime: Annotated[None | datetime.datetime, Field()] = None

    change_log: Annotated[
        None | list[Revision], Field(min_length=1, description="Revision")
    ] = None


class ProfileEnabledDataset(BaseMhdDataset):
    schema_name: Annotated[
        str, Field(alias="$schema", description="Schema name of the file")
    ]
    profile_uri: Annotated[str, Field(description="Validation Profiles")]


class CvEnabledDataset(ProfileEnabledDataset):
    cv_definitions: Annotated[list[CvDefinition], Field()] = []
