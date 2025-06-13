from typing import Annotated

from pydantic import Field

MhdIdentifier = Annotated[str, Field(pattern=r"MHD[A-Z][0-9]{6,6}")]

PubMedId = Annotated[str, Field(pattern=r"^[0-9]{1,20}$", title="PubMed Id")]
ORCID = Annotated[str, Field(pattern=r"^[0-9]{4}-[0-9]{4}-[0-9]{4}-[0-9]{3}[X0-9]$")]
DOI = Annotated[str, Field(pattern=r"^10[.].+/.+$", title="DOI")]


Author = Annotated[str, Field(min_length=2)]
Authors = Annotated[list[Author], Field(min_length=1)]
GrantId = Annotated[str, Field(min_length=2)]
