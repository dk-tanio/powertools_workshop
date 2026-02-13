"""Repository protocol definitions."""

from typing import Protocol

from domain.entity import Book
from services.dto import BookList


class IBookRepository(Protocol):
    """書籍リポジトリのインタフェース。"""

    def list_books(self) -> BookList:
        """全件取得。"""
        ...

    def create_book(self, book: Book) -> Book:
        """書籍を保存。"""
        ...

    def get_book(self, book_id: str) -> Book:
        """IDで単一取得。存在しない場合はBookNotFoundErrorを送出。"""
        ...

    def update_book(self, book: Book) -> Book:
        """書籍全体を上書き。"""
        ...

    def delete_book(self, book_id: str) -> None:
        """書籍削除。"""
        ...
