from pathlib import Path
from unittest.mock import Mock

import pytest

from src.domain.engines.default_document_engine import DefaultDocumentEngine
from src.domain.providers.document import ExtractedDocument, ExtractedPage
from src.shared.contracts.result import Failure, Success
from src.shared.exceptions import DomainException, ProviderException, ValidationException


def test_document_engine_success(tmp_path: Path) -> None:
    # 1. Create a dummy file in tmp_path to bypass existence checks
    dummy_file = tmp_path / "textbook.pdf"
    dummy_file.write_bytes(b"%PDF-1.4...")

    # 2. Mock DocumentProvider returning successful extraction with outline
    provider = Mock()
    metadata: dict[str, str | None] = {
        "title": "Clean Code",
        "author": "Robert C. Martin",
        "subject": "Software Engineering",
        "creator": "Word",
        "producer": "Adobe",
    }
    extracted_doc = ExtractedDocument(
        metadata=metadata,
        page_count=3,
        pages=[
            ExtractedPage(page_number=1, text="Chapter 1: Clean Code\nThis is chapter one."),
            ExtractedPage(
                page_number=2, text="Section 1.1: Meaningful Names\nUse intention-revealing names."
            ),
            ExtractedPage(page_number=3, text="Chapter 2: Functions\nKeep them small."),
        ],
    )
    provider.extract_document.return_value = Success(extracted_doc)

    # 3. Instantiate engine and parse
    engine = DefaultDocumentEngine(document_provider=provider)
    parsed_doc = engine.parse_pdf(str(dummy_file))

    # 4. Assertions - Book
    assert parsed_doc.book.title == "Clean Code"
    assert parsed_doc.book.author == "Robert C. Martin"
    assert parsed_doc.book.edition is None
    assert parsed_doc.book.subject == "Software Engineering"
    assert parsed_doc.book.file_name == "textbook.pdf"
    assert parsed_doc.book.total_pages == 3

    # 5. Assertions - Pages & Ordering
    assert len(parsed_doc.pages) == 3
    assert parsed_doc.pages[0].page_number == 1
    assert parsed_doc.pages[0].extracted_text == "Chapter 1: Clean Code\nThis is chapter one."
    assert parsed_doc.pages[1].page_number == 2
    assert parsed_doc.pages[2].page_number == 3

    # 6. Assertions - Chapters
    assert len(parsed_doc.chapters) == 2
    # Chapter 1
    assert parsed_doc.chapters[0].chapter_number == "1"
    assert parsed_doc.chapters[0].chapter_title == "Clean Code"
    assert parsed_doc.chapters[0].start_page == 1
    assert parsed_doc.chapters[0].end_page == 2
    # Chapter 2
    assert parsed_doc.chapters[1].chapter_number == "2"
    assert parsed_doc.chapters[1].chapter_title == "Functions"
    assert parsed_doc.chapters[1].start_page == 3
    assert parsed_doc.chapters[1].end_page == 3

    # 7. Assertions - Sections
    assert len(parsed_doc.sections) == 2
    # Section 1 belongs to Chapter 1
    assert parsed_doc.sections[0].chapter_id == parsed_doc.chapters[0].id
    assert parsed_doc.sections[0].title == "Meaningful Names"
    assert parsed_doc.sections[0].start_page == 1
    assert parsed_doc.sections[0].end_page == 2
    # Section 2 belongs to Chapter 2 (fallback Default Section for Chapter 2)
    assert parsed_doc.sections[1].chapter_id == parsed_doc.chapters[1].id
    assert parsed_doc.sections[1].title == "Default Section"
    assert parsed_doc.sections[1].start_page == 3
    assert parsed_doc.sections[1].end_page == 3

    # 8. Relationship integrity checks
    for page in parsed_doc.pages:
        assert page.book_id == parsed_doc.book.id
    for chapter in parsed_doc.chapters:
        assert chapter.book_id == parsed_doc.book.id


