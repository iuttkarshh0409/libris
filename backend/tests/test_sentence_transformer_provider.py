import pytest

from src.infrastructure.providers.embedding.models import EmbeddingBatch, EmbeddingVector
from src.infrastructure.providers.embedding.sentence_transformers import SentenceTransformerProvider
from src.shared.exceptions import ProviderException, ValidationException

MODEL_NAME = "all-MiniLM-L6-v2"


def test_provider_initialization() -> None:
    """Verifies that the provider initializes with custom config."""
    provider = SentenceTransformerProvider(max_batch_size=10)
    assert provider.max_batch_size == 10


def test_model_loading_and_singleton() -> None:
    """Verifies model lazy loading and singleton caching behavior."""
    provider = SentenceTransformerProvider()
    model1 = provider._get_model(MODEL_NAME)
    model2 = provider._get_model(MODEL_NAME)

    # Verify they point to the exact same instance in memory
    assert model1 is model2
    assert model1.get_embedding_dimension() == 384


def test_single_embedding_success() -> None:
    """Verifies single text embedding behaves correctly and returns EmbeddingVector."""
    provider = SentenceTransformerProvider()
    text = "Clean architecture is modular."
    result = provider.generate_query_embedding(text, MODEL_NAME)

    assert isinstance(result, EmbeddingVector)
    assert result.model_identifier == MODEL_NAME
    assert result.dimension == 384
    assert len(result.vector) == 384
    assert all(isinstance(x, float) for x in result.vector)


def test_batch_embedding_success() -> None:
    """Verifies batch text embedding behaves correctly and returns EmbeddingBatch."""
    provider = SentenceTransformerProvider()
    texts = [
        "First sentence to embed.",
        "Second sentence is slightly longer.",
        "Third short sentence.",
    ]
    result = provider.generate_embeddings(texts, MODEL_NAME)

    assert isinstance(result, EmbeddingBatch)
    assert result.model_identifier == MODEL_NAME
    assert result.processing_time > 0.0
    assert len(result.vectors) == 3

    for vector_dto in result.vectors:
        assert isinstance(vector_dto, EmbeddingVector)
        assert vector_dto.dimension == 384
        assert len(vector_dto.vector) == 384
        assert vector_dto.model_identifier == MODEL_NAME


def test_deterministic_output() -> None:
    """Verifies that vector generation is completely deterministic."""
    provider = SentenceTransformerProvider()
    text = "Deterministic vector check."

    v1 = provider.generate_query_embedding(text, MODEL_NAME).vector
    v2 = provider.generate_query_embedding(text, MODEL_NAME).vector
    assert v1 == v2

    batch_v1 = provider.generate_embeddings([text], MODEL_NAME).vectors[0].vector
    assert v1 == batch_v1


def test_unicode_and_emojis() -> None:
    """Verifies that special characters, unicode, and emojis embed correctly."""
    provider = SentenceTransformerProvider()
    text = "こんにちは世界 🌍 RAG pipelines are ✨ awesome ✨."
    result = provider.generate_query_embedding(text, MODEL_NAME)

    assert result.dimension == 384
    assert len(result.vector) == 384


def test_ordering_preserved() -> None:
    """Verifies that input order perfectly maps to output vector order."""
    provider = SentenceTransformerProvider()
    texts = ["Apple", "Banana", "Cherry"]
    result = provider.generate_embeddings(texts, MODEL_NAME)

    # Let's get separate embeddings of individual words
    v_apple = provider.generate_query_embedding("Apple", MODEL_NAME).vector
    v_banana = provider.generate_query_embedding("Banana", MODEL_NAME).vector
    v_cherry = provider.generate_query_embedding("Cherry", MODEL_NAME).vector

    # Check batch output matches individual output order (using float approx)
    assert result.vectors[0].vector == pytest.approx(v_apple, abs=1e-5)
    assert result.vectors[1].vector == pytest.approx(v_banana, abs=1e-5)
    assert result.vectors[2].vector == pytest.approx(v_cherry, abs=1e-5)


def test_validation_empty_query() -> None:
    """Verifies validation of empty or blank query text inputs."""
    provider = SentenceTransformerProvider()

    with pytest.raises(ValidationException, match="Query text must not be empty or blank"):
        provider.generate_query_embedding("", MODEL_NAME)

    with pytest.raises(ValidationException, match="Query text must not be empty or blank"):
        provider.generate_query_embedding("   ", MODEL_NAME)

    with pytest.raises(ValidationException, match="Query text must not be empty or blank"):
        provider.generate_query_embedding(None, MODEL_NAME)  # type: ignore[arg-type]


def test_validation_batch_inputs() -> None:
    """Verifies validation of invalid batch list inputs."""
    provider = SentenceTransformerProvider()

    # Empty list
    with pytest.raises(ValidationException, match="Input texts list must not be empty"):
        provider.generate_embeddings([], MODEL_NAME)

    # Empty/blank strings inside batch
    with pytest.raises(ValidationException, match="Text at index 1 is empty or blank"):
        provider.generate_embeddings(["Valid text", "", "Another valid"], MODEL_NAME)

    with pytest.raises(ValidationException, match="Text at index 0 is empty or blank"):
        provider.generate_embeddings([None], MODEL_NAME)  # type: ignore[list-item]


def test_validation_oversized_batch() -> None:
    """Verifies that exceeding max batch size throws a ValidationException."""
    provider = SentenceTransformerProvider(max_batch_size=2)
    texts = ["one", "two", "three"]

    with pytest.raises(ValidationException, match="Batch size 3 exceeds maximum allowed 2"):
        provider.generate_embeddings(texts, MODEL_NAME)


def test_invalid_model_loading_failure() -> None:
    """Verifies that an invalid model name raises a ProviderException."""
    provider = SentenceTransformerProvider()

    with pytest.raises(ProviderException, match="Failed to initialize model"):
        provider.generate_query_embedding("text", "non-existent-model-name-12345")
