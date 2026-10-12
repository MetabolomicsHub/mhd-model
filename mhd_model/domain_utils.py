import hashlib
import json
import logging
import uuid
from functools import lru_cache
from importlib import resources
from pathlib import Path
from typing import Annotated

from pydantic import BaseModel, Field

from mhd_model.model.v1_0.rules.managed_cv_terms import COMMON_FILE_HASH_ALGORITHMS
from mhd_model.shared.base import NAMESPACE_VALUE, CvTermValue
from mhd_model.shared.model import IdentifiableMhdModel
from mhd_model.urn_utils import check_rfc8141_nid, to_rfc8141_nss

logger = logging.getLogger(__name__)


def generate_id_from_urn(urn: str, namespace: None | str = None) -> str:
    parts = urn.split(":", maxsplit=6)
    if len(parts) < 6:
        raise TypeError(f"URN format is not valid. {urn}")
    prefix = parts[4]
    type_ = parts[5]
    if not namespace:
        namespace = str(NAMESPACE_VALUE)

    name = f"prefix={prefix}&type={type_}&uri={urn}"
    identifier = str(uuid.uuid5(namespace, name=name))
    return f"{prefix}:{type_}:{identifier}"


def generate_urn(
    urn_namespace: str,
    repository_short_name: None | str,
    dataset_id: str,
    prefix: str,
    type_: str,
    identifier: None | str,
) -> str:
    repo = repository_short_name or ""

    if not identifier:
        nss = to_rfc8141_nss(f"{repo}:{dataset_id}:{prefix}:{type_}")
    else:
        nss = to_rfc8141_nss(f"{repo}:{dataset_id}:{prefix}:{type_}:{identifier}")
    return f"urn:{urn_namespace}:{nss}".lower()


def get_urn(
    urn_namespace: str,
    repository_short_name: None | str,
    dataset_id: str,
    node_class: type[IdentifiableMhdModel],
    identifier: None | str,
) -> str:
    prefix = str(node_class.model_fields.get("prefix").default)
    type_ = str(node_class.model_fields.get("type_").default)
    repo = repository_short_name or ""
    if not check_rfc8141_nid(urn_namespace):
        raise TypeError(f"{urn_namespace} is not valid")
    if not identifier:
        nss = to_rfc8141_nss(f"{repo}:{dataset_id}:{prefix}:{type_}")
    else:
        nss = to_rfc8141_nss(f"{repo}:{dataset_id}:{prefix}:{type_}:{identifier}")
    return f"urn:{urn_namespace}:{nss}".lower()


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
    version: Annotated[str, Field(description="Source version")] = ""
    description: Annotated[str, Field(description="Source full name")] = ""
    details: Annotated[str, Field(description="Source details")] = ""
    prefix: Annotated[str, Field(description="Source prefix")] = ""


class OntologySourceReference(BaseModel):
    ontologies: list[OntologySourceReferenceTemplate] = []


@lru_cache
def get_ontology_sources() -> dict[str, OntologySourceReferenceTemplate]:
    with resources.open_text("mhd_model.shared", "ontology_sources.json") as file:
        data = json.load(file)
        reference = OntologySourceReference.model_validate(data)
    return {x.name: x for x in reference.ontologies}
