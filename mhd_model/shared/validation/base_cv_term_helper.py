import abc
import logging

from build.lib.mhd_model.shared.model import CvDefinition
from mhd_model.shared.base import BaseParentCvTerm, CvTerm

logger = logging.getLogger(__name__)


class BaseCvTermHelper(abc.ABC):
    @abc.abstractmethod
    def check_cv_term(
        self,
        cv_term: CvTerm,
        parent_cv_term: None | BaseParentCvTerm = None,
        allow_synonym_search: bool = False,
        allow_obsoletes: bool = True,
    ) -> tuple[bool, str]: ...

    @abc.abstractmethod
    def get_ontology_definition(self, ontology_name: str) -> None | CvDefinition: ...

    @abc.abstractmethod
    def get_uri(self, cv_term: CvTerm) -> str | None: ...

    @abc.abstractmethod
    def get_curie(self, cv_term: CvTerm) -> str | None: ...

    @abc.abstractmethod
    def find_cv_term(
        self,
        source: str,
        accession_or_label: str,
        matched_accession: None | str = None,
        allow_synonym_search: bool = False,
        allow_obsoletes: bool = True,
    ) -> None | CvTerm: ...

    @abc.abstractmethod
    def find_cv_term_with_accession(
        self,
        source: str,
        accession: str,
        allow_obsoletes: bool = True,
    ) -> tuple[CvTerm, list[str]]: ...
