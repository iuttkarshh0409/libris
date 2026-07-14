from typing import Protocol

from src.domain.entities.context import RetrievalContext
from src.domain.entities.query import Query
from src.domain.value_objects.identifiers import BookId


class RetrievalEngine(Protocol):
    """Protocol defining similarity search ranking and context extraction responsibilities."""

    book_id: BookId

    def retrieve_context(
        self,
        query: Query,
        similarity_threshold: float | None = None,
        limit: int | None = None,
    ) -> RetrievalContext:
        """Performs search in the Knowledge Index to construct a RetrievalContext."""
        ...
