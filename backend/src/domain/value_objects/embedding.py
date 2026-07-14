from src.domain.value_objects.identifiers import QueryId
from src.shared.domain.base import ValueObject


class QueryEmbedding(ValueObject):
    """Semantic vector representation of a Query (transient)."""

    def __init__(self, query_id: QueryId, model_identifier: str, vector: list[float]) -> None:
        self._query_id = query_id
        self._model_identifier = model_identifier
        self._vector = vector

    @property
    def query_id(self) -> QueryId:
        return self._query_id

    @property
    def model_identifier(self) -> str:
        return self._model_identifier

    @property
    def vector(self) -> list[float]:
        return self._vector
