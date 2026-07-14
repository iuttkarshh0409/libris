from datetime import datetime
from typing import Any

from src.domain.value_objects.identifiers import BookId, ChunkId, EmbeddingId
from src.shared.domain.base import BaseEntity, ValueObject


class IndexRecord(BaseEntity):
    """Represents a successfully indexed record in the knowledge index."""

    def __init__(
        self,
        embedding_id: EmbeddingId,
        chunk_id: ChunkId,
        book_id: BookId,
        indexed_timestamp: datetime,
        model_identifier: str,
        vector_dimension: int,
        persistence_status: str,
    ) -> None:
        super().__init__(embedding_id)
        self._embedding_id = embedding_id
        self._chunk_id = chunk_id
        self._book_id = book_id
        self._indexed_timestamp = indexed_timestamp
        self._model_identifier = model_identifier
        self._vector_dimension = vector_dimension
        self._persistence_status = persistence_status

    @property
    def embedding_id(self) -> EmbeddingId:
        return self._embedding_id

    @property
    def chunk_id(self) -> ChunkId:
        return self._chunk_id

    @property
    def book_id(self) -> BookId:
        return self._book_id

    @property
    def indexed_timestamp(self) -> datetime:
        return self._indexed_timestamp

    @property
    def model_identifier(self) -> str:
        return self._model_identifier

    @property
    def vector_dimension(self) -> int:
        return self._vector_dimension

    @property
    def persistence_status(self) -> str:
        return self._persistence_status


class KnowledgeIndex(ValueObject):
    """Aggregate representing the successfully persisted knowledge index state for a book."""

    def __init__(
        self,
        book_id: BookId,
        items: list[IndexRecord],
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
    def items(self) -> list[IndexRecord]:
        return self._items

    @property
    def statistics(self) -> dict[str, Any]:
        return self._statistics

    @property
    def metadata(self) -> dict[str, Any]:
        return self._metadata
