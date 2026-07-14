from typing import Protocol

from src.domain.entities.book import Book
from src.domain.value_objects.identifiers import BookId


class BookRepository(Protocol):
    """Protocol defining persistence operations for Book metadata and hierarchy."""

    def save(self, book: Book) -> None:
        """Persists a Book entity."""
        ...

    def get_by_id(self, book_id: BookId) -> Book | None:
        """Retrieves a Book by its BookId, returning None if not found."""
        ...

    def list_all(self) -> list[Book]:
        """Retrieves all persisted Book entities."""
        ...

    def delete(self, book_id: BookId) -> None:
        """Deletes a persisted Book by its BookId."""
        ...
