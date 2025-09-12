import logging

import httpx

from mhd_model.model.v0_1.dataset.validation.validator import MhdFileValidator
from mhd_model.shared.model import CvDefinition
from mhd_model.utils import json_path, load_json

logger = logging.getLogger(__name__)


def validate_mhd_file(file_path: str):
    json_data = load_json(file_path)

    mhd_validator = MhdFileValidator()
    errors = mhd_validator.validate(json_data)

    messages = set()
    validation_errors = []
    for x in errors:
        if x.message in messages:
            continue
        messages.add(x.message)
        validation_errors.append((json_path(x.absolute_path), x))
    validation_errors.sort(key=lambda x: x[0])
    return validation_errors


def search_ontology_definition(ontology_name: str) -> None | CvDefinition:
    if not ontology_name:
        return None
    try:
        url = "https://www.ebi.ac.uk/ols4/api/v2/ontologies" + ontology_name.lower()
        response = httpx.get(url, timeout=2)
        response.raise_for_status()
        json_response = response.json()
        base_uri = json_response.get("baseUri", [])

        return CvDefinition(
            name=json_response.get("description", ""),
            uri=json_response.get("iri", ""),
            prefix=base_uri[0] if base_uri else "",
            label=json_response.get("preferredPrefix", "").upper(),
        )
    except Exception as e:
        logger.error(
            "Error while fetching ontology definition from OLS: '%s' - %s",
            ontology_name,
            e,
        )
        return None
