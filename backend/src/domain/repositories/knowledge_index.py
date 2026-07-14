from typing import Protocol

from src.domain.entities.chunk import Chunk
from src.domain.entities.embedding import Embedding
from src.domain.value_objects.identifiers import BookId
from src.domain.value_objects.retrieval import RetrievalResult


class KnowledgeIndexRepository(Protocol):
    """Protocol defining persistence operations for vector indexing and similarity retrieval."""

    def add(self, chunks: list[Chunk], embeddings: list[Embedding]) -> None:
        """Stores document chunks and embedding vectors into the index."""
        ...

    def delete_by_book_id(self, book_id: BookId) -> None:
        """Removes all indexed nodes associated with the BookId."""
        ...

    def search_similarity(self, query_vector: list[float], limit: int) -> list[RetrievalResult]:
        """Queries the vector index for node matches based on the query vector."""
        ...
