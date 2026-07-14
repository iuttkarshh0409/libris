from datetime import datetime

import pytest

from src.application.container import container
from src.domain.entities.book import Book
from src.domain.entities.chapter import Chapter
from src.domain.entities.chunk import Chunk
from src.domain.entities.page import Page
from src.domain.entities.prompt import Prompt, SystemInstructionSection, TaskDefinitionSection
from src.domain.entities.section import Section
from src.domain.value_objects.identifiers import (
    BookId,
    ChapterId,
    ChunkId,
    PageId,
    SectionId,
)
from src.shared.contracts.result import Failure, Result, Success
from src.shared.exceptions import (
    ConfigurationException,
    DomainException,
    ProviderException,
    RetrievalException,
    ValidationException,
)


def test_result_monad_success() -> None:
    res: Result[str] = Success("value_content")
    assert res.is_success is True
    assert res.is_failure is False
    assert res.value == "value_content"

    with pytest.raises(ValueError, match="Cannot access error of a successful Result"):
        _ = res.error


def test_result_monad_failure() -> None:
    exc = ValueError("something went wrong")
    res: Result[str] = Failure(exc)
    assert res.is_success is False
    assert res.is_failure is True
    assert res.error == exc

    with pytest.raises(ValueError, match="Cannot access value of a failed Result"):
        _ = res.value


def test_exception_hierarchy() -> None:
    assert issubclass(ValidationException, DomainException)
    assert issubclass(ConfigurationException, DomainException)
    assert issubclass(RetrievalException, DomainException)
    assert issubclass(ProviderException, DomainException)


def test_domain_entity_book() -> None:
    book_id = BookId("book-123")
    now = datetime.now()
    book = Book(
        id=book_id,
        title="Introduction to Algorithms",
        author="CLRS",
        edition="3rd",
        subject="Computer Science",
        file_name="algorithms.pdf",
        file_path="/data/algorithms.pdf",
        upload_timestamp=now,
        total_pages=1292,
        index_status="queued",
    )
    assert book.id == book_id
    assert book.title == "Introduction to Algorithms"
    assert book.author == "CLRS"
    assert book.total_pages == 1292
    assert book.index_status == "queued"

    with pytest.raises(ValueError):
        Book(
            id=book_id,
            title="Introduction to Algorithms",
            author="CLRS",
            edition="3rd",
            subject="Computer Science",
            file_name="algorithms.pdf",
            file_path="/data/algorithms.pdf",
            upload_timestamp=now,
            total_pages=1292,
            index_status="invalid_status_here",
        )


def test_domain_hierarchy() -> None:
    book_id = BookId("book-1")
    chapter_id = ChapterId("chapter-1")
    section_id = SectionId("section-1")
    page_id = PageId("page-1")
    chunk_id = ChunkId("chunk-1")

    chapter = Chapter(
        id=chapter_id,
        book_id=book_id,
        chapter_number="1",
        chapter_title="Foundations",
        start_page=1,
        end_page=20,
    )
    assert chapter.id == chapter_id

    section = Section(
        id=section_id,
        chapter_id=chapter_id,
        title="Insertion Sort",
        start_page=2,
        end_page=10,
    )
    assert section.id == section_id

    page = Page(
        id=page_id,
        book_id=book_id,
        page_number=1,
        extracted_text="This is page 1",
        character_count=14,
    )
    assert page.id == page_id

    chunk = Chunk(
        id=chunk_id,
        book_id=book_id,
        page_number=1,
        chunk_index=0,
        chunk_text="This is page 1",
        character_count=14,
        token_count=4,
        chapter_id=chapter_id,
        section_id=section_id,
    )
    assert chunk.id == chunk_id

    prompt = Prompt(
        book_id=BookId("book-1"),
        items=[
            SystemInstructionSection("sys-instructions"),
            TaskDefinitionSection("task-def"),
        ],
        statistics={"stat": "val"},
        metadata={"meta": "val"},
    )
    assert prompt.book_id == BookId("book-1")
    assert len(prompt.items) == 2
    assert prompt.items[0].content == "sys-instructions"
    assert prompt.items[1].content == "task-def"
    assert prompt.statistics == {"stat": "val"}
    assert prompt.metadata == {"meta": "val"}


def test_di_container_wiring() -> None:
    assert container.storage_provider is not None
    assert container.document_provider is not None
    assert container.index_provider is not None
    assert container.embedding_provider is not None
    assert container.prompt_compiler is not None
    assert container.llm_provider is not None
    assert container.book_repository is not None
    assert container.knowledge_index_repository is not None
    assert container.document_engine is not None
    assert container.chunking_engine is not None
    assert container.embedding_engine is not None
    assert container.indexing_engine is not None
    assert container.retrieval_engine is not None
    assert container.grounding_engine is not None
    assert container.generation_engine is not None
    assert container.citation_engine is not None
    assert container.ingestion_service is not None
    assert container.query_service is not None
