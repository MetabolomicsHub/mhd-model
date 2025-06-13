from pydantic import Field
from typing_extensions import Annotated

from mhd_model.model.v0_1.dataset.profiles.base.base import (
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
