import logging
from typing import Any, Self, Sequence

from pydantic import Field
from typing_extensions import Annotated

from mhd_model.model.v0_1.dataset.profiles.base.base import (
    BaseLabeledMhdModel,
    BaseMhdRelationship,
    IdentifiableMhdModel,
    MhdObjectType,
)
from mhd_model.model.v0_1.dataset.profiles.base.profile import (
    GraphEnabledBaseDataset,
    MhDatasetBaseProfile,
)
from mhd_model.model.v0_1.dataset.profiles.base.relationships import Relationship
from mhd_model.model.v0_1.dataset.validation.utils import search_ontology_definition
from mhd_model.model.v0_1.rules.cv_definitions import (
    CONTROLLED_CV_DEFINITIONS,
    OTHER_CONTROLLED_CV_DEFINITIONS,
)
from mhd_model.shared.model import CvDefinition, CvTerm, CvTermValue

logger = logging.getLogger(__name__)


class MhDatasetBuilder(GraphEnabledBaseDataset):
    _cv_definitions_map: Annotated[
        dict[str, None | CvDefinition], Field(exclude=True)
    ] = {}

    type_: Annotated[MhdObjectType, Field(frozen=True, alias="type")] = MhdObjectType(
        "dataset"
    )

    objects: dict[str, IdentifiableMhdModel] = {}

    def add(self, item: IdentifiableMhdModel) -> Self:
        return self.add_node(item)

    def link(
        self,
        source: IdentifiableMhdModel,
        relationship_name: str,
        target: IdentifiableMhdModel,
        add_reverse_relationship: bool = False,
        reverse_relationship_name: None | str = None,
    ) -> Self:
        link = Relationship(
            source_ref=source.id_,
            relationship_name=relationship_name,
            target_ref=target.id_,
        )
        self.objects[link.id_] = link
        if add_reverse_relationship or reverse_relationship_name:
            reverse_relationship_name = (
                reverse_relationship_name
                if reverse_relationship_name
                else relationship_name
            )
            link = Relationship(
                source_ref=target.id_,
                relationship_name=reverse_relationship_name,
                target_ref=source.id_,
            )
            self.objects[link.id_] = link
        return self

    def add_node(self, item: IdentifiableMhdModel) -> Self:
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
                logger.info("%s CV source is added.", item.source)
                self._cv_definitions_map[source_uppercase] = None
            if source_uppercase != item.source:
                logger.info(
                    "CV source '%s' is converted to uppercase '%s'. %s",
                    item.source,
                    source_uppercase,
                    item,
                )
                item.source = source_uppercase
        return self

    def add_relationship(self, item: BaseMhdRelationship) -> Self:
        self.objects[item.id_] = item
        return self

    def create_dataset(
        self, start_item_refs: Sequence[str], dataset_class: type[MhDatasetBaseProfile]
    ) -> MhDatasetBaseProfile:
        cv_definitions_map: dict[str, CvDefinition] = {}

        for source in self._cv_definitions_map.keys():
            if not source:
                continue
            if source in CONTROLLED_CV_DEFINITIONS:
                cv_definition = CONTROLLED_CV_DEFINITIONS[source]
                self.cv_definitions.append(cv_definition)
                cv_definitions_map[source] = cv_definition
            elif source in OTHER_CONTROLLED_CV_DEFINITIONS:
                cv_definition = OTHER_CONTROLLED_CV_DEFINITIONS[source]
                self.cv_definitions.append(cv_definition)
                cv_definitions_map[source] = cv_definition
            else:
                cv_definition = search_ontology_definition(source)
                if not cv_definition:
                    self.cv_definitions.append(CvDefinition(label=source))
                else:
                    self.cv_definitions.append(cv_definition)
                cv_definitions_map[source] = cv_definition

        self.cv_definitions.sort(key=lambda x: x.label)
        mhd_dataset = dataset_class(
            schema_name=self.schema_name, profile_uri=self.profile_uri
        )
        mhd_dataset.cv_definitions = (
            self.cv_definitions.copy() if self.cv_definitions else []
        )
        mhd_dataset.repository_name = self.repository_name
        mhd_dataset.revision = self.revision
        mhd_dataset.repository_identifier = self.repository_identifier
        mhd_dataset.mhd_identifier = self.mhd_identifier
        mhd_dataset.revision_datetime = self.revision_datetime
        mhd_dataset.repository_revision = self.repository_revision
        mhd_dataset.repository_revision_datetime = self.repository_revision_datetime
        mhd_dataset.change_log = self.change_log.copy() if self.change_log else None

        iterated_items: set[str] = set()
        for identifier, item in self.objects.items():
            if identifier not in iterated_items:
                iterated_items.add(identifier)
                if identifier in start_item_refs:
                    mhd_dataset.graph.start_item_refs.append(identifier)
                if isinstance(item, BaseMhdRelationship):
                    mhd_dataset.graph.relationships.append(item)
                else:
                    mhd_dataset.graph.nodes.append(item)

        def sort_key(item: BaseLabeledMhdModel):
            if isinstance(item, CvTerm):
                return (100, item.type_, item.label, item.id_)
            if item.id_ in start_item_refs:
                return (0, item.type_, item.label, item.id_)
            if isinstance(item, BaseMhdRelationship):
                return (
                    0,
                    item.source_ref,
                    item.relationship_name,
                    item.target_ref,
                    item.id_,
                )
            if item.id_.startswith("cv-"):
                return (100, item.type_, item.label, item.id_)
            return (2, item.type_, item.label, item.id_)

        mhd_dataset.graph.nodes = sorted(mhd_dataset.graph.nodes, key=sort_key)
        mhd_dataset.graph.relationships.sort(key=sort_key)
        return mhd_dataset

    @classmethod
    def from_dataset(cls, mhd_dataset: MhDatasetBaseProfile) -> "MhDatasetBuilder":
        dataset = cls(
            schema_name=mhd_dataset.schema_name, profile_uri=mhd_dataset.profile_uri
        )
        dataset.cv_definitions = (
            mhd_dataset.cv_definitions.copy() if mhd_dataset.cv_definitions else []
        )
        dataset.repository_name = mhd_dataset.repository_name
        dataset.mhd_identifier = mhd_dataset.mhd_identifier
        dataset.repository_identifier = mhd_dataset.repository_identifier
        dataset.revision = mhd_dataset.revision
        dataset.revision_datetime = mhd_dataset.revision_datetime
        dataset.repository_revision = mhd_dataset.repository_revision
        dataset.repository_revision_datetime = mhd_dataset.repository_revision_datetime
        dataset.change_log = (
            mhd_dataset.change_log.copy() if mhd_dataset.change_log else []
        )

        for item in mhd_dataset.graph.nodes:
            dataset.objects[item.id_] = item
        for item in mhd_dataset.graph.relationships:
            dataset.objects[item.id_] = item
        return dataset
