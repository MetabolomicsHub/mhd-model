import csv
import logging
from importlib import resources

from cachetools import TTLCache, cached

from mhd_model import cv_mapping
from mhd_model.shared.base import CvTerm
from mhd_model.validation import select_cv_term_helper

logger = logging.getLogger(__name__)

DEFAULT_GROUP_CV_MAPPING = {
    "organism part": ["BTO", "UBERON", "NCIT", "CHEBI"],
    "organism": ["NCBITAXON", "ENVO", "CHEBI"],
    "cell type": ["CL", "CLO"],
    "disease": ["MONDO", "MP", "SNOMED"],
    "mass spectrometer": ["MS"],
    "chromatography instrument": ["MS"],
    "ionization type": ["MS"],
    "chromatography separation": ["MS"],
    "inlet type": ["MS"],
    "acquisition polarity": ["MS"],
    "instrument class": ["MS"],
    "omics type": ["EDAM"],
}


class CvTermSuggestion:
    def __init__(
        self,
        ontology_lookup_file_path: None | str = None,
        group_cv_maps: None | dict[str, list[str]] = None,
    ):
        self.ontology_lookup_file_path = ontology_lookup_file_path
        self.cv_term_helper = select_cv_term_helper(ontology_lookup_file_path)
        self.group_cv_maps = group_cv_maps or DEFAULT_GROUP_CV_MAPPING

    @cached(cache=TTLCache(maxsize=4048, ttl=3600 * 24))
    def match_cv_term(
        self,
        cv_term: CvTerm,
        group: None | str = None,
        cv_list: None | list[str] = None,
        synonym_match: bool = True,
        allow_obsoletes: bool = True,
    ) -> CvTerm:
        return self.suggest_cv_term(
            cv_term=cv_term,
            group=group,
            cv_list=cv_list,
            synonym_match=synonym_match,
            allow_obsoletes=allow_obsoletes,
        )

    def suggest_cv_term(
        self,
        cv_term: CvTerm,
        group: None | str = None,
        cv_list: None | list[str] = None,
        synonym_match: bool = True,
        allow_obsoletes: bool = True,
    ) -> None | CvTerm:
        if not cv_term or not cv_term.name:
            return None
        if group and not cv_list:
            cv_list = self.group_cv_maps.get(group, []) or []
        name = cv_term.name
        source = cv_term.source
        accession = cv_term.accession
        if accession and accession.startswith(("http://", "https://")):
            accession = self.cv_term_helper.get_curie(cv_term=cv_term)

        if not source and accession:
            source = accession.split(":")[0] if ":" in accession else ""

        if not source or not accession:
            source = ""
            accession = ""
        search = None
        if accession and source:
            search, synonyms = self.cv_term_helper.find_cv_term_with_accession(
                source=source,
                accession=accession,
                allow_obsoletes=allow_obsoletes,
            )
            if (
                search
                and synonym_match
                and search.name.lower()
                != name.lower()
                not in {x.lower() for x in {x.lower() for x in synonyms or []}}
            ):
                search = None
                accession = ""

        if not search:
            search = self.cv_term_helper.find_cv_term(
                source=",".join(cv_list),
                accession_or_label=cv_term.name,
                allow_obsoletes=allow_obsoletes,
                allow_synonym_search=synonym_match,
            )

        if not search:
            search = self.cv_term_helper.find_cv_term(
                source=source,
                accession_or_label=cv_term.name,
                allow_obsoletes=allow_obsoletes,
                allow_synonym_search=synonym_match,
            )

        mappings, cv_term_transforms, cv_terms_map = get_cv_terms_mapping()
        mappings_values = (
            mappings.get(group.lower(), {}).get(name.lower()) if group else []
        )
        if not search and mappings_values:
            cv_set = (
                {a.lower(): idx for idx, a in enumerate(cv_list) or []}
                if cv_list
                else {}
            )
            if cv_list:
                filtered_list = list(
                    filter(lambda x: x.source.lower() in cv_set, mappings_values)
                )

                alternatives = list(
                    filter(
                        lambda x: (
                            x.accession.lower() in cv_term_transforms
                            and x.source.lower() not in cv_set
                        ),
                        mappings_values,
                    )
                )
            else:
                filtered_list = list(
                    filter(
                        lambda x: x.accession.lower() not in cv_term_transforms,
                        mappings_values,
                    )
                )

                alternatives = list(
                    filter(
                        lambda x: x.accession.lower() in cv_term_transforms,
                        mappings_values,
                    )
                )
            filtered_terms = {x.accession.lower() for x in filtered_list}
            for x in alternatives or []:
                key = cv_term_transforms[x.accession.lower()].lower()
                if key not in filtered_terms:
                    filtered_list.append(cv_terms_map[key])

            filtered_list.sort(key=lambda x: cv_set.get(x.source.lower(), 1000))
            for x in filtered_list:
                term_accession = x.accession

                if (
                    x.accession.lower() in cv_term_transforms
                    and x.source.lower() not in cv_set
                ):
                    term_accession = cv_term_transforms[x.accession.lower()]
                    converted = cv_terms_map.get(term_accession.lower())
                    if converted and (not cv_set or converted.source.lower() in cv_set):
                        search = converted
                        break
                else:
                    search = x
                    break
        result = None
        if search:
            transform = cv_term_transforms.get(search.accession.lower())
            if transform:
                result = cv_terms_map.get(transform.lower())
            else:
                result = search

        if result:
            if str(result) != str(cv_term):
                logger.info("%s is transformed to %s", cv_term, result)
        else:
            logger.info("%s does not match any ontology term", cv_term)
        return result


