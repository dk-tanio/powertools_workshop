"""Request schema definitions for API handlers."""

from domain.object_values import Author, PublishedYear, Summary, Title
from services.util import BaseModel


class BookInformationSchema(BaseModel):
    title: Title
    author: Author
    published_year: PublishedYear
    summary: Summary
