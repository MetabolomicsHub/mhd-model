from typing import Self, Sequence

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
from mhd_model.shared.model import CvTerm


class MhDatasetBuilder(GraphEnabledBaseDataset):
    type_: Annotated[MhdObjectType, Field(frozen=True, alias="type")] = MhdObjectType(
        "dataset"
    )

    objects: dict[str, IdentifiableMhdModel] = {}

    def add(self, item: IdentifiableMhdModel) -> Self:
        self.objects[item.id_] = item
        return self

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
        self.objects[item.id_] = item
        return self

    def add_relationship(self, item: BaseMhdRelationship) -> Self:
        self.objects[item.id_] = item
        return self

    def create_dataset(self, start_item_refs: Sequence[str]) -> MhDatasetBaseProfile:
        mhd_dataset = MhDatasetBaseProfile(
            schema_name=self.schema_name, profile_uri=self.profile_uri
        )
        mhd_dataset.repository_name = self.repository_name
        mhd_dataset.revision = self.revision
        mhd_dataset.revision_datetime = self.revision_datetime
        mhd_dataset.repository_revision = self.repository_revision
        mhd_dataset.repository_revision_datetime = self.repository_revision_datetime
        mhd_dataset.change_log = self.change_log

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
        dataset.repository_name = mhd_dataset.repository_name
        dataset.revision = mhd_dataset.revision
        dataset.revision_datetime = mhd_dataset.revision_datetime
        dataset.repository_revision = mhd_dataset.repository_revision
        dataset.repository_revision_datetime = mhd_dataset.repository_revision_datetime
        dataset.change_log = mhd_dataset.change_log

        for item in mhd_dataset.graph.nodes:
            dataset.objects[item.id_] = item
        for item in mhd_dataset.graph.relationships:
            dataset.objects[item.id_] = item
        return dataset
