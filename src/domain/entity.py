"""Domain models for book aggregate."""

from datetime import datetime
from typing import Annotated

from pydantic import Field, field_serializer, field_validator, model_validator

from domain.object_values import Author, PublishedYear, Summary, Title
from services.util import BaseModel


class Book(BaseModel):
    """書籍エンティティ。"""

    id: Annotated[str, Field(min_length=1)]
    title: Title
    author: Author
    published_year: PublishedYear
    summary: Summary
    created_at: datetime | str
    updated_at: datetime | str

    @model_validator(mode="after")
    def validate_year(self) -> "Book":
        """出版年を未来日にさせない。"""
        current_year = datetime.now().year
        if self.published_year.root > current_year:
            msg = "published_year cannot be in the future"
            raise ValueError(msg)
        return self

    @field_validator("created_at", "updated_at", mode="before")
    def deserialize_datetime(cls, value: datetime | str) -> datetime:
        """ISO 8601形式の文字列をdatetimeに変換。"""
        if isinstance(value, datetime):
            return value
        return datetime.fromisoformat(value)

    @field_serializer("created_at", "updated_at")
    def serialize_datetime(self, value: datetime) -> str:
        """日時をISO 8601形式でシリアライズ。"""
        return value.isoformat()

    def update(
        self,
        title: Title,
        author: Author,
        published_year: PublishedYear,
        now: datetime,
        summary: Summary,
    ) -> "Book":
        return self.model_copy(
            update={
                "title": title,
                "author": author,
                "published_year": published_year,
                "summary": summary,
                "updated_at": now,
            }
        )
