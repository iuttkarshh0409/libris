import time
from typing import Any

import chromadb
from chromadb.config import Settings
from loguru import logger

from src.domain.providers.knowledge_index import (
    CollectionStatistics,
    IndexedVector,
    KnowledgeIndexProvider,
    SearchBatch,
    SearchResult,
)
from src.shared.exceptions import ProviderException, ValidationException


class ChromaDBProvider(KnowledgeIndexProvider):
    """Concrete implementation of KnowledgeIndexProvider using ChromaDB."""

    def __init__(self, persist_directory: str | None = None) -> None:
        """Initializes the provider. Client initialization is lazy."""
        self._persist_directory = persist_directory
        self._client: Any = None

    def _get_client(self) -> Any:
        """Lazily initializes the ChromaDB client."""
        if self._client is None:
            settings = Settings(allow_reset=True)
            try:
                if self._persist_directory:
                    self._client = chromadb.PersistentClient(
                        path=self._persist_directory, settings=settings
                    )
                else:
                    self._client = chromadb.EphemeralClient(settings=settings)
            except Exception as e:
                raise ProviderException(f"Failed to initialize ChromaDB client: {e!s}") from e
        return self._client

    def _get_collection(self, collection_name: str) -> Any:
        """Retrieves collection lazily, raising ValidationException if missing."""
        client = self._get_client()
        try:
            collection = client.get_collection(name=collection_name)
            logger.info("Collection opened")
            return collection
        except Exception as e:
            raise ValidationException(f"Collection '{collection_name}' does not exist.") from e

    @property
    def provider_name(self) -> str:
        return "ChromaDB"

    @property
    def provider_version(self) -> str:
        return getattr(chromadb, "__version__", "Unknown")

    def create_collection(self, collection_name: str) -> None:
        """Creates a collection with the given name."""
        if not collection_name or collection_name.strip() == "":
            raise ValidationException("Collection name must not be empty.")

        client = self._get_client()
        try:
            # Check if collection already exists
            existing_names = [c.name for c in client.list_collections()]
            if collection_name in existing_names:
                raise ValidationException(f"Collection '{collection_name}' already exists.")

            client.create_collection(name=collection_name, metadata={"hnsw:space": "cosine"})
            logger.info("Collection created")
        except Exception as e:
            if isinstance(e, ValidationException):
                raise
            raise ProviderException(
                f"Failed to create collection '{collection_name}': {e!s}"
            ) from e

    def delete_collection(self, collection_name: str) -> None:
        """Deletes a collection with the given name."""
        if not collection_name or collection_name.strip() == "":
            raise ValidationException("Collection name must not be empty.")

        client = self._get_client()
        try:
            existing_names = [c.name for c in client.list_collections()]
            if collection_name not in existing_names:
                raise ValidationException(f"Collection '{collection_name}' does not exist.")

            client.delete_collection(name=collection_name)
        except Exception as e:
            if isinstance(e, ValidationException):
                raise
            raise ProviderException(
                f"Failed to delete collection '{collection_name}': {e!s}"
            ) from e

    def has_collection(self, collection_name: str) -> bool:
        """Checks if a collection exists."""
        if not collection_name or collection_name.strip() == "":
            return False

        client = self._get_client()
        try:
            existing_names = [c.name for c in client.list_collections()]
            return collection_name in existing_names
        except Exception:
            return False

    def add_vectors(self, collection_name: str, vectors: list[IndexedVector]) -> None:
        """Adds a batch of vectors and their metadata to the named collection."""
        collection = self._get_collection(collection_name)

        if not vectors:
            raise ValidationException("Vector list must not be empty.")

        seen_ids = set()
        first_dim = None

        # Gather collection's existing dimension if not empty
        existing_dim = None
        try:
            peeked = collection.peek(limit=1)
            if peeked and peeked.get("embeddings") is not None:
                if len(peeked["embeddings"]) > 0:
                    existing_dim = len(peeked["embeddings"][0])
        except Exception:
            pass

        # Validate vectors
        for idx, v in enumerate(vectors):
            if not v.identifier or v.identifier.strip() == "":
                raise ValidationException(f"Missing identifier at index {idx}.")
            if v.identifier in seen_ids:
                raise ValidationException(f"Duplicate identifier in batch: {v.identifier}")
            seen_ids.add(v.identifier)

            if not v.vector:
                raise ValidationException(f"Empty or missing vector for identifier {v.identifier}.")

            dim = len(v.vector)
            if first_dim is None:
                first_dim = dim
            elif dim != first_dim:
                raise ValidationException(
                    f"Dimension mismatch in batch: expected {first_dim}, "
                    f"got {dim} for vector {v.identifier}."
                )

            if existing_dim is not None and dim != existing_dim:
                raise ValidationException(
                    f"Vector dimension {dim} does not match collection dimension {existing_dim}."
                )

            if not v.metadata:
                raise ValidationException(f"Missing metadata for identifier {v.identifier}.")

            # Validate required metadata fields
            required_keys = {
                "embedding_id",
                "chunk_id",
                "book_id",
                "page_number",
                "chapter_id",
                "section_id",
                "model_identifier",
            }
            for key in required_keys:
                if key not in v.metadata:
                    raise ValidationException(
                        f"Missing required metadata key '{key}' for vector {v.identifier}."
                    )

        # Prepare for bulk insert
        ids = [v.identifier for v in vectors]
        embeddings = [v.vector for v in vectors]
        metadatas = [v.metadata for v in vectors]

        try:
            # Check for duplicate IDs already in collection
            existing = collection.get(ids=ids)
            if existing and existing.get("ids"):
                raise ValidationException(
                    f"One or more identifiers already exist in the index: {existing['ids']}"
                )

            collection.add(ids=ids, embeddings=embeddings, metadatas=metadatas)
            logger.info("Batch inserted")
        except Exception as e:
            if isinstance(e, ValidationException):
                raise
            raise ProviderException(f"Failed to add vectors to '{collection_name}': {e!s}") from e

    def update_vectors(self, collection_name: str, vectors: list[IndexedVector]) -> None:
        """Updates existing vectors in the named collection."""
        collection = self._get_collection(collection_name)

        if not vectors:
            raise ValidationException("Vector list must not be empty.")

        seen_ids = set()
        first_dim = None

        # Validate vectors
        for idx, v in enumerate(vectors):
            if not v.identifier or v.identifier.strip() == "":
                raise ValidationException(f"Missing identifier at index {idx}.")
            if v.identifier in seen_ids:
                raise ValidationException(f"Duplicate identifier in batch: {v.identifier}")
            seen_ids.add(v.identifier)

            if not v.vector:
                raise ValidationException(f"Empty or missing vector for identifier {v.identifier}.")

            dim = len(v.vector)
            if first_dim is None:
                first_dim = dim
            elif dim != first_dim:
                raise ValidationException(
                    f"Dimension mismatch in batch: expected {first_dim}, "
                    f"got {dim} for vector {v.identifier}."
                )

            if not v.metadata:
                raise ValidationException(f"Missing metadata for identifier {v.identifier}.")

            # Validate required metadata fields
            required_keys = {
                "embedding_id",
                "chunk_id",
                "book_id",
                "page_number",
                "chapter_id",
                "section_id",
                "model_identifier",
            }
            for key in required_keys:
                if key not in v.metadata:
                    raise ValidationException(
                        f"Missing required metadata key '{key}' for vector {v.identifier}."
                    )

        ids = [v.identifier for v in vectors]
        embeddings = [v.vector for v in vectors]
        metadatas = [v.metadata for v in vectors]

        try:
            # Assert all IDs exist in collection (unsupported updates on non-existent vectors)
            existing = collection.get(ids=ids)
            if not existing or len(existing.get("ids", [])) != len(ids):
                found_ids = set(existing.get("ids", [])) if existing else set()
                missing_ids = [i for i in ids if i not in found_ids]
                raise ValidationException(
                    f"Cannot update non-existent vector identifiers: {missing_ids}"
                )

            collection.update(ids=ids, embeddings=embeddings, metadatas=metadatas)
        except Exception as e:
            if isinstance(e, ValidationException):
                raise
            raise ProviderException(
                f"Failed to update vectors in '{collection_name}': {e!s}"
            ) from e

    def delete_vectors(
        self,
        collection_name: str,
        identifiers: list[str] | None = None,
        filter_metadata: dict[str, Any] | None = None,
    ) -> None:
        """Deletes vectors from the named collection by identifiers or metadata filter."""
        collection = self._get_collection(collection_name)

        if not identifiers and not filter_metadata:
            raise ValidationException(
                "Must specify either identifiers or filter_metadata for deletion."
            )

        try:
            collection.delete(ids=identifiers, where=filter_metadata)
            logger.info("Vector deleted")
        except Exception as e:
            raise ProviderException(
                f"Failed to delete vectors from '{collection_name}': {e!s}"
            ) from e

    def query_similarity(
        self,
        collection_name: str,
        vector: list[float],
        limit: int,
        filter_metadata: dict[str, Any] | None = None,
    ) -> SearchBatch:
        """Queries the vector index for nodes matching the query vector."""
        collection = self._get_collection(collection_name)

        if not vector:
            raise ValidationException("Query vector must not be empty.")
        if limit <= 0:
            raise ValidationException("Query limit must be greater than zero.")

        start_time = time.perf_counter()
        try:
            results = collection.query(
                query_embeddings=[vector],
                n_results=limit,
                where=filter_metadata,
            )
            duration = time.perf_counter() - start_time
            logger.info("Search executed")

            search_results: list[SearchResult] = []
            if results and results.get("ids") and len(results["ids"][0]) > 0:
                ids = results["ids"][0]
                has_dists = bool(results.get("distances"))
                has_metas = bool(results.get("metadatas"))
                distances = results["distances"][0] if has_dists else [0.0] * len(ids)
                metadatas = results["metadatas"][0] if has_metas else [{}] * len(ids)

                for idx in range(len(ids)):
                    # Cosine similarity = 1.0 - Cosine distance
                    cosine_distance = distances[idx]
                    similarity_score = 1.0 - cosine_distance
                    search_results.append(
                        SearchResult(
                            identifier=ids[idx],
                            similarity_score=similarity_score,
                            metadata=metadatas[idx] or {},
                        )
                    )

            total_candidates = collection.count()

            return SearchBatch(
                results=search_results,
                search_duration=duration,
                total_candidates=total_candidates,
            )
        except Exception as e:
            raise ProviderException(f"Query execution failure in '{collection_name}': {e!s}") from e

    def get_statistics(self, collection_name: str) -> CollectionStatistics:
        """Gets statistics for the named collection."""
        collection = self._get_collection(collection_name)

        try:
            total_vectors = collection.count()
            logger.info("Collection statistics queried")

            # Determine dimension by peeking
            dimension = 0
            peeked = collection.peek(limit=1)
            has_embs = peeked and peeked.get("embeddings") is not None
            if has_embs and len(peeked["embeddings"]) > 0:
                dimension = len(peeked["embeddings"][0])

            return CollectionStatistics(
                collection_name=collection_name,
                total_vectors=total_vectors,
                embedding_dimension=dimension,
                provider_version=self.provider_version,
            )
        except Exception as e:
            raise ProviderException(
                f"Failed to get statistics for '{collection_name}': {e!s}"
            ) from e

    def reset_index(self) -> None:
        """Resets the entire database/index (development only)."""
        client = self._get_client()
        try:
            client.reset()
        except Exception as e:
            raise ProviderException(f"Failed to reset ChromaDB index: {e!s}") from e
