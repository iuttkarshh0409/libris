from datetime import datetime
from unittest.mock import Mock

from src.application.contracts.dto import (
    IngestDocumentRequest,
    IngestDocumentResponse,
    QueryRequest,
    QueryResponse,
)
from src.application.services.ingestion_application_service import IngestionApplicationService
from src.application.services.query_application_service import QueryApplicationService
from src.domain.entities.book import Book
from src.domain.entities.chapter import Chapter
from src.domain.entities.chunk import Chunk
from src.domain.entities.citation import Citation
from src.domain.entities.context import RetrievalContext
from src.domain.entities.page import Page
from src.domain.entities.prompt import Prompt
from src.domain.entities.response import GeneratedResponse, ResponseItem
from src.domain.entities.section import Section
from src.domain.value_objects.identifiers import (
    BookId,
    ChunkId,
    CitationId,
    PageId,
    QueryId,
    ResponseId,
)
from src.shared.contracts.result import Result
from src.shared.exceptions import DomainException, ValidationException


def test_ingestion_application_service_success() -> None:
    # 1. Setup mocks
    document_engine = Mock()
    chunking_engine = Mock()
    embedding_engine = Mock()
    indexing_engine = Mock()
    book_repository = Mock()

    # Stub document engine parse
    book_id = BookId("book-1")
    book = Book(
        id=book_id,
        title="Sample Book",
        author="Author",
        edition="1st",
        subject="RAG",
        file_name="sample.pdf",
        file_path="/data/sample.pdf",
        upload_timestamp=datetime.now(),
        total_pages=1,
        index_status="queued",
    )
    pages = [
        Page(
            id=PageId("page-1"),
            book_id=book_id,
            page_number=1,
            extracted_text="content",
            character_count=7,
        )
    ]
    chapters = [
        Chapter(
            id=Mock(),
            book_id=book_id,
            chapter_number="1",
            chapter_title="Intro",
            start_page=1,
            end_page=1,
        )
    ]
    sections = [Section(id=Mock(), chapter_id=Mock(), title="Sec 1", start_page=1, end_page=1)]
    from src.domain.entities.parsed_document import ParsedDocument

    parsed_doc = ParsedDocument(book, pages, chapters, sections)
    document_engine.parse_pdf.return_value = parsed_doc

    # Stub chunking engine
    chunks = [
        Chunk(
            id=ChunkId("chunk-1"),
            book_id=book_id,
            page_number=1,
            chunk_index=0,
            chunk_text="content",
            character_count=7,
            token_count=2,
        )
    ]
    from src.domain.entities.chunk_collection import ChunkCollection

    chunk_collection = ChunkCollection(book_id=book_id, chunks=chunks, statistics={}, metadata={})
    chunking_engine.generate_chunks.return_value = chunk_collection

    # Stub embedding engine
    from src.domain.entities.embedding_collection import EmbeddingCollection

    embedding_collection = EmbeddingCollection(
        book_id=book_id,
        embeddings=[Mock()],
        statistics={},
        metadata={},
    )
    embedding_engine.embed_chunks.return_value = embedding_collection

    # Instantiate service
    service = IngestionApplicationService(
        document_engine=document_engine,
        chunking_engine=chunking_engine,
        embedding_engine=embedding_engine,
        indexing_engine=indexing_engine,
        book_repository=book_repository,
    )

    request = IngestDocumentRequest(file_path="/data/sample.pdf")
    res: Result[IngestDocumentResponse] = service.ingest_document(request)

    # Assertions
    assert res.is_success is True
    assert res.value.book_id == book_id
    assert res.value.total_pages == 1
    assert res.value.total_chunks == 1

    # Verify orchestration order
    document_engine.parse_pdf.assert_called_once_with("/data/sample.pdf")
    assert book_repository.save.call_count == 2
    book_repository.save.assert_any_call(book)
    chunking_engine.generate_chunks.assert_called_once_with(parsed_doc)
    embedding_engine.embed_chunks.assert_called_once_with(chunk_collection)
    indexing_engine.add_to_index.assert_called_once_with(chunk_collection, embedding_collection)


def test_ingestion_application_service_validation_failure() -> None:
    service = IngestionApplicationService(
        document_engine=Mock(),
        chunking_engine=Mock(),
        embedding_engine=Mock(),
        indexing_engine=Mock(),
        book_repository=Mock(),
    )

    request = IngestDocumentRequest(file_path="  ")
    res: Result[IngestDocumentResponse] = service.ingest_document(request)

    assert res.is_failure is True
    assert isinstance(res.error, ValidationException)


