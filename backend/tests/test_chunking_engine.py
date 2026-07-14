from datetime import datetime

import pytest

from src.domain.engines.default_chunking_engine import DefaultChunkingEngine
from src.domain.entities.book import Book
from src.domain.entities.chapter import Chapter
from src.domain.entities.page import Page
from src.domain.entities.parsed_document import ParsedDocument
from src.domain.entities.section import Section
from src.domain.value_objects.identifiers import BookId, ChapterId, PageId, SectionId
from src.shared.exceptions import ValidationException


def _create_dummy_document(
    pages_data: list[tuple[int, str]],
    chapters_data: list[tuple[str, int, int]],  # title, start, end
    sections_data: list[tuple[str, int, int]],  # title, start, end
) -> ParsedDocument:
    book_id = BookId("dummy-book-id")
    book = Book(
        id=book_id,
        title="Test Book",
        author="Test Author",
        edition="1st",
        subject="Testing",
        file_name="test.pdf",
        file_path="test.pdf",
        upload_timestamp=datetime.now(),
        total_pages=len(pages_data),
        index_status="queued",
    )

    pages = []
    for num, text in pages_data:
        pages.append(
            Page(
                id=PageId(f"page-id-{num}"),
                book_id=book_id,
                page_number=num,
                extracted_text=text,
                character_count=len(text),
            )
        )

    chapters = []
    for idx, (title, start, end) in enumerate(chapters_data):
        chapters.append(
            Chapter(
                id=ChapterId(f"chapter-id-{idx}"),
                book_id=book_id,
                chapter_number=str(idx + 1),
                chapter_title=title,
                start_page=start,
                end_page=end,
            )
        )

    sections = []
    for idx, (title, start, end) in enumerate(sections_data):
        sections.append(
            Section(
                id=SectionId(f"section-id-{idx}"),
                chapter_id=chapters[0].id if chapters else ChapterId("dummy-chap"),
                title=title,
                start_page=start,
                end_page=end,
            )
        )

    return ParsedDocument(book=book, pages=pages, chapters=chapters, sections=sections)


def test_chunking_engine_single_page() -> None:
    doc = _create_dummy_document(
        pages_data=[(1, "Paragraph one.\n\nParagraph two.")],
        chapters_data=[("Chapter 1", 1, 1)],
        sections_data=[("Section 1.1", 1, 1)],
    )

    engine = DefaultChunkingEngine(max_chunk_size=100, overlap_size=20)
    collection = engine.generate_chunks(doc)

    assert collection.book_id == doc.book.id
    assert collection.total_chunks > 0
    assert len(collection.chunks) == collection.total_chunks
    assert collection.metadata["chunking_strategy"] == "recursive_semantic"

    # Validate first chunk properties
    first = collection.chunks[0]
    assert first.book_id == doc.book.id
    assert first.page_number == 1
    assert first.source_page_start == 1
    assert first.source_page_end == 1
    assert first.chunk_index == 0
    assert first.chapter_id is not None
    assert first.section_id is not None
    assert first.character_count == len(first.chunk_text)
    assert first.token_count > 0


def test_chunking_engine_multi_page_and_linked_sequence() -> None:
    doc = _create_dummy_document(
        pages_data=[
            (1, "This is page 1 content."),
            (2, "This is page 2 content."),
        ],
        chapters_data=[("Chapter 1", 1, 2)],
        sections_data=[("Section 1.1", 1, 2)],
    )

    engine = DefaultChunkingEngine(max_chunk_size=50, overlap_size=10)
    collection = engine.generate_chunks(doc)

    assert collection.total_chunks == 2
    chunks = collection.chunks

    # Verify doubly-linked list
    assert chunks[0].previous_chunk_id is None
    assert chunks[0].next_chunk_id == chunks[1].id
    assert chunks[1].previous_chunk_id == chunks[0].id
    assert chunks[1].next_chunk_id is None

    # Verify page numbers match
    assert chunks[0].page_number == 1
    assert chunks[1].page_number == 2


def test_chunking_engine_multiple_chapters_and_sections() -> None:
    doc = _create_dummy_document(
        pages_data=[
            (1, "Chap 1 Sec 1 text."),
            (2, "Chap 2 Sec 2 text."),
        ],
        chapters_data=[
            ("Chapter 1", 1, 1),
            ("Chapter 2", 2, 2),
        ],
        sections_data=[
            ("Section 1.1", 1, 1),
            ("Section 2.1", 2, 2),
        ],
    )

    engine = DefaultChunkingEngine(max_chunk_size=100, overlap_size=10)
    collection = engine.generate_chunks(doc)

    assert len(collection.chunks) == 2
    c1, c2 = collection.chunks

    # Verify no cross-chapter chunking: each chunk maps to its exact page's chapter/section
    assert c1.chapter_id == doc.chapters[0].id
    assert c1.section_id == doc.sections[0].id

    assert c2.chapter_id == doc.chapters[1].id
    assert c2.section_id == doc.sections[1].id


