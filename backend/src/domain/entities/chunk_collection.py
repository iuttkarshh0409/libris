from src.domain.entities.chunk import Chunk
from src.domain.value_objects.identifiers import BookId
from src.shared.domain.base import ValueObject


class ChunkCollection(ValueObject):
    """A technical aggregate packaging the collection of Chunk entities generated for a Book."""

    def __init__(
        self,
        book_id: BookId,
        chunks: list[Chunk],
        statistics: dict[str, int | float],
        metadata: dict[str, str | int | float | None],
    ) -> None:
        self._book_id = book_id
        self._chunks = chunks
        self._statistics = statistics
        self._metadata = metadata

    @property
    def book_id(self) -> BookId:
        return self._book_id

    @property
    def chunks(self) -> list[Chunk]:
        return self._chunks

    @property
    def items(self) -> list[Chunk]:
        return self._chunks

    @property
    def total_chunks(self) -> int:
        return len(self._chunks)

    @property
    def statistics(self) -> dict[str, int | float]:
        return self._statistics

    @property
    def metadata(self) -> dict[str, str | int | float | None]:
        return self._metadata
