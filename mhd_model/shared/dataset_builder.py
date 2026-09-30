import logging
from collections.abc import Sequence
from typing import Annotated, Any, Generic, Self, TypeVar

from pydantic import Field

from mhd_model.domain_utils import get_ontology_sources
from mhd_model.shared.cv_definitions import (
    COMMON_CV_DEFINITIONS,
    OTHER_COMMON_CV_DEFINITIONS,
)
from mhd_model.shared.model import (
    BaseCvTermModel,
    BaseCvTermValueModel,
    BaseMhDatasetProfile,
    BaseRelationshipModel,
    CvDefinition,
    CvTerm,
    CvTermValue,
    IdentifiableMhdModel,
    MhdNode,
)
from mhd_model.shared.utils import search_ontology_definition
from mhd_model.shared.validation.cv_term_helper import CvTermHelper

logger = logging.getLogger(__name__)

_cv_helper: CvTermHelper | None = None


def _get_cv_helper() -> CvTermHelper:
    global _cv_helper
    if _cv_helper is None:
        _cv_helper = CvTermHelper()
    return _cv_helper


T = TypeVar("T", bound=BaseMhDatasetProfile)


class MhDatasetBuilder(Generic[T]):
    def __init__(self, dataset: T, **kwargs):
        self.kwargs = kwargs
        self.dataset = dataset

        self._cv_definitions_map: Annotated[
            dict[str, None | CvDefinition], Field(exclude=True)
        ] = {}
        self._links: Annotated[set[tuple[str, str, str]], Field(exclude=True)] = set()
        # created_at: Annotated[datetime.datetime | None, Field(description="Created at")] = (
        #     None
        # )
        # name: Annotated[None | str, Field()] = None
        # description: Annotated[None | str, Field()] = None
        self.objects: dict[str, IdentifiableMhdModel] = {}

    def add(self, item: MhdNode, use_label_for_invalid_cv_term: bool = False) -> Self:
        return self.add_node(item, use_label_for_invalid_cv_term)

    def link(
        self,
        source: IdentifiableMhdModel,
        relationship_name: str,
        target: IdentifiableMhdModel,
        add_reverse_relationship: bool = False,
        reverse_relationship_name: None | str = None,
        source_role: None | str = None,
        target_role: None | str = None,
        relationship_type: None | str = None,
        **kwargs,
    ) -> Self:
        default_relation_type = (
            self.dataset.get_config().get_default_relationship_type()
        )
        relationship_class = self.dataset.get_config().get_relationship_type_class(
            type_=relationship_type or default_relation_type
        )
        if (source.id_, relationship_name, target.id_) not in self._links:
            data: dict[str, Any] = {
                "source_ref": source.id_,
                "relationship_name": relationship_name,
                "target_ref": target.id_,
                "source_role": source_role,
                "target_role": target_role,
            }
            data.update(**kwargs)
            link = relationship_class.model_validate(data)
            self._links.add((source.id_, relationship_name, target.id_))
            self.objects[link.id_] = link
        if target.id_ != source.id_ and (
            add_reverse_relationship or reverse_relationship_name
        ):
            reverse_relationship_name = (
                reverse_relationship_name
                if reverse_relationship_name
                else relationship_name
            )
            if (target.id_, reverse_relationship_name, source.id_) not in self._links:
                data: dict[str, Any] = {
                    "source_ref": target.id_,
                    "relationship_name": reverse_relationship_name,
                    "target_ref": source.id_,
                    "source_role": target_role,
                    "target_role": source_role,
                }
                data.update(**kwargs)
                link = relationship_class.model_validate(data)
                self.objects[link.id_] = link
        return self

    def add_node(
        self, item: MhdNode, use_label_for_invalid_cv_term: bool = False
    ) -> Self:
        if (
            use_label_for_invalid_cv_term
            and item
            and isinstance(item, (CvTerm, CvTermValue))
            and item.name
        ):
            if item.source:
                item.source = item.source.upper()
                if not item.accession:
                    term = _get_cv_helper().find_cv_term(
                        item.source, item.name, allow_synonym_search=False
                    )
                    if term and term.name == item.name:
                        item.name = term.name
                        item.accession = term.accession.replace(
                            term.source, term.source.upper()
                        )
                        item.source = term.source.upper()
                    else:
                        item.name = term.name
                        item.accession = ""
                        item.source = ""
                else:
                    term = _get_cv_helper().find_cv_term(
                        item.source,
                        item.name,
                        matched_accession=item.accession,
                        allow_synonym_search=True,
                    )
                    if term:
                        item.name = term.name
                        item.accession = term.accession.replace(
                            term.source, term.source.upper()
                        )
                        item.source = term.source.upper()
                    else:
                        logger.warning(
                            "Could not find CV term for %s, %s, %s. Keeping the provided label as name.",
                            item.name,
                            item.source,
                            item.accession,
                        )
                        item.source = ""
                        item.accession = ""

            else:
                item.source = ""
                item.accession = ""
        if item and isinstance(item, IdentifiableMhdModel) and item.id_:
            self.objects[item.id_] = item

            self.add_cv_source(item)
        else:
            logger.warning("Item %s is not valid. It will not be added.", item)
        return self

    def add_cv_source(self, item: Any) -> Self:
        if isinstance(item, (CvTerm, CvTermValue)):
            source_uppercase = item.source.upper() if item.source else ""
            if not source_uppercase:
                return self
            if source_uppercase not in self._cv_definitions_map:
                logger.debug("%s CV source is added.", source_uppercase)
                self._cv_definitions_map[source_uppercase] = None
        return self

    def add_relationship(self, item: BaseRelationshipModel) -> Self:
        self.objects[item.id_] = item
        return self

    def build_dataset(self, start_item_refs: Sequence[str]) -> BaseMhDatasetProfile:
        cv_definitions_map: dict[str, CvDefinition] = {}
        cv_definitions: list[CvDefinition] = []
        sources = get_ontology_sources()
        for source in self._cv_definitions_map:
            if not source:
                continue

            if source in COMMON_CV_DEFINITIONS:
                cv_definition = COMMON_CV_DEFINITIONS[source]
                cv_definitions.append(cv_definition)
                cv_definitions_map[source] = cv_definition
            elif source in OTHER_COMMON_CV_DEFINITIONS:
                cv_definition = OTHER_COMMON_CV_DEFINITIONS[source]
                cv_definitions.append(cv_definition)
                cv_definitions_map[source] = cv_definition
            elif source in sources:
                ref = sources[source]
                definition = CvDefinition(
                    label=ref.name,
                    name=ref.description,
                    uri=ref.file,
                    version=ref.version or None,
                    prefix=ref.prefix,
                )
                cv_definitions.append(definition)
                cv_definitions_map[source] = definition
            else:
                cv_definition = search_ontology_definition(source)
                if not cv_definition:
                    cv_definitions.append(CvDefinition(label=source))
                else:
                    cv_definitions.append(cv_definition)
                cv_definitions_map[source] = cv_definition

        cv_definitions.sort(key=lambda x: x.label)
        self.dataset.cv_definitions = cv_definitions
        # mhd_dataset = dataset_class(
        #     schema_name=self.schema_name,
        #     profile_uri=self.profile_uri,
        #     repository_name=self.repository_name or None,
        #     repository_identifier=self.repository_identifier or None,
        #     mhd_identifier=self.mhd_identifier or None,
        #     doi=self.doi or None,
        # )
        # mhd_dataset = self.dataset
        # mhd_dataset.cv_definitions = (
        #     self.cv_definitions.copy() if self.cv_definitions else []
        # )

        # mhd_dataset.name = self.name or None
        # mhd_dataset.description = self.description or None
        # mhd_dataset.created_at = self.created_at or datetime.datetime.now(datetime.UTC)

        # mhd_dataset.repository_name = self.repository_name or None
        # mhd_dataset.revision = self.revision or None
        # mhd_dataset.repository_identifier = self.repository_identifier or None
        # mhd_dataset.mhd_identifier = self.mhd_identifier or None
        # mhd_dataset.repository_revision = self.repository_revision or None
        # mhd_dataset.repository_revision_datetime = (
        #     self.repository_revision_datetime or None
        # )
        # mhd_dataset.repository_revision_comment = (
        #     self.repository_revision_comment or None
        # )
        # mhd_dataset.change_log = self.change_log.copy() if self.change_log else None
        self.dataset.graph.relationships = []
        self.dataset.graph.nodes = []
        iterated_items: set[str] = set()
        for identifier, item in self.objects.items():
            if identifier not in iterated_items:
                iterated_items.add(identifier)
                if identifier in start_item_refs:
                    self.dataset.graph.start_item_refs.append(identifier)
                if isinstance(item, BaseRelationshipModel):
                    self.dataset.graph.relationships.append(item)
                else:
                    self.dataset.graph.nodes.append(item)

        def sort_key(item: MhdNode):
            if isinstance(item, BaseCvTermValueModel):
                return (200, item.type_, item.label, item.id_)
            if isinstance(item, BaseCvTermModel):
                return (100, item.type_, item.label, item.id_)
            if item.id_ in start_item_refs:
                return (0, item.type_, item.label, item.id_)
            if isinstance(item, BaseRelationshipModel):
                return (
                    0,
                    item.source_ref,
                    item.relationship_name,
                    item.target_ref,
                    item.source_role,
                    item.target_role,
                    item.id_,
                )
            if item.id_.startswith("cv-"):
                return (100, item.type_, item.label, item.id_)
            return (10, item.type_, item.label, item.id_)

        self.dataset.graph.nodes = sorted(self.dataset.graph.nodes, key=sort_key)
        self.dataset.graph.relationships.sort(key=sort_key)
        return self.dataset

    @classmethod
    def from_dataset(cls, mhd_dataset: BaseMhDatasetProfile) -> "MhDatasetBuilder":
        dataset = cls(dataset=mhd_dataset)
        # dataset.cv_definitions = (
        #     mhd_dataset.cv_definitions.copy() if mhd_dataset.cv_definitions else []
        # )
        # dataset.repository_name = mhd_dataset.repository_name
        # dataset.mhd_identifier = mhd_dataset.mhd_identifier
        # dataset.repository_identifier = mhd_dataset.repository_identifier
        # dataset.revision = mhd_dataset.revision
        # dataset.revision_datetime = mhd_dataset.revision_datetime
        # dataset.repository_revision = mhd_dataset.repository_revision
        # dataset.repository_revision_datetime = mhd_dataset.repository_revision_datetime
        # dataset.change_log = (
        #     mhd_dataset.change_log.copy() if mhd_dataset.change_log else []
        # )

        for item in mhd_dataset.graph.nodes:
            dataset.objects[item.id_] = item
        for item in mhd_dataset.graph.relationships:
            dataset.objects[item.id_] = item
        return dataset
