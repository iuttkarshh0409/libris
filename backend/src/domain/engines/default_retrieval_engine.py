import re
import time
from datetime import datetime
from typing import Any

from loguru import logger

from src.domain.engines.retrieval import RetrievalEngine
from src.domain.entities.context import RetrievalContext, RetrievedChunk
from src.domain.entities.query import Query
from src.domain.providers.embedding import EmbeddingProvider
from src.domain.providers.knowledge_index import KnowledgeIndexProvider
from src.domain.value_objects.identifiers import BookId, ChapterId, ChunkId, EmbeddingId, SectionId
from src.shared.exceptions import ValidationException


class DefaultRetrievalEngine(RetrievalEngine):
    """Concrete implementation of RetrievalEngine.

    Orchestrates the retrieval of knowledge chunks matching a semantic query
    by interacting with the EmbeddingProvider and KnowledgeIndexProvider.
    """

    def __init__(
        self,
        embedding_provider: EmbeddingProvider,
        index_provider: KnowledgeIndexProvider,
        book_id: BookId = BookId("default-book"),
        model_name: str = "all-MiniLM-L6-v2",
    ) -> None:
        """Initializes the retrieval engine with providers and settings."""
        self.embedding_provider = embedding_provider
        self.index_provider = index_provider
        self.book_id = book_id
        self.model_name = model_name

    def _get_collection_name(self, book_id: BookId) -> str:
        """Derives a safe ChromaDB collection name from the BookId."""
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

    def retrieve_context(
        self,
        query: Query,
        similarity_threshold: float | None = None,
        limit: int | None = None,
        filter_metadata: dict[str, Any] | None = None,
    ) -> RetrievalContext:
        """Performs search in the Knowledge Index to construct a RetrievalContext."""
        start_time = time.perf_counter()
        logger.info("Retrieval started")

        # 1. Validate Query
        if query is None:
            logger.error("Retrieval failed: Query is None")
            raise ValidationException("Query cannot be None.")

        if (
            not hasattr(query, "original_question")
            or not query.original_question
            or query.original_question.strip() == ""
        ):
            logger.error("Retrieval failed: Query text is empty or blank")
            raise ValidationException("Query text cannot be empty or blank.")

        # 2. Generate Query Embedding
        try:
            emb_vector_dto = self.embedding_provider.generate_query_embedding(
                query.original_question, model_name=self.model_name
            )
            query_vector = emb_vector_dto.vector
            model_identifier = emb_vector_dto.model_identifier
        except Exception as e:
            logger.error(f"Retrieval failed: Embedding generation error: {e!s}")
            raise
        logger.info("Query embedded")

        # 3. Query similarity search
        collection_name = self._get_collection_name(self.book_id)
        if not self.index_provider.has_collection(collection_name):
            logger.error(f"Retrieval failed: Collection {collection_name} does not exist")
            raise ValidationException(f"Collection '{collection_name}' does not exist.")

        search_limit = limit if limit is not None else 5
        if search_limit <= 0:
            raise ValidationException("Limit must be greater than zero.")

        try:
            search_batch = self.index_provider.query_similarity(
                collection_name=collection_name,
                vector=query_vector,
                limit=search_limit,
                filter_metadata=filter_metadata,
            )
        except Exception as e:
            logger.error(f"Retrieval failed: Vector search error: {e!s}")
            raise
        logger.info("Semantic search completed")

        # 4. Search Result Validation
        if not search_batch.results:
            logger.error("Retrieval failed: Search result list is empty")
            raise ValidationException("No search results found.")

        seen_chunk_ids = set()
        scores = []
        for res in search_batch.results:
            # Validate similarity score
            score = res.similarity_score
            if score is None or not isinstance(score, (int, float)) or score != score:  # NaN check
                logger.error(f"Retrieval failed: Invalid similarity score {score}")
                raise ValidationException("Invalid similarity score in search results.")
            scores.append(score)

            # Metadata validation
            meta = res.metadata
            if not meta or "chunk_id" not in meta:
                logger.error("Retrieval failed: Missing chunk_id in metadata")
                raise ValidationException("Missing chunk_id in result metadata.")

            chunk_id_val = meta["chunk_id"]
            if chunk_id_val in seen_chunk_ids:
                logger.error(f"Retrieval failed: Duplicate ChunkId found: {chunk_id_val}")
                raise ValidationException(
                    f"Duplicate ChunkId found in search results: {chunk_id_val}"
                )
            seen_chunk_ids.add(chunk_id_val)

        # Validate ranking consistency
        if len(scores) > 1:
            is_ascending = all(scores[i] <= scores[i + 1] for i in range(len(scores) - 1))
            is_descending = all(scores[i] >= scores[i + 1] for i in range(len(scores) - 1))
            if not (is_ascending or is_descending):
                logger.error("Retrieval failed: Ranking consistency check failed")
                raise ValidationException("Search results scores are not sorted consistently.")

        # 5. Filtering Candidates & Mapping
        retrieved_chunks = []
        rank = 1
        for res in search_batch.results:
            # Perform similarity threshold filtering if configured
            if similarity_threshold is not None and res.similarity_score < similarity_threshold:
                continue

            chunk_id_str = res.metadata["chunk_id"]
            emb_id_str = res.metadata.get("embedding_id") or res.identifier
            chunk_text = res.metadata.get("chunk_text") or ""
            page_num = res.metadata.get("page_number", 0)

            # Map chapter_id and section_id
            chapter_id_str = res.metadata.get("chapter_id")
            section_id_str = res.metadata.get("section_id")
            chapter_id = ChapterId(chapter_id_str) if chapter_id_str else None
            section_id = SectionId(section_id_str) if section_id_str else None

            retrieved_chunk = RetrievedChunk(
                chunk_id=ChunkId(chunk_id_str),
                embedding_id=EmbeddingId(emb_id_str),
                chunk_text=chunk_text,
                similarity_score=res.similarity_score,
                retrieval_rank=rank,
                page_number=page_num,
                chapter_id=chapter_id,
                section_id=section_id,
                retrieval_timestamp=datetime.now(),
            )
            retrieved_chunks.append(retrieved_chunk)
            rank += 1

        logger.info("Candidates filtered")

        # 6. Build statistics & metadata
        duration = time.perf_counter() - start_time
        avg_score = (
            sum(c.similarity_score for c in retrieved_chunks) / len(retrieved_chunks)
            if retrieved_chunks
            else 0.0
        )

        stats = {
            "total_candidates": search_batch.total_candidates,
            "retrieved_chunks": len(retrieved_chunks),
            "average_similarity": avg_score,
            "retrieval_duration": duration,
        }

        meta = {
            "model_identifier": model_identifier,
            "collection_name": collection_name,
            "provider_name": self.index_provider.provider_name,
            "provider_version": self.index_provider.provider_version,
        }

        logger.info("RetrievalContext assembled")
        logger.info("Retrieval completed")

        return RetrievalContext(
            book_id=self.book_id,
            items=retrieved_chunks,
            statistics=stats,
            metadata=meta,
        )
