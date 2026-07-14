from datetime import datetime

from src.domain.value_objects.identifiers import ChunkId, EmbeddingId
from src.shared.domain.base import BaseEntity


class Embedding(BaseEntity):
    """Represents the vector representation of a single knowledge chunk."""

    def __init__(
        self,
        id: EmbeddingId,
        chunk_id: ChunkId,
        model_identifier: str,
        vector_dimension: int,
        embedding_vector: list[float],
        generated_timestamp: datetime,
    ) -> None:
        super().__init__(id)
        self._chunk_id = chunk_id
        self._model_identifier = model_identifier
        self._vector_dimension = vector_dimension
        self._embedding_vector = embedding_vector
        self._generated_timestamp = generated_timestamp

    @property
    def id(self) -> EmbeddingId:
        assert isinstance(self._id, EmbeddingId)
        return self._id

    @property
    def chunk_id(self) -> ChunkId:
        return self._chunk_id

    @property
    def model_identifier(self) -> str:
        return self._model_identifier

    @property
    def vector_dimension(self) -> int:
        return self._vector_dimension

    @property
    def embedding_vector(self) -> list[float]:
        return self._embedding_vector

    @property
    def generated_timestamp(self) -> datetime:
        return self._generated_timestamp
