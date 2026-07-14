from src.domain.value_objects.identifiers import BookId, PageId
from src.shared.domain.base import BaseEntity


class Page(BaseEntity):
    """Represents a single physical page extracted from a Book."""

    def __init__(
        self,
        id: PageId,
        book_id: BookId,
        page_number: int,
        extracted_text: str,
        character_count: int,
    ) -> None:
        super().__init__(id)
        self._book_id = book_id
        self._page_number = page_number
        self._extracted_text = extracted_text
        self._character_count = character_count

    @property
    def id(self) -> PageId:
        assert isinstance(self._id, PageId)
        return self._id

    @property
    def book_id(self) -> BookId:
        return self._book_id

    @property
    def page_number(self) -> int:
        return self._page_number

    @property
    def extracted_text(self) -> str:
        return self._extracted_text

    @property
    def character_count(self) -> int:
        return self._character_count
