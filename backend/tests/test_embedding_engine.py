from datetime import datetime
from unittest.mock import Mock

import pytest

from src.domain.engines.default_embedding_engine import DefaultEmbeddingEngine
from src.domain.entities.chunk import Chunk
from src.domain.entities.chunk_collection import ChunkCollection
from src.domain.entities.embedding import Embedding
from src.domain.entities.embedding_collection import EmbeddingCollection
from src.domain.entities.query import Query
from src.domain.providers.embedding import EmbeddingBatch, EmbeddingProvider, EmbeddingVector
from src.domain.value_objects.embedding import QueryEmbedding
from src.domain.value_objects.identifiers import BookId, ChunkId, EmbeddingId, QueryId
from src.shared.exceptions import ProviderException, ValidationException


class FakeEmbeddingProvider(EmbeddingProvider):
    """A fake implementation of EmbeddingProvider for isolated engine tests."""

    def __init__(self, vector_dim: int = 384, fail_on_generate: bool = False) -> None:
        self.vector_dim = vector_dim
        self.fail_on_generate = fail_on_generate
        self.last_model_used: str | None = None

    @property
    def provider_name(self) -> str:
        return "FakeEmbeddingProvider"

    @property
    def provider_version(self) -> str:
        return "1.0.0"

    def generate_embeddings(self, texts: list[str], model_name: str) -> EmbeddingBatch:
        self.last_model_used = model_name
        if self.fail_on_generate:
            raise ProviderException("Mock provider error during batch generation")

        vectors = [
            EmbeddingVector(
                vector=[0.1] * self.vector_dim,
                dimension=self.vector_dim,
                model_identifier=model_name,
            )
            for _ in texts
        ]
        return EmbeddingBatch(
            vectors=vectors,
            processing_time=0.042,
            model_identifier=model_name,
        )

    def generate_query_embedding(self, query_text: str, model_name: str) -> EmbeddingVector:
        self.last_model_used = model_name
        if self.fail_on_generate:
            raise ProviderException("Mock provider error during query generation")

        return EmbeddingVector(
            vector=[0.2] * self.vector_dim,
            dimension=self.vector_dim,
            model_identifier=model_name,
        )


def test_embed_chunks_success() -> None:
    """Verifies that the embedding engine processes a ChunkCollection successfully."""
    provider = FakeEmbeddingProvider(vector_dim=384)
    engine = DefaultEmbeddingEngine(provider=provider, model_name="test-model")

    book_id = BookId("book-123")
    chunks = [
        Chunk(
            id=ChunkId("chunk-1"),
            book_id=book_id,
            page_number=1,
            chunk_index=0,
            chunk_text="First chunk text.",
            character_count=len("First chunk text."),
            token_count=5,
            source_page_start=1,
            source_page_end=1,
        ),
        Chunk(
            id=ChunkId("chunk-2"),
            book_id=book_id,
            page_number=2,
            chunk_index=1,
            chunk_text="Second chunk text.",
            character_count=len("Second chunk text."),
            token_count=5,
            source_page_start=2,
            source_page_end=2,
        ),
    ]
    chunk_collection = ChunkCollection(book_id=book_id, chunks=chunks, statistics={}, metadata={})

    result = engine.embed_chunks(chunk_collection)

    assert isinstance(result, EmbeddingCollection)
    assert result.book_id == book_id
    assert result.total_embeddings == 2
    assert provider.last_model_used == "test-model"

    # Verify embeddings list mapping
    for i, emb in enumerate(result.embeddings):
        assert isinstance(emb, Embedding)
        assert isinstance(emb.id, EmbeddingId)
        assert emb.chunk_id == chunks[i].id
        assert emb.model_identifier == "test-model"
        assert emb.vector_dimension == 384
        assert emb.embedding_vector == [0.1] * 384
        assert emb.generated_timestamp is not None

    # Verify stats
    assert result.statistics["total_embeddings"] == 2
    assert result.statistics["embedding_dimension"] == 384
    assert result.statistics["processing_time"] == 0.042
    # Norm check: L2 norm of [0.1]*384 is sqrt(384 * 0.01) = sqrt(3.84)
    expected_norm = pytest.approx((384 * 0.01) ** 0.5)
    assert result.statistics["average_vector_norm"] == expected_norm

    # Verify metadata
    assert result.metadata["model_identifier"] == "test-model"
    expected_avg_len = (len(chunks[0].chunk_text) + len(chunks[1].chunk_text)) / 2.0
    assert result.metadata["average_chunk_char_length"] == expected_avg_len