@cached(cache=TTLCache(maxsize=1, ttl=120))
def get_cv_terms_mapping() -> tuple[dict[str, dict[str, list[CvTerm]]], dict[str, str]]:
    return load_cv_terms_mapping()


def load_cv_terms_mapping() -> tuple[
    dict[str, dict[str, list[CvTerm]]], dict[str, str]
]:
    """loads MS ontology term mappings file"""
    with (
        resources.files(cv_mapping.__name__)
        .joinpath("cv_mapping_table.csv")
        .open("r", encoding="utf-8") as f
    ):
        cv_term_transforms: dict[str, str] = {}
        # MAP TO MHD common parameter/characteristic definition
        custom_definition_mappings = {
            "liquid chromatography instrument": "chromatography instrument",
            "gas chromatography instrument": "chromatography instrument",
            "mass spectrometry instrument": "mass spectrometer",
        }
        # Column names and their index in the cv_mappings.csv file.
        HEADERS = {
            "GROUP": 0,
            "REF_SOURCE": 1,
            "REF_ACCESSION": 2,
            "REF_TERM": 3,
            "ALTERNATIVE_NAMES": 4,
            "TARGET_CV_TERM": 5,
        }
        cv_terms_map = {}
        reader = csv.reader(f)
        term_mappings: dict[str, dict[str, list[CvTerm]]] = {}
        for idx, row in enumerate(reader):
            if idx == 0:
                continue

            accession = row[HEADERS["REF_ACCESSION"]]
            source = row[HEADERS["REF_SOURCE"]]
            term = row[HEADERS["REF_TERM"]]
            cv_names_set: set[str] = set()
            for x in ["ALTERNATIVE_NAMES", "REF_TERM"]:
                cv_names_set.update(
                    {
                        name.strip().lower()
                        for name in row[HEADERS[x]].split(";")
                        if name and name.strip()
                    }
                )
            target_cv_term = row[HEADERS["TARGET_CV_TERM"]] or None
            if target_cv_term:
                cv_term_transforms[accession.lower()] = target_cv_term
            instance = row[HEADERS["GROUP"]]
            if not cv_names_set or not term or not accession:
                continue
            if not instance:
                logger.warning(
                    "Term mapping file row %s with accession %s and term '%s' "
                    "does not have an instance value. Row will be ignored.",
                    idx + 1,
                    accession,
                    term,
                )
                continue
            definition = custom_definition_mappings.get(instance.lower()) or instance
            if definition not in term_mappings:
                term_mappings[definition] = {}
            for cv_name in cv_names_set:
                if cv_name.lower() not in term_mappings[definition]:
                    term_mappings[definition][cv_name.lower()] = []
                cv_term = CvTerm(
                    source=source,
                    accession=accession,
                    name=term,
                )
                cv_terms_map[cv_term.accession.lower()] = cv_term
                term_mappings[definition][cv_name.lower()].append(cv_term)
    return term_mappings, cv_term_transforms, cv_terms_map


if __name__ == "__main__":
    suggestion = CvTermSuggestion()
    suggestion.match_cv_term(
        CvTerm(source="", accession="BTO:10091", name="human"),
        group="organism",
        # cv_list=["BTO", "UBERON"],
    )
