from datetime import datetime
from unittest.mock import MagicMock

import pytest

from src.domain.engines.default_retrieval_engine import DefaultRetrievalEngine
from src.domain.entities.context import RetrievalContext
from src.domain.entities.query import Query
from src.domain.providers.embedding import EmbeddingProvider, EmbeddingVector
from src.domain.providers.knowledge_index import KnowledgeIndexProvider, SearchBatch, SearchResult
from src.domain.value_objects.identifiers import BookId, QueryId
from src.shared.exceptions import ValidationException


@pytest.fixture
def mock_embedding_provider() -> MagicMock:
    """Fixture returning a mocked EmbeddingProvider."""
    provider = MagicMock(spec=EmbeddingProvider)
    provider.provider_name = "MockEmbeddingProvider"
    provider.provider_version = "1.0.0"

    # Mock query embedding DTO
    vector = [0.1, 0.2, 0.3, 0.4]
    provider.generate_query_embedding.return_value = EmbeddingVector(
        vector=vector,
        dimension=4,
        model_identifier="test-embedding-model",
    )
    return provider


@pytest.fixture
def mock_index_provider() -> MagicMock:
    """Fixture returning a mocked KnowledgeIndexProvider."""
    provider = MagicMock(spec=KnowledgeIndexProvider)
    provider.provider_name = "MockIndexProvider"
    provider.provider_version = "2.0.0"
    provider.has_collection.return_value = True
    return provider


@pytest.fixture
def engine(
    mock_embedding_provider: MagicMock, mock_index_provider: MagicMock
) -> DefaultRetrievalEngine:
    """Fixture returning a DefaultRetrievalEngine with mocked providers."""
    return DefaultRetrievalEngine(
        embedding_provider=mock_embedding_provider,
        index_provider=mock_index_provider,
        book_id=BookId("test-book"),
        model_name="test-embedding-model",
    )


def test_retrieval_success(
    mock_embedding_provider: MagicMock,
    mock_index_provider: MagicMock,
    engine: DefaultRetrievalEngine,
) -> None:
    """Verifies that retrieval successfully maps search results to RetrievalContext."""
    query = Query(
        id=QueryId("q-1"),
        original_question="What is RAG?",
        query_timestamp=datetime.now(),
    )

    # Mock index search results (sorted by distance ascending/similarity descending)
    search_results = [
        SearchResult(
            identifier="emb-1",
            similarity_score=0.9,
            metadata={
                "chunk_id": "chunk-1",
                "embedding_id": "emb-1",
                "chunk_text": "RAG stands for Retrieval-Augmented Generation.",
                "page_number": 5,
                "chapter_id": "chap-1",
                "section_id": "sec-1",
            },
        ),
        SearchResult(
            identifier="emb-2",
            similarity_score=0.7,
            metadata={
                "chunk_id": "chunk-2",
                "embedding_id": "emb-2",
                "chunk_text": "It improves LLM answers by querying external databases.",
                "page_number": 6,
                "chapter_id": "chap-1",
                "section_id": "sec-2",
            },
        ),
    ]
    mock_index_provider.query_similarity.return_value = SearchBatch(
        results=search_results,
        search_duration=0.05,
        total_candidates=10,
    )

    context = engine.retrieve_context(query)

    assert isinstance(context, RetrievalContext)
    assert context.book_id.value == "test-book"
    assert len(context.items) == 2

    # First chunk checks
    assert context.items[0].chunk_id.value == "chunk-1"
    assert context.items[0].embedding_id.value == "emb-1"
    assert context.items[0].chunk_text == "RAG stands for Retrieval-Augmented Generation."
    assert context.items[0].similarity_score == 0.9
    assert context.items[0].retrieval_rank == 1
    assert context.items[0].page_number == 5
    assert context.items[0].chapter_id.value == "chap-1" if context.items[0].chapter_id else False
    assert context.items[0].section_id.value == "sec-1" if context.items[0].section_id else False
    assert isinstance(context.items[0].retrieval_timestamp, datetime)

    # Second chunk checks
    assert context.items[1].chunk_id.value == "chunk-2"
    assert context.items[1].retrieval_rank == 2

    # Verification of Provider calls
    mock_embedding_provider.generate_query_embedding.assert_called_once_with(
        "What is RAG?", model_name="test-embedding-model"
    )
    mock_index_provider.query_similarity.assert_called_once_with(
        collection_name="test-book",
        vector=[0.1, 0.2, 0.3, 0.4],
        limit=5,
        filter_metadata=None,
    )

    # Statistics validation
    assert context.statistics["total_candidates"] == 10
    assert context.statistics["retrieved_chunks"] == 2
    assert context.statistics["average_similarity"] == 0.8
    assert context.statistics["retrieval_duration"] > 0

    # Metadata validation
    assert context.metadata["model_identifier"] == "test-embedding-model"
    assert context.metadata["collection_name"] == "test-book"
    assert context.metadata["provider_name"] == "MockIndexProvider"
    assert context.metadata["provider_version"] == "2.0.0"


def test_retrieval_empty_query(engine: DefaultRetrievalEngine) -> None:
    """Verifies that an empty or blank query text raises ValidationException."""
    # None Query
    with pytest.raises(ValidationException, match="Query cannot be None"):
        engine.retrieve_context(None)  # type: ignore

    # Empty Query Text
    query_empty = Query(id=QueryId("q-empty"), original_question="", query_timestamp=datetime.now())
    with pytest.raises(ValidationException, match="Query text cannot be empty or blank"):
        engine.retrieve_context(query_empty)

    # Blank Query Text
    query_blank = Query(
        id=QueryId("q-blank"),
        original_question="   ",
        query_timestamp=datetime.now(),
    )
    with pytest.raises(ValidationException, match="Query text cannot be empty or blank"):
        engine.retrieve_context(query_blank)


