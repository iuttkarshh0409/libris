from src.domain.value_objects.identifiers import ChunkId
from src.shared.domain.base import ValueObject


class RetrievalResult(ValueObject):
    """Represents a single retrieved chunk with its similarity rating."""

    def __init__(self, chunk_id: ChunkId, similarity_score: float, rank: int) -> None:
        self._chunk_id = chunk_id
        self._similarity_score = similarity_score
        self._rank = rank

    @property
    def chunk_id(self) -> ChunkId:
        return self._chunk_id

    @property
    def similarity_score(self) -> float:
        return self._similarity_score

    @property
    def rank(self) -> int:
        return self._rank
