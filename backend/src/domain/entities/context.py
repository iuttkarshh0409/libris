from datetime import datetime
from typing import Any

from src.domain.value_objects.identifiers import BookId, ChapterId, ChunkId, EmbeddingId, SectionId
from src.shared.domain.base import BaseEntity, ValueObject


class RetrievedChunk(BaseEntity):
    """Represents a chunk of retrieved text with score and ranking metadata."""

    def __init__(
        self,
        chunk_id: ChunkId,
        embedding_id: EmbeddingId,
        chunk_text: str,
        similarity_score: float,
        retrieval_rank: int,
        page_number: int,
        chapter_id: ChapterId | None,
        section_id: SectionId | None,
        retrieval_timestamp: datetime,
    ) -> None:
        super().__init__(chunk_id)
        self._chunk_id = chunk_id
        self._embedding_id = embedding_id
        self._chunk_text = chunk_text
        self._similarity_score = similarity_score
        self._retrieval_rank = retrieval_rank
        self._page_number = page_number
        self._chapter_id = chapter_id
        self._section_id = section_id
        self._retrieval_timestamp = retrieval_timestamp

    @property
    def chunk_id(self) -> ChunkId:
        return self._chunk_id

    @property
    def embedding_id(self) -> EmbeddingId:
        return self._embedding_id

    @property
    def chunk_text(self) -> str:
        return self._chunk_text

    @property
    def similarity_score(self) -> float:
        return self._similarity_score

    @property
    def retrieval_rank(self) -> int:
        return self._retrieval_rank

    @property
    def page_number(self) -> int:
        return self._page_number

    @property
    def chapter_id(self) -> ChapterId | None:
        return self._chapter_id

    @property
    def section_id(self) -> SectionId | None:
        return self._section_id

    @property
    def retrieval_timestamp(self) -> datetime:
        return self._retrieval_timestamp


class RetrievalContext(ValueObject):
    """Aggregate representing the ordered, validated retrieval context for a query."""

    def __init__(
        self,
        book_id: BookId,
        items: list[RetrievedChunk],
        statistics: dict[str, Any],
        metadata: dict[str, Any],
    ) -> None:
        self._book_id = book_id
        self._items = items
        self._statistics = statistics
        self._metadata = metadata

    @property
    def book_id(self) -> BookId:
        return self._book_id

    @property
    def items(self) -> list[RetrievedChunk]:
        return self._items

    @property
    def statistics(self) -> dict[str, Any]:
        return self._statistics

    @property
    def metadata(self) -> dict[str, Any]:
        return self._metadata