def test_retrieval_no_search_results(
    mock_index_provider: MagicMock, engine: DefaultRetrievalEngine
) -> None:
    """Verifies that empty results from the provider raise a ValidationException."""
    query = Query(id=QueryId("q-1"), original_question="Testing...", query_timestamp=datetime.now())
    mock_index_provider.query_similarity.return_value = SearchBatch(
        results=[],
        search_duration=0.01,
        total_candidates=0,
    )

    with pytest.raises(ValidationException, match="No search results found"):
        engine.retrieve_context(query)


def test_retrieval_duplicate_chunks(
    mock_index_provider: MagicMock, engine: DefaultRetrievalEngine
) -> None:
    """Verifies that duplicate chunk IDs in search results raise a ValidationException."""
    query = Query(id=QueryId("q-1"), original_question="Testing...", query_timestamp=datetime.now())

    # Results pointing to the same chunk ID
    search_results = [
        SearchResult(
            identifier="emb-1",
            similarity_score=0.9,
            metadata={"chunk_id": "chunk-dup", "chunk_text": "Sample"},
        ),
        SearchResult(
            identifier="emb-2",
            similarity_score=0.8,
            metadata={"chunk_id": "chunk-dup", "chunk_text": "Sample duplicate"},
        ),
    ]
    mock_index_provider.query_similarity.return_value = SearchBatch(
        results=search_results,
        search_duration=0.02,
        total_candidates=2,
    )

    with pytest.raises(ValidationException, match="Duplicate ChunkId found in search results"):
        engine.retrieve_context(query)


def test_retrieval_ranking_consistency(
    mock_index_provider: MagicMock, engine: DefaultRetrievalEngine
) -> None:
    """Verifies that unsorted/inconsistent scores from the provider raise a ValidationException."""
    query = Query(id=QueryId("q-1"), original_question="Testing...", query_timestamp=datetime.now())

    # Scores are neither ascending nor descending
    search_results = [
        SearchResult(identifier="e1", similarity_score=0.9, metadata={"chunk_id": "c1"}),
        SearchResult(identifier="e2", similarity_score=0.4, metadata={"chunk_id": "c2"}),
        SearchResult(identifier="e3", similarity_score=0.8, metadata={"chunk_id": "c3"}),
    ]
    mock_index_provider.query_similarity.return_value = SearchBatch(
        results=search_results,
        search_duration=0.02,
        total_candidates=3,
    )

    expected_msg = "Search results scores are not sorted consistently"
    with pytest.raises(ValidationException, match=expected_msg):
        engine.retrieve_context(query)


def test_retrieval_similarity_threshold(
    mock_index_provider: MagicMock, engine: DefaultRetrievalEngine
) -> None:
    """Verifies that results below the similarity threshold are filtered out."""
    query = Query(id=QueryId("q-1"), original_question="Testing...", query_timestamp=datetime.now())
    search_results = [
        SearchResult(identifier="e1", similarity_score=0.9, metadata={"chunk_id": "c1"}),
        SearchResult(identifier="e2", similarity_score=0.8, metadata={"chunk_id": "c2"}),
        SearchResult(identifier="e3", similarity_score=0.5, metadata={"chunk_id": "c3"}),
    ]
    mock_index_provider.query_similarity.return_value = SearchBatch(
        results=search_results,
        search_duration=0.03,
        total_candidates=3,
    )

    # Use similarity threshold of 0.75 (should exclude c3)
    context = engine.retrieve_context(query, similarity_threshold=0.75)

    assert len(context.items) == 2
    assert context.items[0].chunk_id.value == "c1"
    assert context.items[0].retrieval_rank == 1
    assert context.items[1].chunk_id.value == "c2"
    assert context.items[1].retrieval_rank == 2

    # Verify that statistics correctly show 2 retrieved chunks
    assert context.statistics["retrieved_chunks"] == 2
    assert context.statistics["average_similarity"] == pytest.approx(0.85)


def test_retrieval_top_k_limit(
    mock_index_provider: MagicMock, engine: DefaultRetrievalEngine
) -> None:
    """Verifies that the limit is correctly propagated to the vector store query."""
    query = Query(id=QueryId("q-1"), original_question="Testing...", query_timestamp=datetime.now())
    mock_index_provider.query_similarity.return_value = SearchBatch(
        results=[SearchResult(identifier="e1", similarity_score=0.9, metadata={"chunk_id": "c1"})],
        search_duration=0.01,
        total_candidates=1,
    )

    engine.retrieve_context(query, limit=10)

    mock_index_provider.query_similarity.assert_called_once_with(
        collection_name="test-book",
        vector=[0.1, 0.2, 0.3, 0.4],
        limit=10,
        filter_metadata=None,
    )


def test_retrieval_provider_failure(
    mock_index_provider: MagicMock, engine: DefaultRetrievalEngine
) -> None:
    """Verifies that provider exceptions are propagated correctly."""
    query = Query(id=QueryId("q-1"), original_question="Testing...", query_timestamp=datetime.now())
    mock_index_provider.query_similarity.side_effect = RuntimeError("DB connection lost")

    with pytest.raises(RuntimeError, match="DB connection lost"):
        engine.retrieve_context(query)


def test_retrieval_missing_collection(
    mock_index_provider: MagicMock, engine: DefaultRetrievalEngine
) -> None:
    """Verifies that searching a non-existent collection raises ValidationException."""
    query = Query(id=QueryId("q-1"), original_question="Testing...", query_timestamp=datetime.now())
    mock_index_provider.has_collection.return_value = False

    with pytest.raises(ValidationException, match="Collection 'test-book' does not exist"):
        engine.retrieve_context(query)
