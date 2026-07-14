import os
import re
import uuid
from datetime import datetime

from loguru import logger

from src.domain.entities.book import Book
from src.domain.entities.chapter import Chapter
from src.domain.entities.page import Page
from src.domain.entities.parsed_document import ParsedDocument
from src.domain.entities.section import Section
from src.domain.providers.document import DocumentProvider
from src.domain.value_objects.identifiers import BookId, ChapterId, PageId, SectionId
from src.shared.exceptions import DomainException, ValidationException


class DefaultDocumentEngine:
    """Production implementation of DocumentEngine.

    Translates raw PDF extraction artifacts from DocumentProvider into
    a structured domain-integrity validated ParsedDocument aggregate.
    """

    def __init__(self, document_provider: DocumentProvider) -> None:
        self._document_provider = document_provider

    def parse_pdf(self, file_path: str) -> ParsedDocument:
        """Parses a textbook PDF file into a structured ParsedDocument."""
        logger.info(f"Parsing PDF document from file path: {file_path}")

        # 1. Invoke provider to extract structured content (provider owns filesystem resolution)
        extraction_result = self._document_provider.extract_document(file_path)

        if extraction_result.is_failure:
            err_msg = str(extraction_result.error)
            logger.error(f"Document extraction failed: {err_msg}")
            if "not found" in err_msg.lower() or "no such file" in err_msg.lower():
                raise ValidationException(f"File does not exist: {file_path}")
            raise DomainException(f"Extraction failed: {err_msg}")

        extracted_doc = extraction_result.value

        # 2. Validate extracted document properties
        if extracted_doc.page_count <= 0:
            logger.error("Extracted document contains no pages")
            raise ValidationException("Empty document detected.")
        if not extracted_doc.pages:
            logger.error("Extracted document has empty page list")
            raise ValidationException("Empty document detected.")

        # 3. Construct Book entity
        book_id = BookId(str(uuid.uuid4()))
        title = extracted_doc.metadata.get("title")
        author = extracted_doc.metadata.get("author")
        edition = extracted_doc.metadata.get("edition")
        subject = extracted_doc.metadata.get("subject")

        book = Book(
            id=book_id,
            title=title,
            author=author,
            edition=edition,
            subject=subject,
            file_name=os.path.basename(file_path),
            file_path=file_path,
            upload_timestamp=datetime.now(),
            total_pages=extracted_doc.page_count,
            index_status="queued",
        )
        logger.info(f"Book entity created with ID: {book_id.value}")

        # 5. Construct Page entities with validations
        pages = []
        page_numbers = set()
        for ext_page in extracted_doc.pages:
            # Validate duplicate page numbers
            if ext_page.page_number in page_numbers:
                logger.error(f"Duplicate page number {ext_page.page_number} detected")
                raise ValidationException(f"Duplicate page number {ext_page.page_number} detected.")
            page_numbers.add(ext_page.page_number)

            # Validate missing text (warn and ignore, don't crash)
            if ext_page.text is None or not ext_page.text.strip():
                logger.warning(
                    f"Ignoring page {ext_page.page_number}: it has missing or empty text."
                )
                continue

            page_id = PageId(str(uuid.uuid4()))
            page = Page(
                id=page_id,
                book_id=book_id,
                page_number=ext_page.page_number,
                extracted_text=ext_page.text,
                character_count=len(ext_page.text),
            )
            pages.append(page)

        if not pages:
            logger.error("All document pages are empty or contain no text")
            raise ValidationException("All document pages are empty or contain no text.")

        # Sort pages to ensure proper ordering
        pages.sort(key=lambda p: p.page_number)
        logger.info(f"Pages constructed successfully. Total: {len(pages)}")

        # 6. Chapter & Section Detection (Deterministic heading check)
        chapters = []
        sections = []

        # Find heading lines representing Chapters or Sections
        # Chapter pattern e.g., "Chapter 1", "CHAPTER I", "Chapter 12 - Intro"
        chapter_regex = re.compile(
            r"^chapter\s+(\d+|[ivxlcdm]+)\b(?:\s*[:-]\s*|\s+)?(.*)$", re.IGNORECASE
        )
        # Section pattern e.g., "Section 1.1", "1.2 Section title", "12.3.4 Title"
        section_regex = re.compile(
            r"^(?:section\s+)?(\d+\.\d+)\b(?:\s*[:-]\s*|\s+)?(.*)$", re.IGNORECASE
        )

        detected_chapters_info = []  # List of tuples: (page_number, chapter_num, chapter_title)
        detected_sections_info = []  # List of tuples: (page_number, section_num, section_title)

        for page in pages:
            lines = page.extracted_text.split("\n")
            for line in lines:
                line_stripped = line.strip()
                chap_match = chapter_regex.match(line_stripped)
                if chap_match:
                    chap_num = chap_match.group(1)
                    chap_title = chap_match.group(2).strip() or f"Chapter {chap_num}"
                    detected_chapters_info.append((page.page_number, chap_num, chap_title))
                    break  # Keep first detected chapter per page

                sec_match = section_regex.match(line_stripped)
                if sec_match:
                    sec_num = sec_match.group(1)
                    sec_title = sec_match.group(2).strip() or f"Section {sec_num}"
                    detected_sections_info.append((page.page_number, sec_num, sec_title))

        # Construct Chapter & Section entities
        if not detected_chapters_info:
            # Fallback to single default chapter representing the whole book
            logger.info("No chapters detected. Creating default chapter.")
            default_chap_id = ChapterId(str(uuid.uuid4()))
            default_chapter = Chapter(
                id=default_chap_id,
                book_id=book_id,
                chapter_number="1",
                chapter_title="Default Chapter",
                start_page=1,
                end_page=book.total_pages,
            )
            chapters.append(default_chapter)

            # Fallback section
            default_sec_id = SectionId(str(uuid.uuid4()))
            default_section = Section(
                id=default_sec_id,
                chapter_id=default_chap_id,
                title="Default Section",
                start_page=1,
                end_page=book.total_pages,
            )
            sections.append(default_section)
        else:
            # Create chapters based on detected outlines
            detected_chapters_info.sort(key=lambda x: x[0])

            # Ensure the first chapter starts on page 1 to include prefix pages
            first_chap = detected_chapters_info[0]
            detected_chapters_info[0] = (1, first_chap[1], first_chap[2])

            for i, info in enumerate(detected_chapters_info):
                start_page, chap_num, chap_title = info
                if i < len(detected_chapters_info) - 1:
                    end_page = detected_chapters_info[i + 1][0] - 1
                else:
                    end_page = book.total_pages

                # Safeguard page boundary crossing
                if end_page < start_page:
                    end_page = start_page

                chapter_id = ChapterId(str(uuid.uuid4()))
                chapter = Chapter(
                    id=chapter_id,
                    book_id=book_id,
                    chapter_number=chap_num,
                    chapter_title=chap_title,
                    start_page=start_page,
                    end_page=end_page,
                )
                chapters.append(chapter)

                # Find sections belonging to this chapter
                chapter_sections = [
                    sec for sec in detected_sections_info if start_page <= sec[0] <= end_page
                ]
                if not chapter_sections:
                    # Fallback single section for this chapter
                    default_sec_id = SectionId(str(uuid.uuid4()))
                    default_section = Section(
                        id=default_sec_id,
                        chapter_id=chapter_id,
                        title="Default Section",
                        start_page=start_page,
                        end_page=end_page,
                    )
                    sections.append(default_section)
                else:
                    chapter_sections.sort(key=lambda x: x[0])
                    # Ensure first section starts at the chapter's start page
                    first_sec = chapter_sections[0]
                    chapter_sections[0] = (start_page, first_sec[1], first_sec[2])

                    for j, s_info in enumerate(chapter_sections):
                        s_start, _s_num, s_title = s_info
                        if j < len(chapter_sections) - 1:
                            s_end = chapter_sections[j + 1][0] - 1
                        else:
                            s_end = end_page

                        if s_end < s_start:
                            s_end = s_start

                        section_id = SectionId(str(uuid.uuid4()))
                        section = Section(
                            id=section_id,
                            chapter_id=chapter_id,
                            title=s_title,
                            start_page=s_start,
                            end_page=s_end,
                        )
                        sections.append(section)

        logger.info(f"Parsed outline: {len(chapters)} chapters, {len(sections)} sections")
        logger.info("Document successfully parsed")

        return ParsedDocument(
            book=book,
            pages=pages,
            chapters=chapters,
            sections=sections,
        )