def test_embed_chunks_validation_empty() -> None:
    """Verifies that an empty chunk list raises a ValidationException."""
    provider = FakeEmbeddingProvider()
    engine = DefaultEmbeddingEngine(provider=provider)

    chunk_collection = ChunkCollection(
        book_id=BookId("book-123"), chunks=[], statistics={}, metadata={}
    )

    with pytest.raises(ValidationException, match="Chunk collection is empty"):
        engine.embed_chunks(chunk_collection)


def test_embed_query_success() -> None:
    """Verifies that the embedding engine processes a Query successfully."""
    provider = FakeEmbeddingProvider(vector_dim=384)
    engine = DefaultEmbeddingEngine(provider=provider, model_name="test-model")

    query = Query(
        id=QueryId("query-1"),
        original_question="What is clean architecture?",
        query_timestamp=datetime.now(),
    )
    result = engine.embed_query(query)

    assert isinstance(result, QueryEmbedding)
    assert result.query_id == query.id
    assert result.model_identifier == "test-model"
    assert result.vector == [0.2] * 384
    assert provider.last_model_used == "test-model"


def test_embed_query_validation_empty() -> None:
    """Verifies that empty/blank query text raises a ValidationException."""
    provider = FakeEmbeddingProvider()
    engine = DefaultEmbeddingEngine(provider=provider)

    q_empty = Query(id=QueryId("q1"), original_question="", query_timestamp=datetime.now())
    with pytest.raises(ValidationException, match="Query text must not be empty or blank"):
        engine.embed_query(q_empty)

    q_blank = Query(id=QueryId("q2"), original_question="    ", query_timestamp=datetime.now())
    with pytest.raises(ValidationException, match="Query text must not be empty or blank"):
        engine.embed_query(q_blank)

    q_none = Query(id=QueryId("q3"), original_question=None, query_timestamp=datetime.now())  # type: ignore[arg-type]
    with pytest.raises(ValidationException, match="Query text must not be empty or blank"):
        engine.embed_query(q_none)


def test_provider_errors_propagate() -> None:
    """Verifies that any provider-level exceptions are propagated transparently."""
    provider = FakeEmbeddingProvider(fail_on_generate=True)
    engine = DefaultEmbeddingEngine(provider=provider)

    # Chunks error propagation
    chunk_collection = ChunkCollection(
        book_id=BookId("b1"),
        chunks=[
            Chunk(
                id=ChunkId("c1"),
                book_id=BookId("b1"),
                page_number=1,
                chunk_index=0,
                chunk_text="text",
                character_count=4,
                token_count=1,
            )
        ],
        statistics={},
        metadata={},
    )
    with pytest.raises(ProviderException, match="Mock provider error during batch generation"):
        engine.embed_chunks(chunk_collection)

    # Query error propagation
    query = Query(id=QueryId("q1"), original_question="query", query_timestamp=datetime.now())
    with pytest.raises(ProviderException, match="Mock provider error during query generation"):
        engine.embed_query(query)


def test_embed_chunks_duplicate_chunk_ids() -> None:
    """Verifies duplicate ChunkIds throw a ValidationException."""
    provider = FakeEmbeddingProvider()
    engine = DefaultEmbeddingEngine(provider=provider)

    book_id = BookId("book-123")
    chunks = [
        Chunk(
            id=ChunkId("chunk-1"),
            book_id=book_id,
            page_number=1,
            chunk_index=0,
            chunk_text="First",
            character_count=5,
            token_count=1,
        ),
        Chunk(
            id=ChunkId("chunk-1"),  # Duplicate
            book_id=book_id,
            page_number=2,
            chunk_index=1,
            chunk_text="Second",
            character_count=6,
            token_count=1,
        ),
    ]
    chunk_collection = ChunkCollection(book_id=book_id, chunks=chunks, statistics={}, metadata={})

    with pytest.raises(ValidationException, match="Duplicate ChunkId found"):
        engine.embed_chunks(chunk_collection)


