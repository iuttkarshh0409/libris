from typing import ClassVar

from src.domain.entities.book import Book
from src.domain.repositories.book import BookRepository
from src.domain.value_objects.identifiers import BookId


class LocalBookRepository(BookRepository):
    """Concrete local implementation of BookRepository using an in-memory database."""

    _db: ClassVar[dict[str, Book]] = {}

    def save(self, book: Book) -> None:
        self._db[book.id.value] = book

    def get_by_id(self, book_id: BookId) -> Book | None:
        return self._db.get(book_id.value)

    def list_all(self) -> list[Book]:
        return list(self._db.values())

    def delete(self, book_id: BookId) -> None:
        if book_id.value in self._db:
            del self._db[book_id.value]
