import json
import logging
import pathlib
import re
from typing import Any, Generic, TypeVar
from urllib.parse import quote

import bioregistry
import httpx2
from cachetools import TTLCache, cached
from pydantic import BaseModel, ConfigDict, field_validator
from pydantic.alias_generators import to_camel, to_pascal

from mhd_model.shared.cv_definitions import OTHER_COMMON_CV_DEFINITIONS
from mhd_model.shared.model import CvTerm
from mhd_model.shared.validation.definitions import ParentCvTerm

logger = logging.getLogger(__name__)

T = TypeVar("T")


class OlsBaseModel(BaseModel):
    """Base model class to convert python attributes to camel case"""

    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=to_camel,
        json_schema_serialization_defaults_required=True,
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


@cached(
    key=lambda url, params, headers, *args, **kwargs: (
        url,
        json.dumps(params, sort_keys=True),
        json.dumps(headers, sort_keys=True),
    ),
    cache=TTLCache(maxsize=2048, ttl=600),
)
def search_ols(
    url: str, params: dict, headers: dict, timeout: int = 10
) -> tuple[int, dict[str, Any]]:
    result = httpx2.get(url, params=params, headers=headers, timeout=timeout)
    if result.status_code in {200, 201}:
        return result.status_code, result.json()
    logger.warning(
        "Could not find CV term: %s %s",
        result.status_code,
        json.dumps(params, sort_keys=True),
    )
    return result.status_code, {}


