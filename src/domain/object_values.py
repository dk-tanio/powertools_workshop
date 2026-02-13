from typing import Annotated

from pydantic import Field, RootModel


class Title(RootModel):
    root: Annotated[str, Field(min_length=1, max_length=200)]


class Author(RootModel):
    root: Annotated[str, Field(min_length=1, max_length=120)]


class PublishedYear(RootModel):
    root: Annotated[int, Field(ge=0)]


class Summary(RootModel):
    root: Annotated[str | None, Field(default=None, max_length=2000)]