def test_ingestion_application_service_error_propagation() -> None:
    document_engine = Mock()
    document_engine.parse_pdf.side_effect = DomainException("File not found")

    service = IngestionApplicationService(
        document_engine=document_engine,
        chunking_engine=Mock(),
        embedding_engine=Mock(),
        indexing_engine=Mock(),
        book_repository=Mock(),
    )

    request = IngestDocumentRequest(file_path="/data/missing.pdf")
    res: Result[IngestDocumentResponse] = service.ingest_document(request)

    assert res.is_failure is True
    assert isinstance(res.error, DomainException)
    assert str(res.error) == "File not found"


def test_query_application_service_success() -> None:
    # Setup mocks
    retrieval_engine = Mock()
    grounding_engine = Mock()
    generation_engine = Mock()
    citation_engine = Mock()
    book_repository = Mock()

    ret_context = RetrievalContext(
        book_id=BookId("test-book"), items=[], statistics={}, metadata={}
    )
    retrieval_engine.retrieve_context.return_value = ret_context

    # Stub grounding engine
    prompt = Prompt(
        book_id=BookId("test-book"),
        items=[],
        statistics={},
        metadata={},
    )
    grounding_engine.compile_prompt.return_value = prompt

    # Stub generation engine
    gen_response = GeneratedResponse(
        book_id=BookId("test-book"),
        items=[
            ResponseItem(
                response_id=ResponseId("resp-1"),
                query_id=QueryId("q-1"),
                answer_text="The answer",
                generation_timestamp=datetime.now(),
                model_identifier="test-model",
                finish_reason="stop",
            )
        ],
        statistics={},
        metadata={},
    )
    generation_engine.generate_response.return_value = gen_response

    # Stub citation engine
    citations = [
        Citation(
            id=CitationId("cit-1"),
            book_title="Sample Title",
            page_number=12,
            chunk_reference=ChunkId("chunk-1"),
            chapter="Chapter 1",
            section="Section A",
        )
    ]
    verified_response = GeneratedResponse(
        book_id=BookId("test-book"),
        items=[
            ResponseItem(
                response_id=ResponseId("resp-1"),
                query_id=QueryId("q-1"),
                answer_text="The answer with references",
                generation_timestamp=datetime.now(),
                model_identifier="test-model",
                finish_reason="stop",
            )
        ],
        statistics={},
        metadata={},
        supporting_citations=citations,
        supporting_excerpts=["ex-1"],
    )
    citation_engine.verify_citations.return_value = verified_response

    service = QueryApplicationService(
        retrieval_engine=retrieval_engine,
        grounding_engine=grounding_engine,
        generation_engine=generation_engine,
        citation_engine=citation_engine,
        book_repository=book_repository,
    )

    request = QueryRequest(query_text="What is RAG?", similarity_threshold=0.6, limit=3)
    res: Result[QueryResponse] = service.execute_query(request)

    assert res.is_success is True
    assert res.value.response_id.value == "resp-1"
    assert res.value.generated_answer == "The answer with references"
    assert len(res.value.citations) == 1
    assert res.value.citations[0].citation_id == "cit-1"
    assert res.value.citations[0].book_title == "Sample Title"
    assert res.value.citations[0].page_number == 12
    assert res.value.citations[0].chapter == "Chapter 1"
    assert res.value.citations[0].section == "Section A"

    # Verify orchestration order & overrides
    retrieval_engine.retrieve_context.assert_called_once()
    called_query = retrieval_engine.retrieve_context.call_args[0][0]
    assert called_query.original_question == "What is RAG?"
    assert retrieval_engine.retrieve_context.call_args[1] == {
        "similarity_threshold": 0.6,
        "limit": 3,
    }
    grounding_engine.compile_prompt.assert_called_once()
    generation_engine.generate_response.assert_called_once_with(prompt)
    citation_engine.verify_citations.assert_called_once_with(gen_response, ret_context)


def test_query_application_service_validation_failure() -> None:
    service = QueryApplicationService(
        retrieval_engine=Mock(),
        grounding_engine=Mock(),
        generation_engine=Mock(),
        citation_engine=Mock(),
        book_repository=Mock(),
    )

    request = QueryRequest(query_text="   ")
    res: Result[QueryResponse] = service.execute_query(request)

    assert res.is_failure is True
    assert isinstance(res.error, ValidationException)


def test_query_application_service_error_propagation() -> None:
    retrieval_engine = Mock()
    retrieval_engine.retrieve_context.side_effect = DomainException("Model generation failed")

    service = QueryApplicationService(
        retrieval_engine=retrieval_engine,
        grounding_engine=Mock(),
        generation_engine=Mock(),
        citation_engine=Mock(),
        book_repository=Mock(),
    )

    request = QueryRequest(query_text="What is RAG?")
    res: Result[QueryResponse] = service.execute_query(request)

    assert res.is_failure is True
    assert isinstance(res.error, DomainException)
    assert str(res.error) == "Model generation failed"
