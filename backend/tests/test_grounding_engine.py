from datetime import datetime

import pytest

from src.domain.engines.default_grounding_engine import DefaultGroundingEngine
from src.domain.entities.context import RetrievalContext, RetrievedChunk
from src.domain.entities.query import Query
from src.domain.value_objects.identifiers import (
    BookId,
    ChapterId,
    ChunkId,
    EmbeddingId,
    QueryId,
    SectionId,
)
from src.shared.exceptions import ValidationException


@pytest.fixture
def sample_query() -> Query:
    """Fixture returning a standard user query."""
    return Query(
        id=QueryId("q-1"),
        original_question="How does retrieval-augmented generation work?",
        query_timestamp=datetime.now(),
    )


@pytest.fixture
def sample_context() -> RetrievalContext:
    """Fixture returning a standard RetrievalContext with sorted evidence chunks."""
    chunks = [
        RetrievedChunk(
            chunk_id=ChunkId("chunk-1"),
            embedding_id=EmbeddingId("emb-1"),
            chunk_text="RAG combines search models with generative generators.",
            similarity_score=0.9,
            retrieval_rank=1,
            page_number=10,
            chapter_id=ChapterId("chap-1"),
            section_id=SectionId("sec-1"),
            retrieval_timestamp=datetime.now(),
        ),
        RetrievedChunk(
            chunk_id=ChunkId("chunk-2"),
            embedding_id=EmbeddingId("emb-2"),
            chunk_text="It uses external sources to ground generated output.",
            similarity_score=0.8,
            retrieval_rank=2,
            page_number=11,
            chapter_id=ChapterId("chap-1"),
            section_id=None,
            retrieval_timestamp=datetime.now(),
        ),
    ]
    return RetrievalContext(
        book_id=BookId("textbook-rag"),
        items=chunks,
        statistics={"total_candidates": 10, "retrieved_chunks": 2},
        metadata={"retrieval_strategy": "semantic_similarity"},
    )


def test_grounding_success(sample_query: Query, sample_context: RetrievalContext) -> None:
    """Verifies successful compilation of query and context into a Prompt aggregate."""
    engine = DefaultGroundingEngine()
    prompt = engine.compile_prompt(sample_query, sample_context)

    # 1. Structured aggregate assertions
    assert prompt.book_id.value == "textbook-rag"
    assert len(prompt.items) == 5

    # Check sections types and ordering
    assert prompt.items[0].section_type == "system_instructions"
    assert prompt.items[1].section_type == "task_definition"
    assert prompt.items[2].section_type == "retrieved_evidence"
    assert prompt.items[3].section_type == "user_question"
    assert prompt.items[4].section_type == "constraints"

    # 2. Text formatting checks
    evidence_content = prompt.items[2].content
    assert "[Rank: 1]" in evidence_content
    assert "Book: textbook-rag, Page: 10, Chapter: chap-1, Section: sec-1" in evidence_content
    assert "RAG combines search" in evidence_content
    assert "[Rank: 2]" in evidence_content
    assert "Book: textbook-rag, Page: 11" in evidence_content
    assert "Section" not in evidence_content.split("\n\n")[1]  # No section metadata for chunk-2
    assert "It uses external sources" in evidence_content

    assert prompt.items[3].content == "Question: How does retrieval-augmented generation work?"

    # 3. Statistics assertions
    stats = prompt.statistics
    assert stats["total_sections"] == 5
    assert stats["evidence_chunks"] == 2
    assert stats["total_prompt_characters"] > 0
    assert stats["total_prompt_tokens_estimate"] == stats["total_prompt_characters"] // 4
    assert stats["compilation_duration"] > 0

    # 4. Metadata assertions
    meta = prompt.metadata
    assert meta["prompt_version"] == "1.0.0"
    assert meta["prompting_contract_version"] == "1.0.0"
    assert meta["retrieval_strategy"] == "semantic_similarity"
    assert meta["compilation_strategy"] == "rank_ordered_inclusion"

    # 5. Serialization method test
    prompt_str = prompt.to_string()
    assert "=== System Instructions ===" in prompt_str
    assert "=== Retrieved Evidence ===" in prompt_str
    assert "=== User Question ===" in prompt_str


def test_grounding_empty_query(sample_context: RetrievalContext) -> None:
    """Verifies that an empty query object or text raises a ValidationException."""
    engine = DefaultGroundingEngine()

    # None query
    with pytest.raises(ValidationException, match="Query cannot be None"):
        engine.compile_prompt(None, sample_context)  # type: ignore

    # Empty query text
    empty_query = Query(id=QueryId("q-empty"), original_question="", query_timestamp=datetime.now())
    with pytest.raises(ValidationException, match="Query text cannot be empty or blank"):
        engine.compile_prompt(empty_query, sample_context)

    # Blank query text
    blank_query = Query(
        id=QueryId("q-blank"),
        original_question="    ",
        query_timestamp=datetime.now(),
    )
    with pytest.raises(ValidationException, match="Query text cannot be empty or blank"):
        engine.compile_prompt(blank_query, sample_context)


def test_grounding_empty_context(sample_query: Query) -> None:
    """Verifies that a None or empty RetrievalContext raises a ValidationException."""
    engine = DefaultGroundingEngine()

    # None context
    with pytest.raises(ValidationException, match="RetrievalContext cannot be None"):
        engine.compile_prompt(sample_query, None)  # type: ignore

    # Empty context items list
    empty_context = RetrievalContext(book_id=BookId("test"), items=[], statistics={}, metadata={})
    with pytest.raises(ValidationException, match="RetrievalContext has no retrieved chunks"):
        engine.compile_prompt(sample_query, empty_context)


