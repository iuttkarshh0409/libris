from datetime import datetime
from unittest.mock import MagicMock

import pytest

from src.domain.engines.default_indexing_engine import DefaultIndexingEngine
from src.domain.entities.chunk import Chunk
from src.domain.entities.chunk_collection import ChunkCollection
from src.domain.entities.embedding import Embedding
from src.domain.entities.embedding_collection import EmbeddingCollection
from src.domain.entities.knowledge_index import KnowledgeIndex
from src.domain.providers.knowledge_index import KnowledgeIndexProvider
from src.domain.value_objects.identifiers import (
    BookId,
    ChapterId,
    ChunkId,
    EmbeddingId,
    SectionId,
)
from src.shared.exceptions import ValidationException


@pytest.fixture
def mock_provider() -> MagicMock:
    """Fixture returning a mocked KnowledgeIndexProvider."""
    provider = MagicMock(spec=KnowledgeIndexProvider)
    provider.provider_name = "MockProvider"
    provider.provider_version = "1.0.0"
    provider.has_collection.return_value = False
    return provider


@pytest.fixture
def engine(mock_provider: MagicMock) -> DefaultIndexingEngine:
    """Fixture returning a DefaultIndexingEngine with the mocked provider."""
    return DefaultIndexingEngine(provider=mock_provider)


def create_mock_chunk(chunk_id_str: str, book_id_str: str = "book-123", page: int = 1) -> Chunk:
    return Chunk(
        id=ChunkId(chunk_id_str),
        book_id=BookId(book_id_str),
        page_number=page,
        chunk_index=0,
        chunk_text="Some text",
        character_count=9,
        token_count=2,
    )


def create_mock_embedding(
    emb_id_str: str,
    chunk_id_str: str,
    vector: list[float] | None = None,
    dim: int = 4,
) -> Embedding:
    if vector is None:
        vector = [0.1] * dim
    return Embedding(
        id=EmbeddingId(emb_id_str),
        chunk_id=ChunkId(chunk_id_str),
        model_identifier="test-model",
        vector_dimension=dim,
        embedding_vector=vector,
        generated_timestamp=datetime.now(),
    )


def test_indexing_single_embedding(mock_provider: MagicMock, engine: DefaultIndexingEngine) -> None:
    """Verifies that indexing a single embedding is successfully propagated to the provider."""
    book_id = BookId("book-123")
    chunk = create_mock_chunk("chunk-1")
    embedding = create_mock_embedding("emb-1", "chunk-1")

    chunk_coll = ChunkCollection(book_id=book_id, chunks=[chunk], statistics={}, metadata={})
    emb_coll = EmbeddingCollection(
        book_id=book_id, embeddings=[embedding], statistics={}, metadata={}
    )

    result = engine.add_to_index(chunk_coll, emb_coll)

    assert isinstance(result, KnowledgeIndex)
    assert result.book_id == book_id
    assert len(result.items) == 1
    assert result.items[0].embedding_id == embedding.id
    assert result.items[0].persistence_status == "success"

    # Verify provider calls
    mock_provider.has_collection.assert_called_once()
    mock_provider.create_collection.assert_called_once()
    mock_provider.add_vectors.assert_called_once()

    # Check statistics
    assert result.statistics["total_records"] == 1
    assert result.statistics["indexed_records"] == 1
    assert result.statistics["failed_records"] == 0
    assert result.statistics["average_dimension"] == 4.0

    # Check metadata
    assert result.metadata["provider_name"] == "MockProvider"
    assert result.metadata["provider_version"] == "1.0.0"
    assert result.metadata["model_identifier"] == "test-model"


