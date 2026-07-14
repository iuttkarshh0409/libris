import time
from datetime import datetime

import pytest

from src.domain.engines.default_citation_engine import DefaultCitationEngine
from src.domain.entities.context import RetrievalContext, RetrievedChunk
from src.domain.entities.response import GeneratedResponse, ResponseItem, VerifiedResponse
from src.domain.value_objects.identifiers import (
    BookId,
    ChapterId,
    ChunkId,
    EmbeddingId,
    QueryId,
    ResponseId,
    SectionId,
)
from src.shared.exceptions import ValidationException


@pytest.fixture
def sample_context() -> RetrievalContext:
    """Fixture returning a standard valid RetrievalContext."""
    chunk1 = RetrievedChunk(
        chunk_id=ChunkId("chunk-1"),
        embedding_id=EmbeddingId("emb-1"),
        chunk_text="This is chunk one text explaining biology.",
        similarity_score=0.92,
        retrieval_rank=1,
        page_number=12,
        chapter_id=ChapterId("chapter-3"),
        section_id=SectionId("section-b"),
        retrieval_timestamp=datetime.now(),
    )
    chunk2 = RetrievedChunk(
        chunk_id=ChunkId("chunk-2"),
        embedding_id=EmbeddingId("emb-2"),
        chunk_text="This is chunk two text explaining chemistry.",
        similarity_score=0.85,
        retrieval_rank=2,
        page_number=15,
        chapter_id=ChapterId("chapter-4"),
        section_id=None,
        retrieval_timestamp=datetime.now(),
    )
    return RetrievalContext(
        book_id=BookId("test-science-book"),
        items=[chunk1, chunk2],
        statistics={"retrieval_duration": 0.05},
        metadata={
            "book_title": "Science textbook 101",
            "retrieval_strategy": "semantic_similarity",
        },
    )


@pytest.fixture
def sample_response() -> GeneratedResponse:
    """Fixture returning a standard valid GeneratedResponse."""
    item = ResponseItem(
        response_id=ResponseId("resp-1"),
        query_id=QueryId("query-1"),
        answer_text="Based on chunk-1 and chunk-2, biology and chemistry are related.",
        generation_timestamp=datetime.now(),
        model_identifier="gemini-1.5-pro",
        finish_reason="stop",
        token_usage={"total_tokens": 120},
    )
    return GeneratedResponse(
        book_id=BookId("test-science-book"),
        items=[item],
        statistics={"generation_duration": 0.4},
        metadata={"compilation_strategy": "rank_ordered_inclusion"},
    )


def test_citation_verification_success_explicit(
    sample_context: RetrievalContext, sample_response: GeneratedResponse
) -> None:
    """Verifies successful citation extraction, statistics compilation, and metadata propagation."""
    engine = DefaultCitationEngine()
    verified = engine.verify_citations(sample_response, sample_context)

    # 1. Base assertions
    assert isinstance(verified, VerifiedResponse)
    assert verified.book_id.value == "test-science-book"
    assert len(verified.items) == 1

    # 2. VerifiedResponseItem assertions
    item = verified.items[0]
    assert item.response_id.value == "resp-1"
    assert item.query_id.value == "query-1"
    assert item.answer_text == sample_response.generated_answer
    assert item.verification_timestamp is not None

    # Citations
    assert len(item.supporting_citations) == 2
    cit1 = item.supporting_citations[0]
    assert cit1.id.value == "cit-chunk-1"
    assert cit1.book_title == "Science textbook 101"
    assert cit1.page_number == 12
    assert cit1.chapter == "chapter-3"
    assert cit1.section == "section-b"
    assert cit1.retrieval_rank == 1
    assert cit1.similarity_score == 0.92

    cit2 = item.supporting_citations[1]
    assert cit2.id.value == "cit-chunk-2"
    assert cit2.page_number == 15
    assert cit2.chapter == "chapter-4"
    assert cit2.section is None

    # Excerpts mapping check
    assert len(item.supporting_excerpts) == 2
    assert item.supporting_excerpts[0] == "This is chunk one text explaining biology."
    assert item.supporting_excerpts[1] == "This is chunk two text explaining chemistry."

    # 3. Statistics assertions
    stats = verified.statistics
    assert stats["total_citations"] == 2
    assert stats["unique_pages"] == 2
    assert stats["unique_chapters"] == 2
    assert abs(stats["average_similarity"] - 0.885) < 0.001
    assert stats["verification_duration"] >= 0.0

    # 4. Metadata assertions
    meta = verified.metadata
    assert meta["citation_version"] == "1.0.0"
    assert meta["verification_strategy"] == "reconciled_matching"
    assert meta["retrieval_strategy"] == "semantic_similarity"
    assert meta["compilation_strategy"] == "rank_ordered_inclusion"


