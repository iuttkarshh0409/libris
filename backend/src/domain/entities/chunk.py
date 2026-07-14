from src.domain.value_objects.identifiers import BookId, ChapterId, ChunkId, SectionId
from src.shared.domain.base import BaseEntity


class Chunk(BaseEntity):
    """The fundamental cohesive unit of knowledge in the application."""

    def __init__(
        self,
        id: ChunkId,
        book_id: BookId,
        page_number: int,
        chunk_index: int,
        chunk_text: str,
        character_count: int,
        token_count: int,
        chapter_id: ChapterId | None = None,
        section_id: SectionId | None = None,
        previous_chunk_id: ChunkId | None = None,
        next_chunk_id: ChunkId | None = None,
        source_page_start: int | None = None,
        source_page_end: int | None = None,
    ) -> None:
        super().__init__(id)
        self._book_id = book_id
        self._page_number = page_number
        self._chunk_index = chunk_index
        self._chunk_text = chunk_text
        self._character_count = character_count
        self._token_count = token_count
        self._chapter_id = chapter_id
        self._section_id = section_id
        self._previous_chunk_id = previous_chunk_id
        self._next_chunk_id = next_chunk_id
        self._source_page_start = (
            source_page_start if source_page_start is not None else page_number
        )
        self._source_page_end = source_page_end if source_page_end is not None else page_number

    @property
    def id(self) -> ChunkId:
        assert isinstance(self._id, ChunkId)
        return self._id

    @property
    def book_id(self) -> BookId:
        return self._book_id

    @property
    def page_number(self) -> int:
        return self._page_number

    @property
    def chunk_index(self) -> int:
        return self._chunk_index

    @property
    def chunk_text(self) -> str:
        return self._chunk_text

    @property
    def character_count(self) -> int:
        return self._character_count

    @property
    def token_count(self) -> int:
        return self._token_count

    @property
    def chapter_id(self) -> ChapterId | None:
        return self._chapter_id

    @property
    def section_id(self) -> SectionId | None:
        return self._section_id

    @property
    def previous_chunk_id(self) -> ChunkId | None:
        return self._previous_chunk_id

    @property
    def next_chunk_id(self) -> ChunkId | None:
        return self._next_chunk_id

    @property
    def source_page_start(self) -> int:
        return self._source_page_start

    @property
    def source_page_end(self) -> int:
        return self._source_page_end
