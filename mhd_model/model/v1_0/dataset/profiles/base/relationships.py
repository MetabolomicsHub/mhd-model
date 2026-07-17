from pydantic import Field
from typing_extensions import Annotated

from mhd_model.model.v1_0.dataset.profiles.base.base import (
    BaseMhdRelationship,
    MhdObjectType,
)


class Relationship(BaseMhdRelationship):
    type_: Annotated[
        None | MhdObjectType,
        Field(
            frozen=True,
            alias="type",
            description="The type property identifies type of the MHD Relationship Object",
        ),
    ] = "relationship"
