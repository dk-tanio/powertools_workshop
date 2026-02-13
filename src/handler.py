"""Lambda handlers for the book API without Powertools glue code."""

import base64
import json
from http import HTTPStatus
from typing import Any

from aws_lambda_powertools import Logger

from domain.exceptions import (
    BookAlreadyExistsError,
    BookNotFoundError,
    RepositoryOperationError,
)
from domain.object_values import Author, PublishedYear, Summary, Title
from infrastructure.dynamodb_repository import DynamoBookRepository
from services.book_service import BookService

logger = Logger()


def list_books_handler(event: dict[str, Any], context: Any | None = None) -> dict[str, Any]:
    """書籍一覧取得のLambda"""
    try:
        repository = DynamoBookRepository()
        service = BookService(repository=repository)
        books = service.list_books()
    except RepositoryOperationError:
        logger.error("Repository operation failed")
        return {
            "statusCode": int(HTTPStatus.INTERNAL_SERVER_ERROR),
            "body": json.dumps({"message": "Internal server error"}),
        }

    return {"statusCode": int(HTTPStatus.OK), "body": books.model_dump_json()}


@logger.inject_lambda_context(log_event=True)
def create_book_handler(event: dict[str, Any], context: Any | None = None) -> dict[str, Any]:
    """書籍作成のLambda"""
    body = event.get("body")
    if not body:
        body_data: dict[str, Any] = {}
    else:
        if event.get("isBase64Encoded"):
            body = base64.b64decode(body).decode("utf-8")
        body_data = json.loads(body)
    title = Title(body_data.get("title"))
    author = Author(body_data.get("author"))
    published_year = PublishedYear(body_data.get("published_year"))
    summary = Summary(body_data.get("summary"))

    try:
        repository = DynamoBookRepository()
        service = BookService(repository=repository)
        book = service.create_book(
            title=title, author=author, published_year=published_year, summary=summary
        )
    except BookAlreadyExistsError as error:
        logger.warning("Book already exists")
        return {
            "statusCode": int(HTTPStatus.CONFLICT),
            "body": json.dumps({"message": str(error)}),
        }
    except RepositoryOperationError:
        logger.error(msg="Repository operation failed")
        return {
            "statusCode": int(HTTPStatus.INTERNAL_SERVER_ERROR),
            "body": json.dumps({"message": "Internal server error"}),
        }

    logger.info(msg="Book successfully created", extra={"book_id": book.id})
    return {"statusCode": int(HTTPStatus.CREATED), "body": book.model_dump_json()}


def get_book_handler(event: dict[str, Any], context: Any | None = None) -> dict[str, Any]:
    """書籍単体取得のLambda"""
    path_parameters = event.get("pathParameters") or {}
    book_id = path_parameters.get("id")
    if not book_id:
        raise ValueError("path parameter 'id' is required")
    try:
        repository = DynamoBookRepository()
        service = BookService(repository=repository)
        book = service.get_book(book_id=book_id)
    except BookNotFoundError as error:
        logger.warning(msg="Book not found")
        return {
            "statusCode": int(HTTPStatus.NOT_FOUND),
            "body": json.dumps({"message": str(error)}),
        }
    except RepositoryOperationError:
        logger.error(msg="Repository operation failed")
        return {
            "statusCode": int(HTTPStatus.INTERNAL_SERVER_ERROR),
            "body": json.dumps({"message": "Internal server error"}),
        }

    return {"statusCode": int(HTTPStatus.OK), "body": json.dumps(book.model_dump())}


def update_book_handler(event: dict[str, Any], context: Any | None = None) -> dict[str, Any]:
    """書籍更新のLambda"""
    path_parameters = event.get("pathParameters") or {}
    book_id = path_parameters.get("id")
    if not book_id:
        raise ValueError("path parameter 'id' is required")
    body = event.get("body")
    if not body:
        body_data: dict[str, Any] = {}
    else:
        if event.get("isBase64Encoded"):
            body = base64.b64decode(body).decode("utf-8")
        body_data = json.loads(body)
    title = Title(body_data.get("title"))
    author = Author(body_data.get("author"))
    published_year = PublishedYear(body_data.get("published_year"))
    summary = Summary(body_data.get("summary"))

    try:
        repository = DynamoBookRepository()
        service = BookService(repository=repository)
        book = service.update_book(
            book_id=book_id,
            title=title,
            author=author,
            published_year=published_year,
            summary=summary,
        )
    except BookNotFoundError as error:
        logger.warning(msg="Book not found while updating")
        return {
            "statusCode": int(HTTPStatus.NOT_FOUND),
            "body": json.dumps({"message": str(error)}),
        }
    except RepositoryOperationError:
        logger.error(msg="Repository operation failed")
        return {
            "statusCode": int(HTTPStatus.INTERNAL_SERVER_ERROR),
            "body": json.dumps({"message": "Internal server error"}),
        }
    return {"statusCode": int(HTTPStatus.OK), "body": json.dumps(book.model_dump())}


def delete_book_handler(event: dict[str, Any], context: Any | None = None) -> dict[str, Any]:
    """書籍削除のLambda"""
    path_parameters = event.get("pathParameters") or {}
    book_id = path_parameters.get("id")
    if not book_id:
        raise ValueError("path parameter 'id' is required")
    try:
        repository = DynamoBookRepository()
        service = BookService(repository=repository)
        service.delete_book(book_id=book_id)
    except BookNotFoundError as error:
        logger.warning(msg="Book not found while deleting")
        return {
            "statusCode": int(HTTPStatus.NOT_FOUND),
            "body": json.dumps({"message": str(error)}),
        }
    except RepositoryOperationError:
        logger.error(msg="Repository operation failed")
        return {
            "statusCode": int(HTTPStatus.INTERNAL_SERVER_ERROR),
            "body": json.dumps({"message": "Internal server error"}),
        }
    return {"statusCode": int(HTTPStatus.NO_CONTENT), "body": ""}
