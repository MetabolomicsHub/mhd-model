from typing import Annotated

from pydantic import Field

from mhd_model.shared.model import BaseRelationshipModel, MhdObjectType


class Relationship(BaseRelationshipModel):
    type_: Annotated[
        None | MhdObjectType,
        Field(
            alias="type",
            description="The type property identifies type of the MHD Relationship Object",
        ),
    ] = "default"