def test_indexing_multiple_embeddings_batch(
    mock_provider: MagicMock, engine: DefaultIndexingEngine
) -> None:
    """Verifies that indexing multiple embeddings is executed in a single provider batch call."""
    book_id = BookId("book-123")
    chunks = [create_mock_chunk(f"chunk-{i}") for i in range(5)]
    embeddings = [create_mock_embedding(f"emb-{i}", f"chunk-{i}") for i in range(5)]

    chunk_coll = ChunkCollection(book_id=book_id, chunks=chunks, statistics={}, metadata={})
    emb_coll = EmbeddingCollection(
        book_id=book_id, embeddings=embeddings, statistics={}, metadata={}
    )

    result = engine.add_to_index(chunk_coll, emb_coll)

    assert len(result.items) == 5
    # Verify deterministic ordering: IndexRecord N corresponds to Embedding N
    for i in range(5):
        assert result.items[i].embedding_id.value == f"emb-{i}"
        assert result.items[i].chunk_id.value == f"chunk-{i}"

    # Provider add_vectors should be called exactly once (batch)
    mock_provider.add_vectors.assert_called_once()
    called_vectors = mock_provider.add_vectors.call_args[0][1]
    assert len(called_vectors) == 5
    for i in range(5):
        assert called_vectors[i].identifier == f"emb-{i}"


def test_indexing_empty_collection(engine: DefaultIndexingEngine) -> None:
    """Verifies that empty embedding or chunk collection raises ValidationException."""
    book_id = BookId("book-123")
    chunk = create_mock_chunk("chunk-1")
    embedding = create_mock_embedding("emb-1", "chunk-1")

    # Empty embeddings
    chunk_coll_1 = ChunkCollection(book_id=book_id, chunks=[chunk], statistics={}, metadata={})
    emb_coll_empty = EmbeddingCollection(book_id=book_id, embeddings=[], statistics={}, metadata={})
    with pytest.raises(ValidationException, match="Embedding collection is empty"):
        engine.add_to_index(chunk_coll_1, emb_coll_empty)

    # Empty chunks
    chunk_coll_empty = ChunkCollection(book_id=book_id, chunks=[], statistics={}, metadata={})
    emb_coll_1 = EmbeddingCollection(
        book_id=book_id, embeddings=[embedding], statistics={}, metadata={}
    )
    with pytest.raises(ValidationException, match="Chunk collection is empty"):
        engine.add_to_index(chunk_coll_empty, emb_coll_1)


def test_duplicate_embeddings_rejection(engine: DefaultIndexingEngine) -> None:
    """Verifies that duplicate embedding IDs raise ValidationException."""
    book_id = BookId("book-123")
    chunks = [create_mock_chunk("chunk-1"), create_mock_chunk("chunk-2")]
    embeddings = [
        create_mock_embedding("emb-dup", "chunk-1"),
        create_mock_embedding("emb-dup", "chunk-2"),  # Duplicate EmbeddingId
    ]

    chunk_coll = ChunkCollection(book_id=book_id, chunks=chunks, statistics={}, metadata={})
    emb_coll = EmbeddingCollection(
        book_id=book_id, embeddings=embeddings, statistics={}, metadata={}
    )

    with pytest.raises(ValidationException, match="Duplicate EmbeddingId found"):
        engine.add_to_index(chunk_coll, emb_coll)


def test_duplicate_chunks_rejection(engine: DefaultIndexingEngine) -> None:
    """Verifies that duplicate chunk IDs raise ValidationException."""
    book_id = BookId("book-123")
    chunks = [
        create_mock_chunk("chunk-dup"),
        create_mock_chunk("chunk-dup"),  # Duplicate ChunkId
    ]
    embeddings = [
        create_mock_embedding("emb-1", "chunk-dup"),
        create_mock_embedding("emb-2", "chunk-dup"),
    ]

    chunk_coll = ChunkCollection(book_id=book_id, chunks=chunks, statistics={}, metadata={})
    emb_coll = EmbeddingCollection(
        book_id=book_id, embeddings=embeddings, statistics={}, metadata={}
    )

    with pytest.raises(ValidationException, match="Duplicate ChunkId found"):
        engine.add_to_index(chunk_coll, emb_coll)


