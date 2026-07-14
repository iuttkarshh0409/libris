from typing import Protocol

from src.domain.entities.chunk_collection import ChunkCollection
from src.domain.entities.embedding_collection import EmbeddingCollection
from src.domain.entities.knowledge_index import KnowledgeIndex
from src.domain.value_objects.identifiers import BookId


class IndexingEngine(Protocol):
    """Protocol defining knowledge index registration and lifecycle responsibilities."""

    def add_to_index(
        self, chunk_collection: ChunkCollection, embedding_collection: EmbeddingCollection
    ) -> KnowledgeIndex:
        """Stores knowledge chunks and associated embedding vectors into the index."""
        ...

    def delete_book_from_index(self, book_id: BookId) -> None:
        """Removes all index entries related to the given Book ID."""
        ...
