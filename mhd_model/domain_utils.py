import hashlib
import json
import logging
from functools import lru_cache
from importlib import resources
from pathlib import Path
from typing import Annotated
from urllib.parse import quote

from pydantic import BaseModel, Field

from mhd_model.shared.base import CvTerm, CvTermValue
from mhd_model.shared.model import IdentifiableMhdModel

logger = logging.getLogger(__name__)

COMMON_FILE_HASH_ALGORITHMS = {
    "sha256": CvTerm(source="MS", accession="MS:1003151", name="SHA-256"),
    "md5": CvTerm(source="MS", accession="MS:1000568", name="MD5"),
}


def get_urn(
    urn_namespace: str,
    repository_short_name: None | str,
    dataset_id: str,
    node_class: type[IdentifiableMhdModel],
    identifier: None | str,
) -> str:
    prefix = str(node_class.model_fields.get("prefix").default)
    type_ = str(node_class.model_fields.get("type_").default)
    if not identifier:
        return f"urn:{urn_namespace}:{repository_short_name}:{dataset_id}:{prefix}:{type_}".lower()

    return f"urn:{urn_namespace}:{repository_short_name}:{dataset_id}:{prefix}:{type_}:{quote(identifier)}".lower()


def get_file_hashes(file: bytes | Path):
    file_bytes = file
    if isinstance(file, Path):
        file_bytes = file.read_bytes()

    mhd_metadata_file_hashes: list[CvTermValue] = []
    sha256 = COMMON_FILE_HASH_ALGORITHMS.get("sha256")
    md5 = COMMON_FILE_HASH_ALGORITHMS.get("md5")
    mhd_metadata_file_hashes.append(
        CvTermValue(
            source=sha256.source,
            accession=sha256.accession,
            name=sha256.name,
            value=hashlib.sha256(file_bytes).hexdigest(),
        )
    )
    mhd_metadata_file_hashes.append(
        CvTermValue(
            source=md5.source,
            accession=md5.accession,
            name=md5.name,
            value=hashlib.md5(file_bytes).hexdigest(),
        )
    )
    return mhd_metadata_file_hashes


class OntologySourceReferenceTemplate(BaseModel):
    name: Annotated[str, Field(description="Source name")]
    file: Annotated[str, Field(description="Source file")]
    version: Annotated[str, Field(description="Source version")]
    description: Annotated[str, Field(description="Source full name")]
    details: Annotated[str, Field(description="Source details")] = ""
    prefix: Annotated[str, Field(description="Source prefix")]


class OntologySourceReference(BaseModel):
    ontologies: list[OntologySourceReferenceTemplate] = []


@lru_cache
def get_ontology_sources() -> dict[str, OntologySourceReferenceTemplate]:
    with resources.open_text("mhd_model.shared", "ontology_sources.json") as file:
        data = json.load(file)
        reference = OntologySourceReference.model_validate(data)
    return {x.name: x for x in reference.ontologies}
