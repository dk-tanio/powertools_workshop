"""Lambda handlers for the book API using Powertools REST resolver."""

import json
from http import HTTPStatus

from aws_lambda_powertools import Logger
from aws_lambda_powertools.event_handler import APIGatewayRestResolver, Response
from aws_lambda_powertools.utilities.typing import LambdaContext

from domain.exceptions import (
    BookAlreadyExistsError,
    BookNotFoundError,
    RepositoryOperationError,
)
from domain.object_values import Author, PublishedYear, Summary, Title
from infrastructure.dynamodb_repository import DynamoBookRepository
from services.book_service import BookService

logger = Logger()
app = APIGatewayRestResolver()


@app.get("/books")
def list_books_handler() -> Response:
    """書籍一覧取得のLambda"""
    try:
        repository = DynamoBookRepository()
        service = BookService(repository=repository)
        books = service.list_books()
    except RepositoryOperationError:
        logger.error("Repository operation failed")
        return Response(
            status_code=int(HTTPStatus.INTERNAL_SERVER_ERROR),
            body=json.dumps({"message": "Internal server error"}),
        )

    return Response(status_code=int(HTTPStatus.OK), body=books.model_dump_json())


@app.post("/books")
def create_book_handler() -> Response:
    """書籍作成のLambda"""
    body_data = app.current_event.json_body or {}
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
        return Response(
            status_code=int(HTTPStatus.CONFLICT),
            body=json.dumps({"message": str(error)}),
        )
    except RepositoryOperationError:
        logger.error(msg="Repository operation failed")
        return Response(
            status_code=int(HTTPStatus.INTERNAL_SERVER_ERROR),
            body=json.dumps({"message": "Internal server error"}),
        )

    logger.info(msg="Book successfully created", extra={"book_id": book.id})
    return Response(status_code=int(HTTPStatus.CREATED), body=book.model_dump_json())


@app.get("/books/<book_id>")
def get_book_handler(book_id: str) -> Response:
    """書籍単体取得のLambda"""
    try:
        repository = DynamoBookRepository()
        service = BookService(repository=repository)
        book = service.get_book(book_id=book_id)
    except BookNotFoundError as error:
        logger.warning(msg="Book not found")
        return Response(
            status_code=int(HTTPStatus.NOT_FOUND),
            body=json.dumps({"message": str(error)}),
        )
    except RepositoryOperationError:
        logger.error(msg="Repository operation failed")
        return Response(
            status_code=int(HTTPStatus.INTERNAL_SERVER_ERROR),
            body=json.dumps({"message": "Internal server error"}),
        )

    return Response(status_code=int(HTTPStatus.OK), body=book.model_dump_json())


@app.put("/books/<book_id>")
def update_book_handler(book_id: str) -> Response:
    """書籍更新のLambda"""
    body_data = app.current_event.json_body or {}
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
        return Response(
            status_code=int(HTTPStatus.NOT_FOUND),
            body=json.dumps({"message": str(error)}),
        )
    except RepositoryOperationError:
        logger.error(msg="Repository operation failed")
        return Response(
            status_code=int(HTTPStatus.INTERNAL_SERVER_ERROR),
            body=json.dumps({"message": "Internal server error"}),
        )

    return Response(status_code=int(HTTPStatus.OK), body=book.model_dump_json())


@app.delete("/books/<book_id>")
def delete_book_handler(book_id: str) -> Response:
    """書籍削除のLambda"""
    try:
        repository = DynamoBookRepository()
        service = BookService(repository=repository)
        service.delete_book(book_id=book_id)
    except BookNotFoundError as error:
        logger.warning(msg="Book not found while deleting")
        return Response(
            status_code=int(HTTPStatus.NOT_FOUND),
            body=json.dumps({"message": str(error)}),
        )
    except RepositoryOperationError:
        logger.error(msg="Repository operation failed")
        return Response(
            status_code=int(HTTPStatus.INTERNAL_SERVER_ERROR),
            body=json.dumps({"message": "Internal server error"}),
        )

    return Response(
        status_code=int(HTTPStatus.NO_CONTENT),
        body="",
    )


def lambda_handler(event: dict, context: LambdaContext) -> dict:
    """Entrypoint for AWS Lambda."""
    return app.resolve(event, context)