def test_embed_chunks_duplicate_embedding_ids(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verifies duplicate EmbeddingIds throw a ValidationException."""
    provider = FakeEmbeddingProvider()
    engine = DefaultEmbeddingEngine(provider=provider)

    book_id = BookId("book-123")
    chunks = [
        Chunk(
            id=ChunkId("chunk-1"),
            book_id=book_id,
            page_number=1,
            chunk_index=0,
            chunk_text="First",
            character_count=5,
            token_count=1,
        ),
        Chunk(
            id=ChunkId("chunk-2"),
            book_id=book_id,
            page_number=2,
            chunk_index=1,
            chunk_text="Second",
            character_count=6,
            token_count=1,
        ),
    ]
    chunk_collection = ChunkCollection(book_id=book_id, chunks=chunks, statistics={}, metadata={})

    # Force uuid4 to return duplicate string values
    monkeypatch.setattr("uuid.uuid4", lambda: "static-uuid-value")

    with pytest.raises(ValidationException, match="Duplicate EmbeddingId"):
        engine.embed_chunks(chunk_collection)


def test_embed_chunks_inconsistent_dimensions() -> None:
    """Verifies inconsistent dimensions returned by the provider raise a ValidationException."""

    class InconsistentDimensionProvider(FakeEmbeddingProvider):
        def generate_embeddings(self, texts: list[str], model_name: str) -> EmbeddingBatch:
            return EmbeddingBatch(
                vectors=[
                    EmbeddingVector(vector=[0.1] * 384, dimension=384, model_identifier=model_name),
                    EmbeddingVector(vector=[0.2] * 512, dimension=512, model_identifier=model_name),
                ],
                processing_time=0.01,
                model_identifier=model_name,
            )

    provider = InconsistentDimensionProvider()
    engine = DefaultEmbeddingEngine(provider=provider)

    book_id = BookId("book-123")
    chunks = [
        Chunk(
            id=ChunkId("c1"),
            book_id=book_id,
            page_number=1,
            chunk_index=0,
            chunk_text="First",
            character_count=5,
            token_count=1,
        ),
        Chunk(
            id=ChunkId("c2"),
            book_id=book_id,
            page_number=2,
            chunk_index=1,
            chunk_text="Second",
            character_count=6,
            token_count=1,
        ),
    ]
    chunk_collection = ChunkCollection(book_id=book_id, chunks=chunks, statistics={}, metadata={})

    with pytest.raises(ValidationException, match="Inconsistent vector dimension"):
        engine.embed_chunks(chunk_collection)


def test_embed_chunks_missing_vectors() -> None:
    """Verifies missing vectors from the provider throw a ValidationException."""

    class MissingVectorsProvider(FakeEmbeddingProvider):
        def generate_embeddings(self, texts: list[str], model_name: str) -> EmbeddingBatch:
            return EmbeddingBatch(
                vectors=[],
                processing_time=0.01,
                model_identifier=model_name,
            )

    provider = MissingVectorsProvider()
    engine = DefaultEmbeddingEngine(provider=provider)

    book_id = BookId("book-123")
    chunks = [
        Chunk(
            id=ChunkId("c1"),
            book_id=book_id,
            page_number=1,
            chunk_index=0,
            chunk_text="First",
            character_count=5,
            token_count=1,
        )
    ]
    chunk_collection = ChunkCollection(book_id=book_id, chunks=chunks, statistics={}, metadata={})

    with pytest.raises(ValidationException, match="Provider returned empty or missing vectors"):
        engine.embed_chunks(chunk_collection)


def test_aggregate_standardized_properties() -> None:
    """Verifies aggregate standardized properties (book_id, items, statistics, metadata)."""
    provider = FakeEmbeddingProvider(vector_dim=384)
    engine = DefaultEmbeddingEngine(provider=provider, model_name="test-model")

    book_id = BookId("book-123")
    chunks = [
        Chunk(
            id=ChunkId("chunk-1"),
            book_id=book_id,
            page_number=1,
            chunk_index=0,
            chunk_text="First",
            character_count=5,
            token_count=1,
        )
    ]
    chunk_collection = ChunkCollection(
        book_id=book_id,
        chunks=chunks,
        statistics={"test": 1},
        metadata={"source": "test"},
    )

    # Check ChunkCollection properties
    assert chunk_collection.book_id == book_id
    assert chunk_collection.items == chunks
    assert chunk_collection.statistics == {"test": 1}
    assert chunk_collection.metadata == {"source": "test"}

    result = engine.embed_chunks(chunk_collection)

    # Check EmbeddingCollection properties
    assert result.book_id == book_id
    assert result.items == result.embeddings
    assert result.statistics["total_embeddings"] == 1
    assert result.metadata["model_identifier"] == "test-model"

    # Check ParsedDocument properties
    from src.domain.entities.book import Book
    from src.domain.entities.page import Page
    from src.domain.entities.parsed_document import ParsedDocument

    book = Book(
        id=book_id,
        title="Title",
        author="Author",
        edition="1st",
        subject="Subject",
        file_name="file.pdf",
        file_path="file.pdf",
        upload_timestamp=datetime.now(),
        total_pages=1,
        index_status="queued",
    )
    pages = [
        Page(
            id=Mock(),
            book_id=book_id,
            page_number=1,
            extracted_text="test",
            character_count=4,
        )
    ]
    parsed_doc = ParsedDocument(book=book, pages=pages, chapters=[], sections=[])

    assert parsed_doc.book_id == book_id
    assert parsed_doc.items == pages
    assert parsed_doc.statistics["total_pages"] == 1
    assert parsed_doc.metadata["title"] == "Title"
