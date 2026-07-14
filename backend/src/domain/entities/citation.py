from src.domain.value_objects.identifiers import ChunkId, CitationId, EmbeddingId
from src.shared.domain.base import BaseEntity


class Citation(BaseEntity):
    """Traceable evidence supporting part of a generated response."""

    def __init__(
        self,
        id: CitationId,
        book_title: str,
        page_number: int,
        chunk_reference: ChunkId,
        chapter: str | None = None,
        section: str | None = None,
        embedding_id: EmbeddingId | None = None,
        retrieval_rank: int | None = None,
        similarity_score: float | None = None,
    ) -> None:
        super().__init__(id)
        self._book_title = book_title
        self._page_number = page_number
        self._chunk_reference = chunk_reference
        self._chapter = chapter
        self._section = section
        self._embedding_id = embedding_id
        self._retrieval_rank = retrieval_rank
        self._similarity_score = similarity_score

    @property
    def id(self) -> CitationId:
        assert isinstance(self._id, CitationId)
        return self._id

    @property
    def book_title(self) -> str:
        return self._book_title

    @property
    def page_number(self) -> int:
        return self._page_number

    @property
    def chunk_reference(self) -> ChunkId:
        return self._chunk_reference

    @property
    def chapter(self) -> str | None:
        return self._chapter

    @property
    def section(self) -> str | None:
        return self._section

    @property
    def embedding_id(self) -> EmbeddingId | None:
        return self._embedding_id

    @property
    def retrieval_rank(self) -> int | None:
        return self._retrieval_rank

    @property
    def similarity_score(self) -> float | None:
        return self._similarity_score