def test_inconsistent_dimensions_rejection(engine: DefaultIndexingEngine) -> None:
    """Verifies that inconsistent vector dimensions raise ValidationException."""
    book_id = BookId("book-123")
    chunks = [create_mock_chunk("chunk-1"), create_mock_chunk("chunk-2")]
    embeddings = [
        create_mock_embedding("emb-1", "chunk-1", dim=4),
        create_mock_embedding("emb-2", "chunk-2", dim=5),  # Mismatching dimension
    ]

    chunk_coll = ChunkCollection(book_id=book_id, chunks=chunks, statistics={}, metadata={})
    emb_coll = EmbeddingCollection(
        book_id=book_id, embeddings=embeddings, statistics={}, metadata={}
    )

    with pytest.raises(ValidationException, match="Inconsistent dimension"):
        engine.add_to_index(chunk_coll, emb_coll)


def test_relationship_integrity_mismatch(engine: DefaultIndexingEngine) -> None:
    """Verifies that positional alignment mismatch of chunk_id raises ValidationException."""
    book_id = BookId("book-123")
    chunks = [create_mock_chunk("chunk-1"), create_mock_chunk("chunk-2")]
    # Embedding 0 points to chunk-2, but Chunk 0 is chunk-1 -> Mismatch
    embeddings = [
        create_mock_embedding("emb-1", "chunk-2"),
        create_mock_embedding("emb-2", "chunk-1"),
    ]

    chunk_coll = ChunkCollection(book_id=book_id, chunks=chunks, statistics={}, metadata={})
    emb_coll = EmbeddingCollection(
        book_id=book_id, embeddings=embeddings, statistics={}, metadata={}
    )

    with pytest.raises(ValidationException, match="Relationship mismatch at index 0"):
        engine.add_to_index(chunk_coll, emb_coll)


def test_provider_persistence_failure(
    mock_provider: MagicMock, engine: DefaultIndexingEngine
) -> None:
    """Verifies that provider errors are propagated and not silently swallowed."""
    book_id = BookId("book-123")
    chunk = create_mock_chunk("chunk-1")
    embedding = create_mock_embedding("emb-1", "chunk-1")

    chunk_coll = ChunkCollection(book_id=book_id, chunks=[chunk], statistics={}, metadata={})
    emb_coll = EmbeddingCollection(
        book_id=book_id, embeddings=[embedding], statistics={}, metadata={}
    )

    mock_provider.add_vectors.side_effect = RuntimeError("DB connection lost")

    with pytest.raises(RuntimeError, match="DB connection lost"):
        engine.add_to_index(chunk_coll, emb_coll)


def test_metadata_propagation(mock_provider: MagicMock, engine: DefaultIndexingEngine) -> None:
    """Verifies that metadata fields are accurately mapped and passed to the provider."""
    book_id = BookId("book-123")
    chunk = Chunk(
        id=ChunkId("chunk-1"),
        book_id=book_id,
        page_number=42,
        chunk_index=0,
        chunk_text="Sample",
        character_count=6,
        token_count=1,
        chapter_id=ChapterId("chap-1"),
        section_id=SectionId("sec-1"),
    )
    embedding = create_mock_embedding("emb-1", "chunk-1")

    chunk_coll = ChunkCollection(book_id=book_id, chunks=[chunk], statistics={}, metadata={})
    emb_coll = EmbeddingCollection(
        book_id=book_id, embeddings=[embedding], statistics={}, metadata={}
    )

    engine.add_to_index(chunk_coll, emb_coll)

    mock_provider.add_vectors.assert_called_once()
    called_vectors = mock_provider.add_vectors.call_args[0][1]
    assert len(called_vectors) == 1
    metadata = called_vectors[0].metadata

    assert metadata["embedding_id"] == "emb-1"
    assert metadata["chunk_id"] == "chunk-1"
    assert metadata["book_id"] == "book-123"
    assert metadata["page_number"] == 42
    assert metadata["chapter_id"] == "chap-1"
    assert metadata["section_id"] == "sec-1"
    assert metadata["model_identifier"] == "test-model"


def test_delete_book_from_index(mock_provider: MagicMock, engine: DefaultIndexingEngine) -> None:
    """Verifies delete_book_from_index is dispatched to the provider with correct filters."""
    book_id = BookId("book-123")
    mock_provider.has_collection.return_value = True

    engine.delete_book_from_index(book_id)

    mock_provider.delete_vectors.assert_called_once_with(
        "book-123", filter_metadata={"book_id": "book-123"}
    )
