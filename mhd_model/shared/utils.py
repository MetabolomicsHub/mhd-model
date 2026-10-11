import logging

import httpx2
from pydantic import AnyUrl, BaseModel

from mhd_model.shared.base import CvDefinition, CvTerm, CvTermValue

logger = logging.getLogger(__name__)


def search_ontology_definition(ontology_name: str) -> None | CvDefinition:
    if not ontology_name:
        return None
    try:
        url = "https://www.ebi.ac.uk/ols4/api/v2/ontologies/" + ontology_name.lower()
        response = httpx2.get(url, timeout=2)
        response.raise_for_status()
        json_response = response.json()
        base_uri = json_response.get("baseUris", [])

        return CvDefinition(
            name=json_response.get("label", [""])[0] or json_response.get("title"),
            uri=json_response.get("versionIri")
            or json_response.get("iri")
            or json_response.get("ontologyIri", None),
            prefix=base_uri[0] if base_uri else None,
            label=json_response.get("preferredPrefix", "").upper()
            or json_response.get("ontologyId", "").upper()
            or None,
        )
    except Exception as e:
        logger.error(
            "Error while fetching ontology definition from OLS: '%s' - %s",
            ontology_name,
            e,
        )
        return None


def generate_unique_id(
    source: BaseModel,
    prefix: None | str,
    type_: None | str,
    contribution: None | list[tuple[str, ...]] = None,
    unique_value_contribution_field: None | str = "unique_value_alternatives",
    calculate_all: bool = False,
) -> None | str | list[str]:
    all_identifiers: list[str] = []
    if not contribution:
        extra = source.__class__.model_config.get("json_schema_extra", {})
        contribution: list[tuple[str, ...]] = (
            extra.get(unique_value_contribution_field) or []
        )
    elif isinstance(contribution, tuple):
        contribution = [contribution]

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

    for field_names in field_names_list:
        values = []
        if isinstance(field_names, str):
            field_names = [field_names]
        for field_name in field_names:
            value = ""
            if hasattr(source, field_name):
                field_value = getattr(source, field_name) or ""
                value_list = field_value
                if not isinstance(field_value, (list, tuple)):
                    # Use first item in list
                    value_list = [field_value]
                for value in value_list:
                    if not isinstance(
                        value,
                        (str, int, AnyUrl, CvTerm, CvTermValue),
                    ):
                        raise ValueError(
                            f"{source.__class__} {field_name} value '{value.__class__}' is not valid to create unique id."
                        )

                    if isinstance(value, (CvTerm, CvTermValue)):
                        value = value.get_as_string()
                    else:
                        value = str(value)
                    values.append((field_name.lower().strip(), value.lower().strip()))
            else:
                raise ValueError(f"{source.__class__} has no field named {field_name}")

        non_empty_values = [x[1] for x in values if x[1]]
        if non_empty_values:
            new_values = []
            if prefix:
                new_values.append(("prefix", prefix.lower().strip()))
            if type_:
                new_values.append(("type", type_.lower().strip()))
            new_values.extend(values)
            identifier = "&".join([f"{x[0]}:{x[1]}" for x in new_values])
            if not calculate_all:
                return identifier
            else:
                all_identifiers.append(identifier)
    if not calculate_all:
        raise ValueError(f"{source.__class__} has no valid values to create unique id")
    return all_identifiers or None
