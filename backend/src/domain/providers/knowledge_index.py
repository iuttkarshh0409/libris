from dataclasses import dataclass
from typing import Any, Protocol


@dataclass(frozen=True)
class IndexedVector:
    """Infrastructure DTO representing a single stored embedding vector and metadata."""

    identifier: str
    vector: list[float]
    metadata: dict[str, Any]


@dataclass(frozen=True)
class SearchResult:
    """Infrastructure DTO representing a single search result match."""

    identifier: str
    similarity_score: float
    metadata: dict[str, Any]


@dataclass(frozen=True)
class SearchBatch:
    """Infrastructure DTO representing search results batch."""

    results: list[SearchResult]
    search_duration: float
    total_candidates: int


@dataclass(frozen=True)
class CollectionStatistics:
    """Infrastructure DTO representing the vector storage statistics."""

    collection_name: str
    total_vectors: int
    embedding_dimension: int
    provider_version: str


class KnowledgeIndexProvider(Protocol):
    """Abstraction interface for storage and querying of the Knowledge Index."""

    @property
    def provider_name(self) -> str:
        """Name of the underlying provider."""
        ...

    @property
    def provider_version(self) -> str:
        """Version of the underlying provider."""
        ...

    def create_collection(self, collection_name: str) -> None:
        """Creates a collection with the given name."""
        ...

    def delete_collection(self, collection_name: str) -> None:
        """Deletes a collection with the given name."""
        ...

    def has_collection(self, collection_name: str) -> bool:
        """Checks if a collection exists."""
        ...

    def add_vectors(self, collection_name: str, vectors: list[IndexedVector]) -> None:
        """Adds a batch of vectors and their metadata to the named collection."""
        ...

    def update_vectors(self, collection_name: str, vectors: list[IndexedVector]) -> None:
        """Updates existing vectors in the named collection."""
        ...

    def delete_vectors(
        self,
        collection_name: str,
        identifiers: list[str] | None = None,
        filter_metadata: dict[str, Any] | None = None,
    ) -> None:
        """Deletes vectors from the named collection by identifiers or metadata filter."""
        ...

    def query_similarity(
        self,
        collection_name: str,
        vector: list[float],
        limit: int,
        filter_metadata: dict[str, Any] | None = None,
    ) -> SearchBatch:
        """Queries the vector index for nodes matching the query vector."""
        ...

    def get_statistics(self, collection_name: str) -> CollectionStatistics:
        """Gets statistics for the named collection."""
        ...

    def reset_index(self) -> None:
        """Resets the entire database/index (development only)."""
        ...
