from src.domain.entities.book import Book
from src.domain.entities.chapter import Chapter
from src.domain.entities.page import Page
from src.domain.entities.section import Section
from src.domain.value_objects.identifiers import BookId
from src.shared.domain.base import ValueObject


class ParsedDocument(ValueObject):
    """A technical aggregate packaging related domain entities for a parsed document."""

    def __init__(
        self,
        book: Book,
        pages: list[Page],
        chapters: list[Chapter],
        sections: list[Section],
    ) -> None:
        self._book = book
        self._pages = pages
        self._chapters = chapters
        self._sections = sections

    @property
    def book(self) -> Book:
        return self._book

    @property
    def book_id(self) -> BookId:
        return self._book.id

    @property
    def pages(self) -> list[Page]:
        return self._pages

    @property
    def items(self) -> list[Page]:
        return self._pages

    @property
    def chapters(self) -> list[Chapter]:
        return self._chapters

    @property
    def sections(self) -> list[Section]:
        return self._sections

    @property
    def statistics(self) -> dict[str, int | float]:
        return {
            "total_pages": len(self._pages),
            "total_chapters": len(self._chapters),
            "total_sections": len(self._sections),
        }

    @property
    def metadata(self) -> dict[str, str | int | float | None]:
        return {
            "title": self._book.title,
            "author": self._book.author,
            "edition": self._book.edition,
            "subject": self._book.subject,
        }