class CvTermHelper:
    def __init__(self) -> None:
        self.cache: dict[str, None | dict[str, CvTerm]] = {}
        self.search_cache: dict[str, tuple[bool, str | None]] = {}
        self.cv_term_cache: dict[str, None | CvTerm] = {}

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
        self.get_children(
            parent.cv_term,
            children,
            parent.allow_only_leaf,
            parent.excluded_cv_terms,
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
        excluded_cv_accessions: None | list[str] = None,
    ) -> None:
        parent_uri = self.get_uri(cv_term)

        parent_uri_encoded = quote(quote(parent_uri, safe=[]))
        children_subpath = f"/ontologies/{cv_term.source.lower()}/classes/{parent_uri_encoded}/children"
        ols4_base_url = "https://www.ebi.ac.uk/ols4/api/v2"

        url = ols4_base_url + children_subpath
        page = 0
        finished = False
        headers = {"Accept": "application/json"}
        selected_terms: list[ChildrenSearchModel] = []
        while not finished:
            params = {"page": page, "size": 100}
            page += 1
            status_code, result_json = search_ols(url, params, headers, timeout=10)
            if not result_json:
                logger.warning(
                    "Could not find children CV Terms for %s - %s",
                    cv_term.accession,
                    cv_term.name,
                )
                break
            search = OlsSearchModel[ChildrenSearchModel].model_validate(result_json)
            selected_items = [x for x in search.elements if not x.is_obsolete]
            selected = []
            if excluded_cv_accessions:
                for x in selected_items:
                    for pattern in excluded_cv_accessions:
                        if not re.match(pattern, x):
                            selected.append(x)

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
        cv_definition = OTHER_COMMON_CV_DEFINITIONS.get(source.upper())
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
        if cv_term.accession and (
            cv_term.accession.startswith("http://")
            or cv_term.accession.startswith("https://")
        ):
            return cv_term.accession
        uri = None
        if cv_term and ":" in cv_term.accession:
            uri = self.get_uri_with_custom_convertor(cv_term)
            if not uri:
                prefix, identifier = cv_term.accession.split(":")
                uri = bioregistry.get_default_iri(prefix, identifier)
                if uri and isinstance(uri, str) and "iri=" in uri:
                    return uri.split("iri=")[-1]

        return uri or None

    def find_cv_term_with_accession(
        self, source: str, accession: str
    ) -> tuple[CvTerm, list[str]]:
        curi = accession
        if accession and (
            accession.startswith("http://") or accession.startswith("https://")
        ):
            curi = bioregistry.curie_from_iri(accession)

        params = {
            "q": curi.lower(),
            "ontology": source.lower(),
            "type": "class,property,individual",
            "exact": True,
            "format": "json",
            "start": 0,
            "rows": 1,
            "local": False,
            "obsoletes": False,
            "lang": "en",
        }

        params["queryFields"] = "obo_id,iri,short_form"
        params["fieldList"] = "iri,obo_id,label,short_form,ontology_prefix,synonym"
        children_subpath = "/search"
        ols4_base_url = "https://www.ebi.ac.uk/ols4/api"
        url = ols4_base_url + children_subpath

        headers = {"Accept": "application/json"}
        try:
            logger.debug("Searching %s", url)
            status_code, result_json = search_ols(url, params, headers, timeout=10)
            if status_code == 404:
                return None, []
            docs = result_json.get("response", {}).get("docs")
            if not docs:
                return None, []
            label = docs[0].get("label", "")
            synonym = docs[0].get("synonym", []) or []
            return CvTerm(
                accession=accession,
                name=label,
                source=source,
            ), synonym
        except Exception as ex:
            logger.exception(ex)
            return None, []

    def find_cv_term(
        self,
        source: str,
        accession_or_label: str,
        matched_accession: None | str = None,
        allow_synonym_search: bool = False,
    ) -> None | CvTerm:
        key = (source, accession_or_label, matched_accession, allow_synonym_search)
        if key in self.cv_term_cache and self.cv_term_cache[key]:
            return self.cv_term_cache[key]
        if not source or not accession_or_label:
            raise ValueError("Source and accession_or_label must be provided")
        search_by_accession = None
        is_accession_input = len(accession_or_label.split(":")) == 2
        if matched_accession:
            search_by_accession = matched_accession
        if not search_by_accession and is_accession_input:
            search_by_accession = accession_or_label

        if search_by_accession:
            term_result, synonym = self.find_cv_term_with_accession(
                source=source, accession=search_by_accession
            )
            if term_result:
                if is_accession_input:
                    if key not in self.cache or not self.cv_term_cache[key]:
                        self.cv_term_cache[key] = term_result
                    return term_result
                else:
                    if (
                        term_result.name.lower() == accession_or_label.lower()
                        or accession_or_label.lower() in {x.lower() for x in synonym}
                    ):
                        if key not in self.cv_term_cache or not self.cv_term_cache[key]:
                            self.cv_term_cache[key] = term_result
                        return term_result

        label = accession_or_label.strip().lower()
        params = {
            "q": label,
            "ontology": source.lower(),
            "type": "class,property,individual",
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
        if allow_synonym_search:
            params["queryFields"] = "obo_id,iri,label,short_form,synonym"
            params["fieldList"] = "iri,obo_id,label,short_form,ontology_prefix,synonym"
        else:
            params["queryFields"] = "obo_id,iri,label,short_form"
            params["fieldList"] = "iri,obo_id,label,short_form,ontology_prefix"

        children_subpath = "/search"
        ols4_base_url = "https://www.ebi.ac.uk/ols4/api"
        url = ols4_base_url + children_subpath

        headers = {"Accept": "application/json"}
        try:
            logger.debug("Searching %s", url)
            status_code, result_json = search_ols(url, params, headers, timeout=10)
            if status_code == 404:
                self.search_cache[key] = None
                return self.search_cache[key]
            docs = result_json.get("response", {}).get("docs")
            if docs:
                obo_id = docs[0].get("obo_id", "")
                iri = docs[0].get("iri", "")
                label = docs[0].get("label", "")
                # synonyms = docs[0].get("synonym", [])
                ontology_prefix = docs[0].get("ontology_prefix", "").lower()
                if ontology_prefix != source.lower():
                    logger.warning(
                        "CV Term %s not found in %s", accession_or_label, source
                    )
                    return None
                uppercase_source = source.upper()
                if obo_id == label:
                    result_source = uppercase_source
                else:
                    result_source = (
                        ontology_prefix.upper() or obo_id.split(":")[0].upper()
                    )
                    if obo_id.upper() == result_source.upper():
                        result_source = uppercase_source
                if ":" in obo_id:
                    result_accession = obo_id
                else:
                    result_accession = iri
                term = CvTerm(
                    accession=result_accession,
                    name=label,
                    source=result_source,
                )
                if key not in self.cv_term_cache or not self.cv_term_cache[key]:
                    self.cv_term_cache[key] = term
                return term
        except Exception as ex:
            logger.exception(str(ex))
            return None

    def check_cv_term(
        self,
        cv_term: CvTerm,
        parent_cv_term: None | ParentCvTerm = None,
        allow_synonym_search: bool = False,
    ) -> tuple[bool, str]:
        if not cv_term.accession or not cv_term.name or not cv_term.source:
            message = f"Invalid cv term [{cv_term.source}, {cv_term.accession}, {cv_term.name}]"
            logger.error(message)
            return False, message
        if not parent_cv_term or not parent_cv_term.cv_term:
            term = self.find_cv_term(
                cv_term.source,
                cv_term.accession,
                allow_synonym_search=allow_synonym_search,
            )
            if not term:
                return False, f"CV term {cv_term.accession} not found"
            return True, ""
        parent = parent_cv_term.cv_term if parent_cv_term else None

        if parent:
            if not parent.accession or not parent.name or not parent.source:
                message = f"Invalid cv term parent [{parent.source}, {parent.accession}, {parent.name}"
                logger.error(message)
                return False, message

        key = ",".join([str(cv_term), str(parent), str(allow_synonym_search)])

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

        # TODO: REMOVE after OLS service patch
        accession = cv_term.accession
        search_ontology = (cv_term.source or "").lower()
        params = {
            "q": accession.lower(),
            "type": "class,property,individual",
            "exact": True,
            "start": 0,
            "obsoletes": False,
            "rows": 1,
            # "local": False,
            "format": "json",
            "lang": "en",
            # "isLeaf": (
            #     True if parent_cv_term and parent_cv_term.allow_only_leaf else False
            # ),
        }

        if allow_synonym_search:
            params["queryFields"] = "obo_id,short_form,iri,synonym"
            params["fieldList"] = "iri,obo_id,label,short_form,ontology_prefix,synonym"
        else:
            params["queryFields"] = "obo_id,short_form,iri"
            params["fieldList"] = "iri,obo_id,label,short_form,ontology_prefix"
        if search_ontology:
            params["ontology"] = search_ontology

        ols4_base_url = "https://www.ebi.ac.uk/ols4/api"
        url = ols4_base_url + children_subpath
        parent_uri = self.get_uri(parent_cv_term.cv_term)
        params["allChildrenOf"] = parent_uri
        logger.debug(
            "%s: %s in cv %s, parent %s",
            url,
            accession,
            cv_term.source,
            parent_uri,
        )

        headers = {"Accept": "application/json"}
        try:
            logger.debug("Searching %s", url)
            status_code, result_json = search_ols(url, params, headers, timeout=10)
            if status_code == 404:
                self.search_cache[key] = (
                    False,
                    f"{cv_term.source} is not valid or {accession} is not in ontology {cv_term.source}",
                )
                return self.search_cache[key]
            docs = result_json.get("response", {}).get("docs")
            if docs:
                obo_id = docs[0].get("obo_id", "")
                iri_id = docs[0].get("iri", "")
                synonyms = docs[0].get("synonym", []) or []
                synonyms_lower_set = {s.lower() for s in synonyms}
                if accession.lower() in {obo_id.lower(), iri_id.lower()} and (
                    docs[0].get("label", "").lower() == cv_term.name.lower()
                    or (
                        allow_synonym_search
                        and cv_term.name.lower() in synonyms_lower_set
                    )
                ):
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
                            accession,
                            cv_term.name,
                        )
                    self.search_cache[key] = (True, None)
                    return self.search_cache[key]
                if not parent_cv_term:
                    self.search_cache[key] = (
                        False,
                        f"'{cv_term.source}' is not valid source or [{cv_term.source}, {accession}, {cv_term.name}] is not found in {cv_term.source} ontology",
                    )
                else:
                    self.search_cache[key] = (
                        False,
                        f"{cv_term.name} {accession} is not child of {parent.accession} on source {parent.source}. ",
                    )
                return self.search_cache[key]

            else:
                self.search_cache[key] = (False, f"{accession} does not match")
                return self.search_cache[key]

        except httpx2.HTTPStatusError as ex:
            return False, f"{accession} search failed: {str(ex)}"
        except Exception as ex:
            return (
                False,
                f"{accession} is not in {cv_term.source} ontology. {str(ex)}",
            )
