from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class EmbeddingVector:
    """Infrastructure DTO representing a single generated embedding vector."""

    vector: list[float]
    dimension: int
    model_identifier: str


@dataclass(frozen=True)
class EmbeddingBatch:
    """Infrastructure DTO representing a batch of generated embedding vectors."""

    vectors: list[EmbeddingVector]
    processing_time: float
    model_identifier: str


class EmbeddingProvider(Protocol):
    """Abstraction interface for semantic vector embedding generation models."""

    @property
    def provider_name(self) -> str:
        """Name of the underlying provider."""
        ...

    @property
    def provider_version(self) -> str:
        """Version of the underlying provider."""
        ...

    def generate_embeddings(self, texts: list[str], model_name: str) -> EmbeddingBatch:
        """Generates embedding DTO for a batch of text inputs."""
        ...

    def generate_query_embedding(self, query_text: str, model_name: str) -> EmbeddingVector:
        """Generates an embedding DTO for a single query text."""
        ...
