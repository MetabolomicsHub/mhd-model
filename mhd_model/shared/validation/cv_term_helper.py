from __future__ import annotations

import json
import logging
import pathlib
from typing import Any, Generic, TypeVar
from urllib.parse import quote

import bioregistry
import httpx
from pydantic import BaseModel, ConfigDict, field_validator
from pydantic.alias_generators import to_camel, to_pascal

from mhd_model.model.v0_1.rules.cv_definitions import CONTROLLED_CV_DEFINITIONS
from mhd_model.shared.model import CvTerm
from mhd_model.shared.validation.definitions import ParentCvTerm

logger = logging.getLogger(__name__)

T = TypeVar("T")


class OlsBaseModel(BaseModel):
    """Base model class to convert python attributes to camel case"""

    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=to_camel,
        JSON_schema_serialization_defaults_required=True,
        field_title_generator=lambda field_name, field_info: to_pascal(
            field_name.replace("_", " ").strip()
        ),
    )


class OlsSearchModel(OlsBaseModel, Generic[T]):
    page: int
    num_elements: int
    total_pages: int
    total_elements: int
    elements: list[T]


class ChildrenSearchModel(OlsBaseModel):
    curie: str
    has_hierarchical_children: bool
    has_direct_children: bool
    iri: str
    is_obsolete: bool
    label: str
    ontology_preferred_prefix: str

    @field_validator("label", mode="before")
    @classmethod
    def label_validator(cls, value: list[str] | Any | None) -> str:
        if value is None:
            return ""
        if isinstance(value, list):
            return value[0] if value else ""
        return str(value)