def test_chunking_engine_overlap_correctness() -> None:
    # A single page text that will split into two chunks
    # Max size = 30, Overlap = 10
    doc = _create_dummy_document(
        pages_data=[(1, "A very long sentence here that splits.")],
        chapters_data=[("Chapter 1", 1, 1)],
        sections_data=[("Section 1.1", 1, 1)],
    )

    engine = DefaultChunkingEngine(max_chunk_size=30, overlap_size=10)
    collection = engine.generate_chunks(doc)

    assert len(collection.chunks) == 2
    _, c2 = collection.chunks

    # Verify overlap: c2 should contain characters from the end of c1
    # c1 = "A very long sentence here" (length 25)
    # c2 starts with overlap from c1 (e.g. "here")
    assert "here" in c2.chunk_text


def test_chunking_engine_deterministic_output() -> None:
    doc = _create_dummy_document(
        pages_data=[(1, "Paragraph one.\n\nParagraph two.\n\nParagraph three.")],
        chapters_data=[("Chapter 1", 1, 1)],
        sections_data=[("Section 1.1", 1, 1)],
    )

    engine = DefaultChunkingEngine(max_chunk_size=50, overlap_size=10)
    col1 = engine.generate_chunks(doc)
    col2 = engine.generate_chunks(doc)

    assert col1.total_chunks == col2.total_chunks
    for i in range(col1.total_chunks):
        assert col1.chunks[i].chunk_text == col2.chunks[i].chunk_text
        assert col1.chunks[i].chunk_index == col2.chunks[i].chunk_index
        assert col1.chunks[i].page_number == col2.chunks[i].page_number
        assert col1.chunks[i].chapter_id == col2.chunks[i].chapter_id
        assert col1.chunks[i].section_id == col2.chunks[i].section_id


def test_chunking_engine_empty_document() -> None:
    doc = _create_dummy_document(
        pages_data=[], chapters_data=[("Chapter 1", 1, 1)], sections_data=[("Section 1.1", 1, 1)]
    )

    engine = DefaultChunkingEngine()
    with pytest.raises(ValidationException, match="no pages"):
        engine.generate_chunks(doc)


def test_chunking_engine_invalid_document_page_ordering() -> None:
    # Pages duplicate
    doc1 = _create_dummy_document(
        pages_data=[(1, "Page 1"), (1, "Page 1 again")],
        chapters_data=[("Chapter 1", 1, 1)],
        sections_data=[("Section 1.1", 1, 1)],
    )
    engine = DefaultChunkingEngine()
    with pytest.raises(ValidationException, match="Duplicate page number"):
        engine.generate_chunks(doc1)

    # Pages out of order
    doc2 = _create_dummy_document(
        pages_data=[(2, "Page 2"), (1, "Page 1")],
        chapters_data=[("Chapter 1", 1, 2)],
        sections_data=[("Section 1.1", 1, 2)],
    )
    with pytest.raises(ValidationException, match="ascending order"):
        engine.generate_chunks(doc2)


def test_chunking_engine_page_outside_boundaries() -> None:
    doc = _create_dummy_document(
        pages_data=[(1, "Page 1"), (2, "Page 2")],
        chapters_data=[("Chapter 1", 1, 1)],  # Chapter stops at page 1
        sections_data=[("Section 1.1", 1, 1)],
    )

    engine = DefaultChunkingEngine()
    with pytest.raises(ValidationException, match="does not belong to any chapter"):
        engine.generate_chunks(doc)


def test_chunking_engine_paragraph_preservation() -> None:
    # Document contains paragraphs that fit within 100 characters.
    # Verify they are not split.
    doc = _create_dummy_document(
        pages_data=[
            (1, "Header line\n\nFirst paragraph content here.\n\nSecond paragraph content.")
        ],
        chapters_data=[("Chapter 1", 1, 1)],
        sections_data=[("Section 1.1", 1, 1)],
    )

    engine = DefaultChunkingEngine(max_chunk_size=100, overlap_size=10)
    collection = engine.generate_chunks(doc)

    # All text is split by paragraph and merged.
    # The header line is "Header line", first paragraph is "First paragraph content here.",
    # second is "Second paragraph content."
    # Since "Header line" + "First paragraph content here." = 11 + 30 = 41 <= 100, they merge.
    # "Second paragraph content" is 25. Adding it: 41 + 2 + 25 = 68 <= 100.
    # So it fits in a single chunk!
    assert len(collection.chunks) == 1
    assert collection.chunks[0].chunk_text.count("\n\n") == 2


def test_chunking_engine_sentence_fallback() -> None:
    # A single paragraph of 80 characters. Max size is 45.
    # It must split at sentence boundaries.
    text = "This is the first sentence. And this is the second sentence."
    doc = _create_dummy_document(
        pages_data=[(1, text)],
        chapters_data=[("Chapter 1", 1, 1)],
        sections_data=[("Section 1.1", 1, 1)],
    )

    engine = DefaultChunkingEngine(max_chunk_size=45, overlap_size=5)
    collection = engine.generate_chunks(doc)

    # Should split into two chunks:
    # "This is the first sentence." (27 chars)
    # "And this is the second sentence." (32 chars)
    assert len(collection.chunks) == 2
    assert collection.chunks[0].chunk_text == "This is the first sentence."
    assert collection.chunks[1].chunk_text == "And this is the second sentence."