def test_grounding_duplicate_evidence(
    sample_query: Query, sample_context: RetrievalContext
) -> None:
    """Verifies that duplicate chunks in context items list raise a ValidationException."""
    engine = DefaultGroundingEngine()

    # Create duplicate chunk
    dup_chunk = RetrievedChunk(
        chunk_id=ChunkId("chunk-1"),  # Same chunk ID
        embedding_id=EmbeddingId("emb-dup"),
        chunk_text="Duplicate content",
        similarity_score=0.88,
        retrieval_rank=2,
        page_number=10,
        chapter_id=None,
        section_id=None,
        retrieval_timestamp=datetime.now(),
    )
    sample_context.items.append(dup_chunk)

    with pytest.raises(ValidationException, match="Duplicate ChunkId 'chunk-1'"):
        engine.compile_prompt(sample_query, sample_context)


def test_grounding_missing_chunk_text(
    sample_query: Query, sample_context: RetrievalContext
) -> None:
    """Verifies that a chunk with empty or missing text raises a ValidationException."""
    engine = DefaultGroundingEngine()

    bad_chunk = RetrievedChunk(
        chunk_id=ChunkId("chunk-bad"),
        embedding_id=EmbeddingId("emb-bad"),
        chunk_text="",  # Empty
        similarity_score=0.7,
        retrieval_rank=3,
        page_number=12,
        chapter_id=None,
        section_id=None,
        retrieval_timestamp=datetime.now(),
    )
    sample_context.items.append(bad_chunk)

    expected = "Missing chunk text in RetrievedChunk 'chunk-bad'"
    with pytest.raises(ValidationException, match=expected):
        engine.compile_prompt(sample_query, sample_context)


def test_grounding_invalid_rank_order(
    sample_query: Query, sample_context: RetrievalContext
) -> None:
    """Verifies that non-sequential rank numbering raises a ValidationException."""
    engine = DefaultGroundingEngine()

    # Create chunk with rank gap (ranks are 1, 3 instead of 1, 2)
    bad_chunk = RetrievedChunk(
        chunk_id=ChunkId("chunk-3"),
        embedding_id=EmbeddingId("emb-3"),
        chunk_text="Valid chunk text",
        similarity_score=0.7,
        retrieval_rank=3,  # gap!
        page_number=12,
        chapter_id=None,
        section_id=None,
        retrieval_timestamp=datetime.now(),
    )
    sample_context.items[1] = bad_chunk

    with pytest.raises(ValidationException, match="Invalid retrieval rank order"):
        engine.compile_prompt(sample_query, sample_context)


def test_grounding_oversized_truncation(
    sample_query: Query, sample_context: RetrievalContext
) -> None:
    """Verifies that chunks are deterministically truncated to stay within budget."""
    # Set maximum limit to 1500 characters (enough for base prompt + chunk 1,
    # but not enough for chunk 2)
    engine = DefaultGroundingEngine(max_prompt_chars=1500)
    prompt = engine.compile_prompt(sample_query, sample_context)

    # Assures prompt successfully compiles but only contains chunk-1
    assert prompt.statistics["evidence_chunks"] == 1
    evidence_content = prompt.items[2].content
    assert "chunk-1" in sample_context.items[0].chunk_id.value
    assert "RAG combines search" in evidence_content
    assert "It uses external sources" not in evidence_content


def test_grounding_oversized_base_fails(
    sample_query: Query, sample_context: RetrievalContext
) -> None:
    """Verifies that if base prompt instructions exceed the limit, ValidationException is raised."""
    # Base instructions alone are around 1000 characters. Limit to 200 characters.
    engine = DefaultGroundingEngine(max_prompt_chars=200)

    with pytest.raises(ValidationException, match=r"Base prompt size .* exceeds limit"):
        engine.compile_prompt(sample_query, sample_context)


def test_grounding_oversized_chunk_1_fails(
    sample_query: Query, sample_context: RetrievalContext
) -> None:
    """Verifies that if not even the top-ranked chunk fits, a ValidationException is raised."""
    # Limit is enough for base prompt (~1300 chars) but not enough to add chunk 1 (~1470 chars)
    engine = DefaultGroundingEngine(max_prompt_chars=1350)

    with pytest.raises(ValidationException, match="Cannot fit even the top-ranked chunk"):
        engine.compile_prompt(sample_query, sample_context)


def test_grounding_determinism(sample_query: Query, sample_context: RetrievalContext) -> None:
    """Verifies that compiling identical query and context twice produces identical outputs."""
    engine = DefaultGroundingEngine()

    prompt1 = engine.compile_prompt(sample_query, sample_context)
    prompt2 = engine.compile_prompt(sample_query, sample_context)

    # Identical content
    assert prompt1.to_string() == prompt2.to_string()
    # Identical statistics (compilation_duration is float, so we check others)
    assert prompt1.statistics["total_sections"] == prompt2.statistics["total_sections"]
    assert prompt1.statistics["evidence_chunks"] == prompt2.statistics["evidence_chunks"]
    chars1 = prompt1.statistics["total_prompt_characters"]
    chars2 = prompt2.statistics["total_prompt_characters"]
    assert chars1 == chars2
    # Identical metadata
    assert prompt1.metadata == prompt2.metadata
