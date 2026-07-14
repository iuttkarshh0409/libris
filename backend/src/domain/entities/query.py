from datetime import datetime

from src.domain.value_objects.identifiers import QueryId
from src.shared.domain.base import BaseEntity


class Query(BaseEntity):
    """Represents a question submitted by the user."""

    def __init__(self, id: QueryId, original_question: str, query_timestamp: datetime) -> None:
        super().__init__(id)
        self._original_question = original_question
        self._query_timestamp = query_timestamp

    @property
    def id(self) -> QueryId:
        assert isinstance(self._id, QueryId)
        return self._id

    @property
    def original_question(self) -> str:
        return self._original_question

    @property
    def query_timestamp(self) -> datetime:
        return self._query_timestamp
