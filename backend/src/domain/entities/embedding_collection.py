from src.domain.entities.embedding import Embedding
from src.domain.value_objects.identifiers import BookId
from src.shared.domain.base import ValueObject


class EmbeddingCollection(ValueObject):
    """An aggregate wrapping the collection of Embedding entities generated for a Book."""

    def __init__(
        self,
        book_id: BookId,
        embeddings: list[Embedding],
        statistics: dict[str, int | float],
        metadata: dict[str, str | int | float | None],
    ) -> None:
        self._book_id = book_id
        self._embeddings = embeddings
        self._statistics = statistics
        self._metadata = metadata

    @property
    def book_id(self) -> BookId:
        return self._book_id

    @property
    def embeddings(self) -> list[Embedding]:
        return self._embeddings

    @property
    def items(self) -> list[Embedding]:
        return self._embeddings

    @property
    def total_embeddings(self) -> int:
        return len(self._embeddings)

    @property
    def statistics(self) -> dict[str, int | float]:
        return self._statistics

    @property
    def metadata(self) -> dict[str, str | int | float | None]:
        return self._metadata
