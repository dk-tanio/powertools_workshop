from domain.entity import Book
from services.util import BaseModel


class BookList(BaseModel):
    """複数書籍のコレクション。"""

    items: list[Book]
    total: int

    @classmethod
    def from_items(cls, items: list[Book]) -> "BookList":
        """件数をセットしたリストを返す。"""
        return cls(items=items, total=len(items))

    def filter_by_author(self, author: str) -> "BookList":
        """特定著者でフィルタリング(ドメインロジック例)。"""
        filtered = [book for book in self.items if book.author == author]
        return BookList.from_items(items=filtered)

    def published_after(self, year: int) -> "BookList":
        """指定年以降の書籍を抽出。"""
        filtered = [book for book in self.items if book.published_year.root >= year]
        return BookList.from_items(items=filtered)
