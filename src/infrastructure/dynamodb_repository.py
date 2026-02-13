"""DynamoDB implementation of book repository."""

import os

import boto3
from botocore.exceptions import ClientError

from domain.entity import Book
from domain.exceptions import (
    BookAlreadyExistsError,
    BookNotFoundError,
    RepositoryOperationError,
)
from domain.repositories import IBookRepository
from services.dto import BookList


class DynamoBookRepository(IBookRepository):
    """DynamoDBで書籍を保存するリポジトリ。"""

    def __init__(self, table_name: str | None = None) -> None:
        """テーブル名を設定し、リソースを初期化。"""
        resolved_name = table_name or os.environ.get("BOOKS_TABLE_NAME")
        if not resolved_name:
            raise RepositoryOperationError("BOOKS_TABLE_NAME is required")
        self.table = boto3.resource("dynamodb").Table(resolved_name)

    def list_books(self) -> BookList:
        """全件をスキャンで取得。"""
        try:
            response = self.table.scan()
        except ClientError as error:
            raise RepositoryOperationError(str(error)) from error

        items = [Book.model_validate(item) for item in response.get("Items", [])]
        return BookList.from_items(items=items)

    def create_book(self, book: Book) -> Book:
        """条件付き書き込みで新規作成。"""
        item = book.model_dump()

        try:
            self.table.put_item(Item=item, ConditionExpression="attribute_not_exists(id)")
        except ClientError as error:
            if error.response["Error"].get("Code") == "ConditionalCheckFailedException":
                raise BookAlreadyExistsError(str(error)) from error
            raise RepositoryOperationError(str(error)) from error
        return book

    def get_book(self, book_id: str) -> Book:
        """主キーで単一取得。"""
        try:
            response = self.table.get_item(Key={"id": book_id})
        except ClientError as error:
            raise RepositoryOperationError(str(error)) from error

        item = response.get("Item")
        if not item:
            raise BookNotFoundError(f"Book {book_id} not found")
        return Book.model_validate(item)

    def update_book(self, book: Book) -> Book:
        """全体更新。"""
        item = book.model_dump()

        try:
            self.table.put_item(Item=item, ConditionExpression="attribute_exists(id)")
        except ClientError as error:
            if error.response["Error"].get("Code") == "ConditionalCheckFailedException":
                raise BookNotFoundError(str(error)) from error
            raise RepositoryOperationError(str(error)) from error
        return book

    def delete_book(self, book_id: str) -> None:
        """主キー削除。"""
        try:
            self.table.delete_item(Key={"id": book_id}, ConditionExpression="attribute_exists(id)")
        except ClientError as error:
            if error.response["Error"].get("Code") == "ConditionalCheckFailedException":
                raise BookNotFoundError(str(error)) from error
            raise RepositoryOperationError(str(error)) from error