def test_citation_verification_success_fallback(
    sample_context: RetrievalContext, sample_response: GeneratedResponse
) -> None:
    """Verifies that all context chunks are cited if response has no explicit citation marks."""
    # Modify response text to have no mentions of chunk IDs
    sample_response.items[0]._answer_text = "Biology and chemistry are science fields."

    engine = DefaultCitationEngine()
    verified = engine.verify_citations(sample_response, sample_context)

    # Fallback to citing all items
    assert len(verified.items[0].supporting_citations) == 2


def test_citation_verification_success_bracketed(
    sample_context: RetrievalContext, sample_response: GeneratedResponse
) -> None:
    """Verifies parsing of bracketed ranks like [1] and [2]."""
    sample_response.items[0]._answer_text = "As stated in [1] and [2], science is fun."

    engine = DefaultCitationEngine()
    verified = engine.verify_citations(sample_response, sample_context)

    assert len(verified.items[0].supporting_citations) == 2
    assert verified.items[0].supporting_citations[0].chunk_reference.value == "chunk-1"
    assert verified.items[0].supporting_citations[1].chunk_reference.value == "chunk-2"


def test_citation_verification_empty_inputs() -> None:
    """Verifies that empty parameters raise ValidationException."""
    engine = DefaultCitationEngine()

    with pytest.raises(ValidationException, match="GeneratedResponse cannot be None"):
        engine.verify_citations(None, None)  # type: ignore


def test_citation_verification_inconsistent_book_ids(
    sample_context: RetrievalContext, sample_response: GeneratedResponse
) -> None:
    """Verifies that inconsistent book IDs raise ValidationException."""
    # Mutate response book id
    sample_response._book_id = BookId("inconsistent-book")

    engine = DefaultCitationEngine()
    with pytest.raises(ValidationException, match="Inconsistent book IDs"):
        engine.verify_citations(sample_response, sample_context)


def test_citation_verification_duplicate_chunks(
    sample_context: RetrievalContext, sample_response: GeneratedResponse
) -> None:
    """Verifies that duplicate chunks in context raise ValidationException."""
    # Append duplicate chunk
    dup_chunk = sample_context.items[0]
    sample_context.items.append(dup_chunk)

    engine = DefaultCitationEngine()
    with pytest.raises(ValidationException, match="Duplicate chunk found in context"):
        engine.verify_citations(sample_response, sample_context)


def test_citation_verification_orphan_chunk_id(
    sample_context: RetrievalContext, sample_response: GeneratedResponse
) -> None:
    """Verifies that response referencing missing chunk IDs raises ValidationException."""
    sample_response.items[0]._answer_text = "We reference chunk-999 which does not exist."

    engine = DefaultCitationEngine()
    with pytest.raises(ValidationException, match="Orphan citation chunk reference"):
        engine.verify_citations(sample_response, sample_context)


def test_citation_verification_orphan_rank(
    sample_context: RetrievalContext, sample_response: GeneratedResponse
) -> None:
    """Verifies that response referencing invalid bracketed rank raises ValidationException."""
    sample_response.items[0]._answer_text = "We reference [3] but context only has 2 chunks."

    engine = DefaultCitationEngine()
    with pytest.raises(ValidationException, match="Orphan citation rank reference"):
        engine.verify_citations(sample_response, sample_context)


def test_citation_verification_missing_page_number(
    sample_context: RetrievalContext, sample_response: GeneratedResponse
) -> None:
    """Verifies that chunk with invalid page number raises ValidationException."""
    # Mutate page number
    sample_context.items[0]._page_number = 0

    engine = DefaultCitationEngine()
    with pytest.raises(ValidationException, match="missing a valid page number"):
        engine.verify_citations(sample_response, sample_context)


def test_citation_verification_missing_chunk_text(
    sample_context: RetrievalContext, sample_response: GeneratedResponse
) -> None:
    """Verifies that chunk with empty text raises ValidationException."""
    # Mutate chunk text
    sample_context.items[0]._chunk_text = "  "

    engine = DefaultCitationEngine()
    with pytest.raises(ValidationException, match="missing chunk text"):
        engine.verify_citations(sample_response, sample_context)


def test_citation_verification_determinism(
    sample_context: RetrievalContext, sample_response: GeneratedResponse
) -> None:
    """Verifies that repeated executions return deterministic outputs."""
    engine = DefaultCitationEngine()

    res1 = engine.verify_citations(sample_response, sample_context)
    time.sleep(0.01)
    res2 = engine.verify_citations(sample_response, sample_context)

    # Identical values
    assert res1.book_id == res2.book_id
    assert len(res1.items) == len(res2.items)
    assert res1.items[0].answer_text == res2.items[0].answer_text
    assert len(res1.items[0].supporting_citations) == len(res2.items[0].supporting_citations)

    # Identical stats and metadata except execution duration
    assert res1.metadata == res2.metadata
    assert res1.statistics["total_citations"] == res2.statistics["total_citations"]
    assert res1.statistics["unique_pages"] == res2.statistics["unique_pages"]
    assert res1.statistics["unique_chapters"] == res2.statistics["unique_chapters"]
    assert res1.statistics["average_similarity"] == res2.statistics["average_similarity"]
