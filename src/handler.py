"""Lambda handlers for the book API using Powertools REST resolver."""

from http import HTTPStatus

from aws_lambda_powertools import Logger
from aws_lambda_powertools.event_handler import APIGatewayRestResolver, Response
from aws_lambda_powertools.utilities.typing import LambdaContext

from domain.exceptions import (
    BookAlreadyExistsError,
    BookNotFoundError,
    RepositoryOperationError,
)
from infrastructure.dynamodb_repository import DynamoBookRepository
from schema import BookInformationSchema
from services.book_service import BookService

logger = Logger()
app = APIGatewayRestResolver(enable_validation=True)


@app.get("/books")
def list_books_handler() -> Response:
    """書籍一覧取得のLambda"""
    repository = DynamoBookRepository()
    service = BookService(repository=repository)
    books = service.list_books()
    return Response(status_code=int(HTTPStatus.OK), body=books.model_dump_json())


@app.post("/books")
def create_book_handler(body: BookInformationSchema) -> Response:
    """書籍作成のLambda"""
    repository = DynamoBookRepository()
    service = BookService(repository=repository)
    book = service.create_book(
        title=body.title,
        author=body.author,
        published_year=body.published_year,
        summary=body.summary,
    )
    logger.info(msg="Book successfully created", extra={"book_id": book.id})
    return Response(status_code=int(HTTPStatus.CREATED), body=book.model_dump_json())


@app.get("/books/<book_id>")
def get_book_handler(book_id: str) -> Response:
    """書籍単体取得のLambda"""
    repository = DynamoBookRepository()
    service = BookService(repository=repository)
    book = service.get_book(book_id=book_id)
    return Response(status_code=int(HTTPStatus.OK), body=book.model_dump_json())


@app.put("/books/<book_id>")
def update_book_handler(book_id: str, body: BookInformationSchema) -> Response:
    """書籍更新のLambda"""
    repository = DynamoBookRepository()
    service = BookService(repository=repository)
    book = service.update_book(
        book_id=book_id,
        title=body.title,
        author=body.author,
        published_year=body.published_year,
        summary=body.summary,
    )
    return Response(status_code=int(HTTPStatus.OK), body=book.model_dump_json())


@app.delete("/books/<book_id>")
def delete_book_handler(book_id: str) -> Response:
    """書籍削除のLambda"""
    repository = DynamoBookRepository()
    service = BookService(repository=repository)
    service.delete_book(book_id=book_id)
    return Response(status_code=int(HTTPStatus.NO_CONTENT), body="")


def lambda_handler(event: dict, context: LambdaContext) -> dict:
    """Entrypoint for AWS Lambda."""
    return app.resolve(event, context)


@app.exception_handler(BookAlreadyExistsError)
def handle_book_already_exists(ex: BookAlreadyExistsError) -> Response:
    logger.warning("Book already exists", path=app.current_event.path, error=str(ex))
    return Response(status_code=int(HTTPStatus.CONFLICT), body="Book already exists")


@app.exception_handler(BookNotFoundError)
def handle_book_not_found(ex: BookNotFoundError) -> Response:
    logger.warning("Book not found", path=app.current_event.path, error=str(ex))
    return Response(status_code=int(HTTPStatus.NOT_FOUND), body="Book not found")


@app.exception_handler(RepositoryOperationError)
def handle_repository_error(ex: RepositoryOperationError) -> Response:
    logger.error("Repository operation failed", path=app.current_event.path, error=str(ex))
    return Response(status_code=int(HTTPStatus.INTERNAL_SERVER_ERROR), body="Internal server error")
