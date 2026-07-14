import re
import time
from datetime import datetime
from typing import Any

from loguru import logger

from src.domain.engines.indexing import IndexingEngine
from src.domain.entities.chunk_collection import ChunkCollection
from src.domain.entities.embedding_collection import EmbeddingCollection
from src.domain.entities.knowledge_index import IndexRecord, KnowledgeIndex
from src.domain.providers.knowledge_index import IndexedVector, KnowledgeIndexProvider
from src.domain.value_objects.identifiers import BookId
from src.shared.exceptions import ValidationException


class DefaultIndexingEngine(IndexingEngine):
    """Concrete implementation of the IndexingEngine.

    Orchestrates the persistence of document embeddings into the vector store
    by consuming an underlying KnowledgeIndexProvider.
    """

    def __init__(
        self,
        provider: KnowledgeIndexProvider,
        collection_name_override: str | None = None,
    ) -> None:
        """Initializes the indexing engine with a provider and optional collection override."""
        self.provider = provider
        self.collection_name_override = collection_name_override

    def _get_collection_name(self, book_id: BookId) -> str:
        """Derives a safe ChromaDB collection name from the BookId."""
        if self.collection_name_override:
            return self.collection_name_override

        # Replace non-alphanumeric/underscore/hyphen characters with underscores
        clean_name = re.sub(r"[^a-zA-Z0-9_-]", "_", book_id.value)

        # Pad if too short
        if len(clean_name) < 3:
            clean_name = f"col_{clean_name}"
        # Truncate if too long
        if len(clean_name) > 60:
            clean_name = clean_name[:60]

        # Ensure starts and ends with alphanumeric characters
        clean_name = re.sub(r"^[^a-zA-Z0-9]+", "", clean_name)
        clean_name = re.sub(r"[^a-zA-Z0-9]+$", "", clean_name)

        if len(clean_name) < 3:
            clean_name = "collection_" + clean_name

        return clean_name

    def add_to_index(
        self, chunk_collection: ChunkCollection, embedding_collection: EmbeddingCollection
    ) -> KnowledgeIndex:
        """Stores knowledge chunks and associated embedding vectors into the index."""
        logger.info("Indexing started")

        # 1. Validation checks
        # 1a. Empty EmbeddingCollection
        if not embedding_collection.embeddings:
            logger.error("Indexing failed: Embedding collection is empty")
            raise ValidationException("Embedding collection is empty.")

        # 1b. Empty ChunkCollection
        if not chunk_collection.chunks:
            logger.error("Indexing failed: Chunk collection is empty")
            raise ValidationException("Chunk collection is empty.")

        # 1c. Length mismatch
        if len(chunk_collection.chunks) != len(embedding_collection.embeddings):
            logger.error("Indexing failed: Chunk and embedding count mismatch")
            raise ValidationException("Chunk and embedding count mismatch.")

        # 1d. Duplicate EmbeddingIds
        seen_emb_ids = set()
        for emb in embedding_collection.embeddings:
            if emb.id.value in seen_emb_ids:
                logger.error(f"Indexing failed: Duplicate EmbeddingId found: {emb.id.value}")
                raise ValidationException(f"Duplicate EmbeddingId found: {emb.id.value}")
            seen_emb_ids.add(emb.id.value)

        # 1e. Duplicate ChunkIds
        seen_chunk_ids = set()
        for chunk in chunk_collection.chunks:
            if chunk.id.value in seen_chunk_ids:
                logger.error(f"Indexing failed: Duplicate ChunkId found: {chunk.id.value}")
                raise ValidationException(f"Duplicate ChunkId found: {chunk.id.value}")
            seen_chunk_ids.add(chunk.id.value)

        # 1f. Inconsistent dimensions
        first_dim = None
        for emb in embedding_collection.embeddings:
            if first_dim is None:
                first_dim = emb.vector_dimension
            elif emb.vector_dimension != first_dim:
                logger.error(
                    f"Indexing failed: Inconsistent dimension: expected {first_dim}, "
                    f"got {emb.vector_dimension} for embedding {emb.id.value}"
                )
                raise ValidationException(
                    f"Inconsistent dimension: expected {first_dim}, "
                    f"got {emb.vector_dimension} for embedding {emb.id.value}"
                )

        logger.info("Validation completed")

        # 2. Derive collection name and ensure it exists
        book_id = embedding_collection.book_id
        collection_name = self._get_collection_name(book_id)
        if not self.provider.has_collection(collection_name):
            self.provider.create_collection(collection_name)

        # 3. Construct IndexedVector batch with metadata propagation
        indexed_vectors = []
        for i in range(len(embedding_collection.embeddings)):
            embedding = embedding_collection.embeddings[i]
            chunk = chunk_collection.chunks[i]

            # Enforce relationship integrity (Nth embedding corresponds to Nth chunk)
            if embedding.chunk_id != chunk.id:
                logger.error(
                    f"Indexing failed: Relationship mismatch at index {i}: "
                    f"embedding points to chunk {embedding.chunk_id.value}, "
                    f"but chunk list has {chunk.id.value}."
                )
                raise ValidationException(
                    f"Relationship mismatch at index {i}: "
                    f"embedding points to chunk {embedding.chunk_id.value}, "
                    f"but chunk list has {chunk.id.value}."
                )

            # Metadata propagation
            vector_metadata: dict[str, Any] = {
                "embedding_id": embedding.id.value,
                "chunk_id": chunk.id.value,
                "book_id": chunk.book_id.value,
                "page_number": chunk.page_number,
                "model_identifier": embedding.model_identifier,
                "chunk_text": chunk.chunk_text,
            }
            if chunk.chapter_id:
                vector_metadata["chapter_id"] = chunk.chapter_id.value
            if chunk.section_id:
                vector_metadata["section_id"] = chunk.section_id.value

            indexed_vectors.append(
                IndexedVector(
                    identifier=embedding.id.value,
                    vector=embedding.embedding_vector,
                    metadata=vector_metadata,
                )
            )

        logger.info("Embedding batch submitted")
        start_time = time.perf_counter()

        # 4. Batch persistence call to the provider
        try:
            self.provider.add_vectors(collection_name, indexed_vectors)
        except Exception as e:
            logger.error(f"Indexing failed: Provider error: {e!s}")
            raise

        duration = time.perf_counter() - start_time
        logger.info("Index records created")

        # 5. Build IndexRecord entities
        records = []
        for emb in embedding_collection.embeddings:
            records.append(
                IndexRecord(
                    embedding_id=emb.id,
                    chunk_id=emb.chunk_id,
                    book_id=book_id,
                    indexed_timestamp=datetime.now(),
                    model_identifier=emb.model_identifier,
                    vector_dimension=emb.vector_dimension,
                    persistence_status="success",
                )
            )

        # 6. Generate statistics and metadata
        stats = {
            "total_records": len(records),
            "indexed_records": len(records),
            "failed_records": 0,
            "indexing_duration": duration,
            "average_dimension": float(first_dim) if first_dim is not None else 0.0,
        }

        meta = {
            "collection_name": collection_name,
            "provider_name": self.provider.provider_name,
            "provider_version": self.provider.provider_version,
            "model_identifier": (
                embedding_collection.embeddings[0].model_identifier
                if embedding_collection.embeddings
                else "Unknown"
            ),
        }

        # Assemble and return KnowledgeIndex aggregate
        logger.info("KnowledgeIndex assembled")
        return KnowledgeIndex(
            book_id=book_id,
            items=records,
            statistics=stats,
            metadata=meta,
        )

    def delete_book_from_index(self, book_id: BookId) -> None:
        """Removes all index entries related to the given Book ID."""
        logger.info("Deleting book from index")
        collection_name = self._get_collection_name(book_id)
        if self.provider.has_collection(collection_name):
            try:
                self.provider.delete_vectors(
                    collection_name, filter_metadata={"book_id": book_id.value}
                )
            except Exception as e:
                logger.error(f"Deletion failed: {e!s}")
                raise
