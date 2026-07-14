from src.domain.value_objects.identifiers import BookId, ChapterId
from src.shared.domain.base import BaseEntity


class Chapter(BaseEntity):
    """Represents a logical chapter within a textbook."""

    def __init__(
        self,
        id: ChapterId,
        book_id: BookId,
        chapter_number: str,
        chapter_title: str,
        start_page: int,
        end_page: int,
    ) -> None:
        super().__init__(id)
        self._book_id = book_id
        self._chapter_number = chapter_number
        self._chapter_title = chapter_title
        self._start_page = start_page
        self._end_page = end_page

    @property
    def id(self) -> ChapterId:
        assert isinstance(self._id, ChapterId)
        return self._id

    @property
    def book_id(self) -> BookId:
        return self._book_id

    @property
    def chapter_number(self) -> str:
        return self._chapter_number

    @property
    def chapter_title(self) -> str:
        return self._chapter_title

    @property
    def start_page(self) -> int:
        return self._start_page

    @property
    def end_page(self) -> int:
        return self._end_page
