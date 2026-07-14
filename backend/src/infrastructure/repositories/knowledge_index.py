from src.domain.entities.chunk import Chunk
from src.domain.entities.embedding import Embedding
from src.domain.repositories.knowledge_index import KnowledgeIndexRepository
from src.domain.value_objects.identifiers import BookId
from src.domain.value_objects.retrieval import RetrievalResult


class VectorKnowledgeIndexRepository(KnowledgeIndexRepository):
    """Concrete vector implementation of KnowledgeIndexRepository (placeholder)."""

    def add(self, chunks: list[Chunk], embeddings: list[Embedding]) -> None:
        raise NotImplementedError("VectorKnowledgeIndexRepository.add is not implemented.")

    def delete_by_book_id(self, book_id: BookId) -> None:
        raise NotImplementedError(
            "VectorKnowledgeIndexRepository.delete_by_book_id is not implemented."
        )

    def search_similarity(self, query_vector: list[float], limit: int) -> list[RetrievalResult]:
        raise NotImplementedError(
            "VectorKnowledgeIndexRepository.search_similarity is not implemented."
        )
