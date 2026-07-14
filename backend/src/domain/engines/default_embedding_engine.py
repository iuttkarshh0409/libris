import math
import uuid
from datetime import datetime

from loguru import logger

from src.domain.entities.chunk_collection import ChunkCollection
from src.domain.entities.embedding import Embedding
from src.domain.entities.embedding_collection import EmbeddingCollection
from src.domain.entities.query import Query
from src.domain.providers.embedding import EmbeddingProvider
from src.domain.value_objects.embedding import QueryEmbedding
from src.domain.value_objects.identifiers import EmbeddingId
from src.shared.exceptions import ValidationException


class DefaultEmbeddingEngine:
    """Concrete implementation of the EmbeddingEngine.

    Orchestrates the conversion of Chunk and Query entities into vector embeddings
    by consuming an underlying EmbeddingProvider.
    """

    def __init__(self, provider: EmbeddingProvider, model_name: str = "all-MiniLM-L6-v2") -> None:
        """Initializes the embedding engine with a provider and model name."""
        self.provider = provider
        self.model_name = model_name

    def embed_chunks(self, chunk_collection: ChunkCollection) -> EmbeddingCollection:
        """Generates Embedding entities for a list of document Chunks."""
        logger.info("Embedding generation started")

        try:
            # 1. Validation checks
            # 1a. Empty chunk collection
            if not chunk_collection.chunks:
                logger.error("Generation failed: Chunk collection is empty")
                raise ValidationException("Chunk collection is empty.")

            # 1b. Duplicate ChunkIds
            seen_chunk_ids = set()
            for chunk in chunk_collection.chunks:
                if chunk.id.value in seen_chunk_ids:
                    logger.error(f"Generation failed: Duplicate ChunkId found: {chunk.id.value}")
                    raise ValidationException(f"Duplicate ChunkId found: {chunk.id.value}")
                seen_chunk_ids.add(chunk.id.value)

            logger.info("Validation completed")

            # 2. Extract texts to be embedded
            texts = [chunk.chunk_text for chunk in chunk_collection.chunks]

            # 3. Request batch embeddings from the provider
            logger.info("Chunk batch submitted")
            batch_dto = self.provider.generate_embeddings(texts, model_name=self.model_name)

            # 4. Validate Provider DTO output
            # 4a. Missing vectors
            if not batch_dto.vectors:
                logger.error("Generation failed: Provider returned empty/missing vectors")
                raise ValidationException("Provider returned empty or missing vectors.")

            if len(batch_dto.vectors) != len(chunk_collection.chunks):
                logger.error(
                    f"Generation failed: Vector batch size mismatch. "
                    f"Expected {len(chunk_collection.chunks)}, got {len(batch_dto.vectors)}"
                )
                raise ValidationException("Vector count does not match chunk count.")

            # 4b. Inconsistent vector dimensions & missing individual vectors
            first_dim = batch_dto.vectors[0].dimension
            for idx, vec_dto in enumerate(batch_dto.vectors):
                if not vec_dto.vector:
                    logger.error(f"Generation failed: Missing vector at index {idx}")
                    raise ValidationException(f"Missing vector at index {idx}.")
                if vec_dto.dimension != first_dim:
                    logger.error(
                        f"Generation failed: Inconsistent vector dimension at index {idx}: "
                        f"expected {first_dim}, got {vec_dto.dimension}"
                    )
                    raise ValidationException(
                        f"Inconsistent vector dimension at index {idx}: "
                        f"expected {first_dim}, got {vec_dto.dimension}"
                    )
                if len(vec_dto.vector) != first_dim:
                    logger.error(
                        f"Generation failed: Inconsistent vector length at index {idx}: "
                        f"expected {first_dim}, got {len(vec_dto.vector)}"
                    )
                    raise ValidationException(
                        f"Inconsistent vector length at index {idx}: "
                        f"expected {first_dim}, got {len(vec_dto.vector)}"
                    )

            # 5. Map DTO results back to Domain Entities and validate Embedding ID uniqueness
            embeddings: list[Embedding] = []
            norms: list[float] = []
            seen_emb_ids = set()

            for chunk, vector_dto in zip(chunk_collection.chunks, batch_dto.vectors, strict=True):
                # Compute L2 norm for diagnostics
                norm = math.sqrt(sum(val * val for val in vector_dto.vector))
                norms.append(norm)

                emb_id_str = str(uuid.uuid4())
                if emb_id_str in seen_emb_ids:
                    logger.error(
                        f"Generation failed: Duplicate EmbeddingId generated: {emb_id_str}"
                    )
                    raise ValidationException(f"Duplicate EmbeddingId: {emb_id_str}")
                seen_emb_ids.add(emb_id_str)

                embedding_entity = Embedding(
                    id=EmbeddingId(emb_id_str),
                    chunk_id=chunk.id,
                    model_identifier=self.model_name,
                    vector_dimension=vector_dto.dimension,
                    embedding_vector=vector_dto.vector,
                    generated_timestamp=datetime.now(),
                )
                embeddings.append(embedding_entity)

            logger.info("Embedding entities created")

            # 6. Populate statistics & metadata
            avg_norm = sum(norms) / len(norms) if norms else 0.0
            avg_dim = (
                sum(v.dimension for v in batch_dto.vectors) / len(batch_dto.vectors)
                if batch_dto.vectors
                else 0.0
            )

            statistics: dict[str, int | float] = {
                "total_embeddings": len(embeddings),
                "embedding_dimension": first_dim,
                "average_vector_dimension": avg_dim,
                "generation_duration": batch_dto.processing_time,
                "average_vector_norm": avg_norm,
                "processing_time": batch_dto.processing_time,
            }

            avg_char_len = sum(len(t) for t in texts) / len(texts) if texts else 0.0
            metadata: dict[str, str | int | float | None] = {
                "model_identifier": self.model_name,
                "provider_name": self.provider.provider_name,
                "provider_version": self.provider.provider_version,
                "average_chunk_char_length": avg_char_len,
            }

            logger.info("Embedding collection assembled")

            return EmbeddingCollection(
                book_id=chunk_collection.book_id,
                embeddings=embeddings,
                statistics=statistics,
                metadata=metadata,
            )

        except Exception as e:
            if not isinstance(e, ValidationException):
                logger.error(f"Generation failed: {e!s}")
            raise

    def embed_query(self, query: Query) -> QueryEmbedding:
        """Generates a QueryEmbedding value object representing the query vector."""
        logger.info("Embedding generation started")

        try:
            # 1. Validation checks
            if not query.original_question or query.original_question.strip() == "":
                logger.error("Generation failed: Query text is empty or blank")
                raise ValidationException("Query text must not be empty or blank.")

            logger.info("Validation completed")

            # 2. Request query embedding from the provider
            logger.info("Chunk batch submitted")
            vector_dto = self.provider.generate_query_embedding(
                query.original_question, model_name=self.model_name
            )

            # Validate output
            if not vector_dto.vector:
                logger.error("Generation failed: Provider returned empty query vector")
                raise ValidationException("Provider returned empty query vector.")

            logger.info("Embedding entities created")
            logger.info("Embedding collection assembled")

            return QueryEmbedding(
                query_id=query.id,
                model_identifier=self.model_name,
                vector=vector_dto.vector,
            )

        except Exception as e:
            if not isinstance(e, ValidationException):
                logger.error(f"Generation failed: {e!s}")
            raise
