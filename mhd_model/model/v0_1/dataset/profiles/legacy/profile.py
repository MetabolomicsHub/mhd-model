from pydantic import Field
from typing_extensions import Annotated

from mhd_model.model.v0_1.dataset.profiles.base import graph_nodes
from mhd_model.model.v0_1.dataset.profiles.base.base import (
    CvTermObjectId,
    CvTermValueObjectId,
    MhdConfigModel,
    MhdObjectId,
    MhdObjectType,
)
from mhd_model.model.v0_1.dataset.profiles.base.profile import (
    MhDatasetBaseProfile,
)
from mhd_model.model.v0_1.dataset.profiles.legacy.graph_nodes import LegacyStudy


class MhdLegacyProfileGraph(MhdConfigModel):
    start_item_refs: Annotated[
        list[MhdObjectId | CvTermObjectId | CvTermValueObjectId], Field()
    ] = []
    nodes: Annotated[
        list[
            graph_nodes.CvTermValueObject
            | graph_nodes.CvTermObject
            | graph_nodes.Person
            | graph_nodes.Project
            | LegacyStudy
            | graph_nodes.Protocol
            | graph_nodes.Publication
            | graph_nodes.BasicAssay
            | graph_nodes.Assay
            | graph_nodes.Specimen
            | graph_nodes.Subject
            | graph_nodes.Sample
            | graph_nodes.SampleRun
            | graph_nodes.SampleRunConfiguration
            | graph_nodes.Metabolite
            | graph_nodes.MetadataFile
            | graph_nodes.ResultFile
            | graph_nodes.RawDataFile
            | graph_nodes.DerivedDataFile
            | graph_nodes.SupplementaryFile
            | graph_nodes.BaseLabeledMhdModel
        ],
        Field(),
    ] = []


class MhDatasetLegacyProfile(MhDatasetBaseProfile):
    type_: Annotated[MhdObjectType, Field(frozen=True, alias="type")] = MhdObjectType(
        "legacy-dataset"
    )
    graph: Annotated[
        MhdLegacyProfileGraph, Field(json_schema_extra={"mhdGraphValidation": {}})
    ] = MhdLegacyProfileGraph()
