from typing import Annotated

from pydantic import Field

MhdIdentifier = Annotated[
    str, Field(pattern=r"^MHD[A-Z][0-9]{6,8}$", title="MHD Identifier")
]

PubMedId = Annotated[str, Field(pattern=r"^[0-9]{1,20}$", title="PubMed Id")]
ORCID = Annotated[
    str, Field(pattern=r"^[0-9]{4}-[0-9]{4}-[0-9]{4}-[0-9]{3}[X0-9]$", title="ORCID")
]
DOI = Annotated[str, Field(pattern=r"^10[.].+/.+$", title="DOI")]


Author = Annotated[str, Field(min_length=2, title="Author")]
Authors = Annotated[list[Author], Field(min_length=1, title="Authors")]
GrantId = Annotated[str, Field(min_length=2, title="Grant Identifier")]