class CvTermHelper:
    def __init__(self) -> None:
        self.cache: dict[str, None | dict[str, CvTerm]] = {}
        self.search_cache: dict[str, tuple[bool, str | None]] = {}

    def save_children(self, parent: ParentCvTerm, children: dict[str, CvTerm]) -> None:
        file_path = self.get_children_cache_file_path(parent)
        children_dict = {x: y.model_dump() for x, y in children.items()}
        with file_path.open("w") as f:
            f.write(
                json.dumps(
                    {
                        "parent": parent.model_dump(),
                        "children": children_dict,
                    },
                    indent=2,
                )
            )

    def get_children_cache_file_path(self, parent: ParentCvTerm) -> pathlib.Path:
        parent_path = pathlib.Path("cache")
        parent_path.mkdir(parents=True, exist_ok=True)
        parent_option = "p" if parent.allow_parent else "_"
        leaf_option = "l" if parent.allow_parent else "_"
        name_prefix = (
            parent.cv_term.accession.replace(":", "_") if parent.cv_term else ""
        )
        file_path = parent_path / pathlib.Path(
            f"{name_prefix}_children_{parent_option}_{leaf_option}.json"
        )
        return file_path

    def load_children(self, parent: ParentCvTerm) -> None | dict[str, CvTerm]:
        file_path = self.get_children_cache_file_path(parent)
        if file_path in self.cache:
            self.cache[file_path]
        if not file_path.exists():
            return None
        try:
            logger.debug(
                "Loading children CV Terms for %s - %s: %s",
                parent.cv_term.accession,
                parent.cv_term.name,
                file_path,
            )
            with file_path.open() as f:
                data = json.load(f)
            object_map = {
                x: CvTerm.model_validate(y) for x, y in data["children"].items()
            }
            # key = (parent.cv_term.source, parent.cv_term.accession)
            # if key not in self.cache:
            self.cache[file_path] = object_map
            logger.debug("Children CV Terms are loaded. %s", file_path)
            return object_map
        except Exception as ex:
            logger.exception(str(ex))
            return None

    def get_children_of_cv_term(self, parent: ParentCvTerm) -> dict[str, CvTerm]:
        file_path = self.get_children_cache_file_path(parent)
        if file_path in self.cache:
            return self.cache[file_path]

        children_map = self.load_children(parent)
        if children_map is not None:
            return children_map

        children: list[ChildrenSearchModel] = []
        if parent.allow_parent:
            uri = self.get_uri(parent.cv_term)
            children.append(
                ChildrenSearchModel(
                    curie=parent.cv_term.accession,
                    has_direct_children=True,
                    has_hierarchical_children=True,
                    iri=uri,
                    label=parent.cv_term.name,
                    ontology_preferred_prefix=parent.cv_term.source,
                    is_obsolete=False,
                )
            )
        excluded_cv_accessions = set()
        if parent.excluded_cv_terms:
            excluded_cv_accessions = {x.accession for x in parent.excluded_cv_terms}
        self.get_children(
            parent.cv_term,
            children,
            parent.allow_only_leaf,
            excluded_cv_accessions,
        )
        children.sort(key=lambda x: x.label)
        children_cv_terms = {
            x.curie: CvTerm(
                accession=x.curie, source=x.ontology_preferred_prefix, name=x.label
            )
            for x in children
        }
        self.cache[file_path] = children_cv_terms
        self.save_children(parent, children_cv_terms)
        return children_cv_terms

    def get_children(
        self,
        cv_term: CvTerm,
        children: list[ChildrenSearchModel],
        allow_only_leaf: bool = True,
        excluded_cv_accessions: None | set[str] = None,
    ) -> None:
        parent_uri = self.get_uri(cv_term)

        parent_uri_encoded = quote(quote(parent_uri, safe=[]))
        children_subpath = f"/ontologies/{cv_term.source.lower()}/classes/{parent_uri_encoded}/children"
        ols4_base_url = "https://www.ebi.ac.uk/ols4/api/v2"

        url = ols4_base_url + children_subpath
        page = 0
        finished = False
        headers = {"Accept": "application/json"}
        selected_terms = []
        while not finished:
            params = {"page": page, "size": 100}
            page += 1
            result = httpx.get(url, params=params, headers=headers, timeout=10)
            result_json = result.json()
            search = OlsSearchModel[ChildrenSearchModel].model_validate(result_json)
            if not excluded_cv_accessions:
                excluded_cv_accessions = set()
            selected = [
                x
                for x in search.elements
                if not x.is_obsolete and x.curie not in excluded_cv_accessions
            ]
            if selected:
                selected_terms.extend(selected)
            if page >= search.total_pages:
                finished = True
        for term in selected_terms:
            if not allow_only_leaf or (
                allow_only_leaf and not term.has_hierarchical_children
            ):
                children.append(term)

            if term.has_hierarchical_children:
                self.get_children(
                    cv_term=CvTerm(
                        accession=term.curie,
                        name=term.label,
                        source=term.ontology_preferred_prefix,
                    ),
                    children=children,
                    allow_only_leaf=allow_only_leaf,
                    excluded_cv_accessions=excluded_cv_accessions,
                )

    def get_uri_with_custom_convertor(self, cv_term: CvTerm) -> None | str:
        source = cv_term.source
        cv_definition = CONTROLLED_CV_DEFINITIONS.get(source)
        parent_uri = None
        accession = cv_term.source

        if cv_definition:
            accession = cv_term.accession
            if not accession:
                return ""
            if accession.startswith(cv_definition.prefix):
                parent_uri = accession
            elif ":" in accession:
                parent_uri = cv_definition.prefix + accession.split(":")[1]
            else:
                parent_uri = cv_definition.prefix + accession
        else:
            return None
        return parent_uri
        # search.page

    def get_uri(self, cv_term: CvTerm) -> str | None:
        uri = None
        if cv_term and ":" in cv_term.accession:
            uri = self.get_uri_with_custom_convertor(cv_term)
            if not uri:
                prefix, identifier = cv_term.accession.split(":")
                uri = bioregistry.get_default_iri(prefix, identifier)
                if uri and "https://www.ebi.ac.uk/ols/ontologies/edam/terms?" in uri:
                    uri = None

        return uri

    def check_cv_term(
        self, cv_term: CvTerm, parent_cv_term: None | ParentCvTerm = None
    ) -> tuple[bool, str]:
        if not cv_term.accession or not cv_term.name or not cv_term.source:
            message = f"Invalid cv term [{cv_term.source}, {cv_term.accession}, {cv_term.name}]"
            logger.error(message)
            return False, message

        parent = parent_cv_term.cv_term if parent_cv_term else None

        if parent:
            if not parent.accession or not parent.name or not parent.source:
                message = f"Invalid cv term parent [{parent.source}, {parent.accession}, {parent.name}"
                logger.error(message)
                return False, message

        key = ",".join([str(cv_term), str(parent)])

        if key in self.search_cache:
            return self.search_cache[key]

        children_subpath = "/search"
        if parent_cv_term:
            logger.debug(
                "Check CV term %s - %s whether is child of %s %s",
                cv_term.accession,
                cv_term.name,
                parent_cv_term.cv_term.accession,
                parent_cv_term.cv_term.name,
            )
        else:
            logger.debug("Check CV term %s - %s", cv_term.accession, cv_term.name)
        params = {
            "q": cv_term.accession,
            "ontology": cv_term.source,
            "type": "class,property",
            "queryFields": "obo_id",
            "fieldList": "iri,obo_id,label,short_form",
            "exact": True,
            "format": "json",
            "start": 0,
            "rows": 1,
            "local": False,
            "obsoletes": False,
            "lang": "en",
            # "isLeaf": (
            #     True if parent_cv_term and parent_cv_term.allow_only_leaf else False
            # ),
        }
        ols4_base_url = "https://www.ebi.ac.uk/ols4/api"
        url = ols4_base_url + children_subpath
        if parent_cv_term:
            parent_uri = self.get_uri(parent_cv_term.cv_term)
            params["allChildrenOf"] = parent_uri
            logger.info(
                "%s: %s in cv %s, parent %s",
                url,
                cv_term.accession,
                cv_term.source,
                parent_uri,
            )
        else:
            logger.info("%s: %s in cv %s", url, cv_term.accession, cv_term.source)

        headers = {"Accept": "application/json"}
        try:
            logger.debug("Searching %s", url)
            result = httpx.get(url, params=params, headers=headers, timeout=10)
            if result.status_code == 404:
                self.search_cache[key] = (
                    False,
                    f"{cv_term.source} is not valid or {cv_term.accession} is not in ontology {cv_term.source}",
                )
                return self.search_cache[key]
            result.raise_for_status()
            result_json = result.json()
            if result_json.get("response"):
                docs = result_json.get("response").get("docs")
                if docs and docs[0]["obo_id"] == cv_term.accession:
                    if parent_cv_term:
                        logger.debug(
                            "CV term %s - %s is child of %s %s",
                            cv_term.accession,
                            cv_term.name,
                            (
                                parent_cv_term.cv_term.accession
                                if parent_cv_term
                                else None
                            ),
                            parent_cv_term.cv_term.name if parent_cv_term else None,
                        )
                    else:
                        logger.debug(
                            "CV term %s - %s is valid CV term",
                            cv_term.accession,
                            cv_term.name,
                        )
                    self.search_cache[key] = (True, None)
                    return self.search_cache[key]
                if not parent_cv_term:
                    self.search_cache[key] = (
                        False,
                        f"'{cv_term.source}' is not valid source or [{cv_term.source}, {cv_term.accession}, {cv_term.name}] is not found in {cv_term.source} ontology",
                    )
                else:
                    self.search_cache[key] = (
                        False,
                        f"{cv_term.name} {cv_term.accession} is not child of {parent.accession} on source {parent.source}. ",
                    )
                return self.search_cache[key]

            else:
                self.search_cache[key] = (False, f"{cv_term.accession} does not match")
                return self.search_cache[key]

        except httpx.HTTPStatusError as ex:
            return False, f"{cv_term.accession} search failed: {str(ex)}"
        except Exception as ex:
            return (
                False,
                f"{cv_term.accession} is not in {cv_term.source} ontology. {str(ex)}",
            )
