from typing import Protocol

from src.domain.entities.chunk_collection import ChunkCollection
from src.domain.entities.embedding_collection import EmbeddingCollection
from src.domain.entities.query import Query
from src.domain.value_objects.embedding import QueryEmbedding


class EmbeddingEngine(Protocol):
    """Protocol defining text-to-vector embedding generation responsibilities."""

    def embed_chunks(self, chunk_collection: ChunkCollection) -> EmbeddingCollection:
        """Generates Embedding entities for a list of document Chunks."""
        ...

    def embed_query(self, query: Query) -> QueryEmbedding:
        """Generates a QueryEmbedding value object representing the query vector."""
        ...
