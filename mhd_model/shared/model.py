import datetime
import decimal
import logging
import uuid
from typing import Annotated

from pydantic import AnyUrl, BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_pascal

from mhd_model.shared.fields import DOI

logger = logging.getLogger(__name__)


class MhdConfigModel: ...


def generate_id_from_property(
    source: MhdConfigModel,
    prefix: str,
    type_: str,
    property_name: str = "repository_identifier",
) -> str:

    value = ""
    if hasattr(source, property_name):
        value = getattr(source, property_name) or ""
        if isinstance(value, list) and value:
            value = value[0]
        if not isinstance(
            value,
            (str, int, AnyUrl, CvTerm, CvTermValue),
        ):
            raise ValueError(
                f"{source.__class__} {property_name} value '{value.__class__}' "
                "is not valid to create unique id."
            )

        if isinstance(value, (CvTerm, CvTermValue)):
            value = value.get_unique_id()
        else:
            value = str(value)
        value = value.lower().strip()
    else:
        raise ValueError(f"{source.__class__} has no field named {property_name}")

    if value:
        return f"prefix={prefix}&type={type_}&{property_name}={value.lower().strip()}"

    raise ValueError(f"{source.__class__} {property_name} value is not defined")


def generate_unique_id(
    source: BaseModel,
    prefix: None | str,
    type_: None | str,
    contribution: None | list[tuple[str, ...]] = None,
    unique_value_contribution_field: None | str = "unique_value_contribution",
) -> str:
    if not contribution:
        extra = source.__class__.model_config.get("json_schema_extra", {})
        contribution: list[tuple[str, ...]] = (
            extra.get(unique_value_contribution_field) or []
        )
    field_names_list = []
    new_list = None
    for x in contribution:
        if isinstance(x, str):
            if new_list is None:
                new_list = []
            new_list.append(x)
        elif isinstance(x, (tuple, list)):
            new_list = None
            if new_list:
                field_names_list.append(new_list)
            field_names_list.append(x)
    if new_list:
        field_names_list.append(new_list)

    for field_names in contribution:
        values = []
        if isinstance(field_names, str):
            field_names = [field_names]
        for field_name in field_names:
            value = ""
            if hasattr(source, field_name):
                value = getattr(source, field_name) or ""
                if isinstance(value, list) and value:
                    # Use first item in list
                    value = value[0]
                if not isinstance(
                    value,
                    (str, int, AnyUrl, CvTerm, CvTermValue),
                ):
                    raise ValueError(
                        f"{source.__class__} {field_name} value '{value.__class__}' is not valid to create unique id."
                    )

                if isinstance(value, (CvTerm, CvTermValue)):
                    value = value.get_unique_id()
                else:
                    value = str(value)
            else:
                raise ValueError(f"{source.__class__} has no field named {field_name}")
            values.append((field_name.lower().strip(), value.lower().strip()))
        non_empty_values = [x[1] for x in values if x[1]]
        if non_empty_values:
            values = []
            if prefix:
                values.append(("prefix", prefix))
            if type_:
                values.append(("type", prefix))
            values.extend(non_empty_values)
            return "&".join([f"{x[0]}={x[1]}" for x in values])

    raise ValueError(f"{source.__class__} has no valid values to create unique id")


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

    def get_unique_id(self, namespace: str, prefix: str, type_: str):
        if not type_:
            raise ValueError("type is not defined to create unique id")
        identifier_name = generate_id_from_property(
            source=self, prefix=prefix, type_=type_
        )
        identifier = str(uuid.uuid5(namespace, name=identifier_name))
        return f"{prefix}--{type_}--{identifier}"


class CvTerm(MhdConfigModel):
    model_config = ConfigDict(
        json_schema_extra={
            "unique_value_contribution": [
                (
                    "source",
                    "accession",
                    "name",
                )
            ]
        }
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

    def get_unique_id(self):
        return generate_unique_id(source=self, prefix=None, type_=None)


class UnitCvTerm(CvTerm): ...


class QuantitativeValue(MhdConfigModel):
    value: None | str | int | float | decimal.Decimal = None
    unit: None | UnitCvTerm = None


class CvTermValue(CvTerm, QuantitativeValue):
    model_config = ConfigDict(
        json_schema_extra={
            "unique_value_contribution": [
                (
                    "source",
                    "accession",
                    "name",
                    "value",
                    "unit",
                ),
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

    def get_unique_id(self):
        return generate_unique_id(source=self, prefix=None, type_=None)


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
    model_config = ConfigDict(
        json_schema_extra={
            "unique_value_contribution": [
                ("doi",),
                ("mhd_identifier",),
                (
                    "repository_name",
                    "repository_identifier",
                ),
                ("additional_identifier_list",),
            ],
        }
    )
    mhd_identifier: Annotated[None | str, Field()] = None
    doi: Annotated[
        None | DOI,
        Field(description="Digital Object Identifier (DOI) for the dataset."),
    ] = None
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
