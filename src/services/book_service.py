"""Service layer orchestrating domain and infrastructure."""

from datetime import UTC, datetime
from uuid import uuid4

from domain.entity import Book
from domain.object_values import Author, PublishedYear, Summary, Title
from domain.repositories import IBookRepository
from services.dto import BookList


class BookService:
    """書籍ユースケースをまとめるサービス。"""

    def __init__(self, repository: IBookRepository) -> None:
        """依存リポジトリを注入。"""
        self.repository = repository

    def list_books(self) -> BookList:
        """書籍一覧を返す。"""
        return self.repository.list_books()

    def create_book(
        self, title: Title, author: Author, published_year: PublishedYear, summary: Summary
    ) -> Book:
        """新規書籍を作成する。"""
        now = datetime.now(UTC)
        book = Book(
            id=str(uuid4()),
            title=title,
            author=author,
            published_year=published_year,
            summary=summary,
            created_at=now,
            updated_at=now,
        )
        return self.repository.create_book(book=book)

    def get_book(self, book_id: str) -> Book:
        """単体書籍を取得。"""
        return self.repository.get_book(book_id=book_id)

    def update_book(
        self,
        book_id: str,
        title: Title,
        author: Author,
        published_year: PublishedYear,
        summary: Summary,
    ) -> Book:
        """既存書籍を更新。"""
        stored = self.get_book(book_id=book_id)
        now = datetime.now(UTC)
        updated = stored.update(
            title=title, author=author, published_year=published_year, summary=summary, now=now
        )
        return self.repository.update_book(book=updated)

    def delete_book(self, book_id: str) -> None:
        """書籍削除。"""
        self.get_book(book_id=book_id)
        self.repository.delete_book(book_id=book_id)
