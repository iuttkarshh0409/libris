import time
from typing import ClassVar

from loguru import logger
from sentence_transformers import SentenceTransformer

from src.domain.providers.embedding import EmbeddingProvider
from src.infrastructure.providers.embedding.models import EmbeddingBatch, EmbeddingVector
from src.shared.exceptions import ProviderException, ValidationException


class SentenceTransformerProvider(EmbeddingProvider):
    """Concrete implementation of EmbeddingProvider using SentenceTransformers."""

    # Thread-safe cached models at class level (singleton per model name)
    _shared_models: ClassVar[dict[str, SentenceTransformer]] = {}

    def __init__(self, max_batch_size: int = 512) -> None:
        """Initializes the provider with a configurable max batch size."""
        self.max_batch_size = max_batch_size

    @property
    def provider_name(self) -> str:
        return "SentenceTransformers"

    @property
    def provider_version(self) -> str:
        import sentence_transformers

        return getattr(sentence_transformers, "__version__", "Unknown")

    def _get_model(self, model_name: str) -> SentenceTransformer:
        """Lazily loads and caches the SentenceTransformer model (singleton)."""
        if not model_name or model_name.strip() == "":
            raise ValidationException("Model name must not be empty.")

        if model_name not in self._shared_models:
            logger.info(f"Model loading initiated for model: '{model_name}'")
            try:
                # Load the model deterministically (will select CPU/GPU automatically)
                model = SentenceTransformer(model_name)
                # Verify it loaded correctly
                _ = model.get_embedding_dimension()
                self._shared_models[model_name] = model
                logger.info(f"Model loaded successfully: '{model_name}'")
            except Exception as e:
                logger.error(f"Model initialization failure for '{model_name}': {e!s}")
                raise ProviderException(f"Failed to initialize model '{model_name}': {e!s}") from e

        return self._shared_models[model_name]

    def generate_embeddings(self, texts: list[str], model_name: str) -> EmbeddingBatch:
        """Generates embedding DTO for a batch of text inputs."""
        logger.info(f"Batch embedding requested for {len(texts)} texts using model '{model_name}'")

        # 1. Validation checks
        if not texts:
            raise ValidationException("Input texts list must not be empty.")

        if len(texts) > self.max_batch_size:
            logger.error(f"Batch size {len(texts)} exceeds maximum allowed {self.max_batch_size}")
            raise ValidationException(
                f"Batch size {len(texts)} exceeds maximum allowed {self.max_batch_size}."
            )

        for i, text in enumerate(texts):
            if text is None or text.strip() == "":
                raise ValidationException(
                    f"Text at index {i} is empty or blank. All batch inputs must be valid text."
                )

        # 2. Retrieve model
        model = self._get_model(model_name)
        dim = model.get_embedding_dimension()
        if dim is None:
            raise ProviderException(
                f"Failed to retrieve embedding dimension for model '{model_name}'"
            )

        # 3. Perform batch inference
        logger.info(f"Batch embedding started (size: {len(texts)})")
        start_time = time.perf_counter()
        try:
            # We enforce clean lists of floats by casting output from numpy
            embeddings_np = model.encode(texts)
            processing_time = time.perf_counter() - start_time
            logger.info("Embedding batch completed successfully")
        except Exception as e:
            logger.error(f"Batch embedding failed: {e!s}")
            raise ProviderException(f"Failed to generate batch embeddings: {e!s}") from e

        # 4. Convert numpy arrays to lists of float in DTOs
        vectors: list[EmbeddingVector] = []
        for emb in embeddings_np:
            # Convert single embedding vector to Python list of float
            vec_list = [float(x) for x in emb]
            vectors.append(
                EmbeddingVector(
                    vector=vec_list,
                    dimension=dim,
                    model_identifier=model_name,
                )
            )

        return EmbeddingBatch(
            vectors=vectors,
            processing_time=processing_time,
            model_identifier=model_name,
        )

    def generate_query_embedding(self, query_text: str, model_name: str) -> EmbeddingVector:
        """Generates an embedding DTO for a single query text."""
        logger.info(f"Single query embedding requested using model '{model_name}'")

        # 1. Validation checks
        if query_text is None or query_text.strip() == "":
            raise ValidationException("Query text must not be empty or blank.")

        # 2. Retrieve model
        model = self._get_model(model_name)
        dim = model.get_embedding_dimension()
        if dim is None:
            raise ProviderException(
                f"Failed to retrieve embedding dimension for model '{model_name}'"
            )

        # 3. Perform single inference
        logger.info("Embedding single query started")
        try:
            emb_np = model.encode(query_text)
            logger.info("Embedding single query completed successfully")
        except Exception as e:
            logger.error(f"Single embedding failed: {e!s}")
            raise ProviderException(f"Failed to generate query embedding: {e!s}") from e

        vec_list = [float(x) for x in emb_np]
        return EmbeddingVector(
            vector=vec_list,
            dimension=dim,
            model_identifier=model_name,
        )
