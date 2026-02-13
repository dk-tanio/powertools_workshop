"""Domain specific exceptions."""


class BookDomainError(Exception):
    """ドメイン共通の例外。"""


class BookNotFoundError(BookDomainError):
    """書籍が見つからない場合の例外。"""


class BookAlreadyExistsError(BookDomainError):
    """書籍が既に存在する場合の例外。"""


class RepositoryOperationError(BookDomainError):
    """リポジトリ操作全般の例外。"""