def test_document_engine_fallback_behavior(tmp_path: Path) -> None:
    dummy_file = tmp_path / "textbook.pdf"
    dummy_file.write_bytes(b"%PDF...")

    provider = Mock()
    # Plain document with no detectable headings
    extracted_doc = ExtractedDocument(
        metadata={},
        page_count=2,
        pages=[
            ExtractedPage(page_number=1, text="Just plain text here."),
            ExtractedPage(page_number=2, text="More text without headings."),
        ],
    )
    provider.extract_document.return_value = Success(extracted_doc)

    engine = DefaultDocumentEngine(document_provider=provider)
    parsed_doc = engine.parse_pdf(str(dummy_file))

    # Assert fallback chapter and section
    assert len(parsed_doc.chapters) == 1
    assert parsed_doc.chapters[0].chapter_title == "Default Chapter"
    assert parsed_doc.chapters[0].start_page == 1
    assert parsed_doc.chapters[0].end_page == 2

    assert len(parsed_doc.sections) == 1
    assert parsed_doc.sections[0].chapter_id == parsed_doc.chapters[0].id
    assert parsed_doc.sections[0].title == "Default Section"
    assert parsed_doc.sections[0].start_page == 1
    assert parsed_doc.sections[0].end_page == 2


def test_document_engine_missing_metadata(tmp_path: Path) -> None:
    dummy_file = tmp_path / "textbook.pdf"
    dummy_file.write_bytes(b"%PDF...")

    provider = Mock()
    extracted_doc = ExtractedDocument(
        metadata={},  # Empty metadata
        page_count=1,
        pages=[ExtractedPage(page_number=1, text="Text")],
    )
    provider.extract_document.return_value = Success(extracted_doc)

    engine = DefaultDocumentEngine(document_provider=provider)
    parsed_doc = engine.parse_pdf(str(dummy_file))

    # Should default book fields safely
    assert parsed_doc.book.title is None
    assert parsed_doc.book.author is None
    assert parsed_doc.book.subject is None


def test_document_engine_empty_document(tmp_path: Path) -> None:
    dummy_file = tmp_path / "empty.pdf"
    dummy_file.write_bytes(b"")

    provider = Mock()
    extracted_doc = ExtractedDocument(metadata={}, page_count=0, pages=[])
    provider.extract_document.return_value = Success(extracted_doc)

    engine = DefaultDocumentEngine(document_provider=provider)
    with pytest.raises(ValidationException, match="Empty document detected"):
        engine.parse_pdf(str(dummy_file))


def test_document_engine_duplicate_page_numbers(tmp_path: Path) -> None:
    dummy_file = tmp_path / "dup.pdf"
    dummy_file.write_bytes(b"%PDF...")

    provider = Mock()
    extracted_doc = ExtractedDocument(
        metadata={},
        page_count=2,
        pages=[
            ExtractedPage(page_number=1, text="Text 1"),
            ExtractedPage(page_number=1, text="Text 2"),  # Duplicate number!
        ],
    )
    provider.extract_document.return_value = Success(extracted_doc)

    engine = DefaultDocumentEngine(document_provider=provider)
    with pytest.raises(ValidationException, match="Duplicate page number"):
        engine.parse_pdf(str(dummy_file))


def test_document_engine_missing_page_text(tmp_path: Path) -> None:
    dummy_file = tmp_path / "empty_page.pdf"
    dummy_file.write_bytes(b"%PDF...")

    provider = Mock()
    extracted_doc = ExtractedDocument(
        metadata={},
        page_count=2,
        pages=[
            ExtractedPage(page_number=1, text="Valid text"),
            ExtractedPage(page_number=2, text="   "),  # Blank/missing text
        ],
    )
    provider.extract_document.return_value = Success(extracted_doc)

    engine = DefaultDocumentEngine(document_provider=provider)
    with pytest.raises(ValidationException, match="missing or empty text"):
        engine.parse_pdf(str(dummy_file))


def test_document_engine_missing_file() -> None:
    provider = Mock()
    provider.extract_document.return_value = Failure(
        ProviderException("File not found: nonexistent_file.pdf")
    )
    engine = DefaultDocumentEngine(document_provider=provider)
    with pytest.raises(ValidationException, match="File does not exist"):
        engine.parse_pdf("nonexistent_file.pdf")


def test_document_engine_extraction_failure(tmp_path: Path) -> None:
    dummy_file = tmp_path / "corrupt.pdf"
    dummy_file.write_bytes(b"corrupt")

    provider = Mock()
    provider.extract_document.return_value = Failure(DomainException("Extraction failed"))

    engine = DefaultDocumentEngine(document_provider=provider)
    with pytest.raises(DomainException, match="Extraction failed"):
        engine.parse_pdf(str(dummy_file))
