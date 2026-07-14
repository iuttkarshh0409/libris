import re
import uuid
from typing import TypedDict

from loguru import logger

from src.domain.entities.chapter import Chapter
from src.domain.entities.chunk import Chunk
from src.domain.entities.chunk_collection import ChunkCollection
from src.domain.entities.parsed_document import ParsedDocument
from src.domain.entities.section import Section
from src.domain.value_objects.identifiers import ChapterId, ChunkId, SectionId
from src.shared.exceptions import ValidationException


class _TempChunk(TypedDict):
    id: ChunkId
    page_number: int
    chapter_id: ChapterId
    section_id: SectionId
    text: str


class DefaultChunkingEngine:
    """Concrete implementation of ChunkingEngine.

    Splits a ParsedDocument into semantic, overlapping, and linked Chunk entities.
    """

    def __init__(self, max_chunk_size: int = 1000, overlap_size: int = 200) -> None:
        if max_chunk_size <= 0:
            raise ValueError("max_chunk_size must be greater than 0")
        if overlap_size < 0:
            raise ValueError("overlap_size must be greater than or equal to 0")
        if overlap_size >= max_chunk_size:
            raise ValueError("overlap_size must be less than max_chunk_size")

        self.max_chunk_size = max_chunk_size
        self.overlap_size = overlap_size

    def generate_chunks(self, document: ParsedDocument) -> ChunkCollection:
        """Segments a ParsedDocument into overlapping semantic Chunk entities."""
        logger.info("Chunk generation started")

        # 1. Validation checks
        if not document.pages:
            logger.error("Chunk validation failed: Document has no pages.")
            raise ValidationException("Document has no pages.")
        if not document.chapters:
            logger.error("Chunk validation failed: Document has no chapters.")
            raise ValidationException("Document has no chapters.")
        if not document.sections:
            logger.error("Chunk validation failed: Document has no sections.")
            raise ValidationException("Document has no sections.")

        # Check page ordering and duplicates
        seen_pages = set()
        for idx, page in enumerate(document.pages):
            if page.page_number in seen_pages:
                logger.error(f"Chunk validation failed: Duplicate page number {page.page_number}")
                raise ValidationException(f"Duplicate page number {page.page_number}")
            if idx > 0 and page.page_number <= document.pages[idx - 1].page_number:
                logger.error("Chunk validation failed: Pages are not in ascending order.")
                raise ValidationException("Pages are not in ascending order.")
            seen_pages.add(page.page_number)

        # 2. Iterate and chunk page by page
        temp_chunks: list[_TempChunk] = []
        book_id = document.book.id

        for page in document.pages:
            chapter_id, section_id = self._find_chapter_and_section_for_page(
                page.page_number, document.chapters, document.sections
            )

            # Generate split texts for page
            split_texts = self._split_text(
                page.extracted_text, self.max_chunk_size, self.overlap_size
            )

            for text in split_texts:
                temp_chunks.append(
                    {
                        "id": ChunkId(str(uuid.uuid4())),
                        "page_number": page.page_number,
                        "chapter_id": chapter_id,
                        "section_id": section_id,
                        "text": text,
                    }
                )

        # 3. Build doubly-linked sequence of chunks
        chunks = []
        total_chunks = len(temp_chunks)
        chunk_ids = set()

        for idx, temp in enumerate(temp_chunks):
            chunk_id = temp["id"]
            if chunk_id in chunk_ids:
                logger.error("Chunk validation failed: Duplicate ChunkId detected.")
                raise ValidationException("Duplicate ChunkId detected.")
            chunk_ids.add(chunk_id)

            prev_id = temp_chunks[idx - 1]["id"] if idx > 0 else None
            next_id = temp_chunks[idx + 1]["id"] if idx < total_chunks - 1 else None

            # Token count estimation: 4 characters per token
            text = temp["text"]
            token_count = max(1, len(text) // 4)

            chunk = Chunk(
                id=chunk_id,
                book_id=book_id,
                page_number=temp["page_number"],
                chunk_index=idx,
                chunk_text=text,
                character_count=len(text),
                token_count=token_count,
                chapter_id=temp["chapter_id"],
                section_id=temp["section_id"],
                previous_chunk_id=prev_id,
                next_chunk_id=next_id,
                source_page_start=temp["page_number"],
                source_page_end=temp["page_number"],
            )
            chunks.append(chunk)

        # Validate double-link references
        self._validate_doubly_linked_list(chunks)

        logger.info("Chunk sequence completed")

        # 4. Gather statistics and metadata
        total_characters = sum(c.character_count for c in chunks)
        total_tokens = sum(c.token_count for c in chunks)
        stats = {
            "total_chunks": total_chunks,
            "total_characters": total_characters,
            "total_tokens": total_tokens,
            "average_chunk_characters": (
                total_characters / total_chunks if total_chunks > 0 else 0
            ),
            "average_chunk_tokens": total_tokens / total_chunks if total_chunks > 0 else 0,
        }

        meta: dict[str, str | int | float | None] = {
            "chunking_strategy": "recursive_semantic",
            "max_chunk_size": self.max_chunk_size,
            "overlap_size": self.overlap_size,
        }

        return ChunkCollection(
            book_id=book_id,
            chunks=chunks,
            statistics=stats,
            metadata=meta,
        )

    def _find_chapter_and_section_for_page(
        self, page_number: int, chapters: list[Chapter], sections: list[Section]
    ) -> tuple[ChapterId, SectionId]:
        chapter_id = None
        for ch in chapters:
            if ch.start_page <= page_number <= ch.end_page:
                chapter_id = ch.id
                break

        section_id = None
        for sec in sections:
            if sec.start_page <= page_number <= sec.end_page:
                section_id = sec.id
                break

        if chapter_id is None or section_id is None:
            logger.error(f"Page {page_number} outside chapter/section boundaries.")
            raise ValidationException(
                f"Page {page_number} does not belong to any chapter or section."
            )

        return chapter_id, section_id

    def _split_text(self, text: str, max_size: int, overlap: int) -> list[str]:
        if len(text) <= max_size:
            return [text]

        # Try splitting by paragraph
        paragraphs = [p.strip() for p in text.split("\n\n")]
        paragraphs = [p for p in paragraphs if p]
        if len(paragraphs) > 1:
            processed = []
            for p in paragraphs:
                if len(p) > max_size:
                    processed.extend(self._split_lines(p, max_size, overlap))
                else:
                    processed.append(p)
            return self._merge_splits(processed, "\n\n", max_size, overlap)
        else:
            return self._split_lines(text, max_size, overlap)

    def _split_lines(self, text: str, max_size: int, overlap: int) -> list[str]:
        lines = [line.strip() for line in text.split("\n")]
        lines = [line for line in lines if line]
        if len(lines) > 1:
            processed = []
            for line in lines:
                if len(line) > max_size:
                    processed.extend(self._split_sentences(line, max_size, overlap))
                else:
                    processed.append(line)
            return self._merge_splits(processed, "\n", max_size, overlap)
        else:
            return self._split_sentences(text, max_size, overlap)

    def _split_sentences(self, text: str, max_size: int, overlap: int) -> list[str]:
        sentences = re.split(r"(?<=[.!?])\s+", text)
        sentences = [s.strip() for s in sentences if s.strip()]
        if len(sentences) > 1:
            processed = []
            for s in sentences:
                if len(s) > max_size:
                    processed.extend(self._split_words(s, max_size, overlap))
                else:
                    processed.append(s)
            return self._merge_splits(processed, " ", max_size, overlap)
        else:
            return self._split_words(text, max_size, overlap)

    def _split_words(self, text: str, max_size: int, overlap: int) -> list[str]:
        words = [w for w in text.split(" ") if w]
        if len(words) > 1:
            processed = []
            for w in words:
                if len(w) > max_size:
                    processed.extend(self._split_chars(w, max_size, overlap))
                else:
                    processed.append(w)
            return self._merge_splits(processed, " ", max_size, overlap)
        else:
            return self._split_chars(text, max_size, overlap)

    def _split_chars(self, text: str, max_size: int, overlap: int) -> list[str]:
        chunks = []
        start = 0
        text_len = len(text)
        while start < text_len:
            end = start + max_size
            chunk = text[start:end]
            chunks.append(chunk)
            start = end - overlap
            if start >= text_len or end >= text_len:
                break
        return chunks

    def _merge_splits(
        self, splits: list[str], separator: str, max_size: int, overlap: int
    ) -> list[str]:
        chunks = []
        current_doc: list[str] = []
        current_len = 0

        for s in splits:
            s_len = len(s)
            # If adding this split exceeds max_size
            if current_len + (len(separator) if current_doc else 0) + s_len > max_size:
                if current_doc:
                    chunks.append(separator.join(current_doc))
                # Backtrack to build the overlap prefix
                overlap_doc: list[str] = []
                overlap_len = 0
                for old_s in reversed(current_doc):
                    if overlap_len + (len(separator) if overlap_doc else 0) + len(old_s) <= overlap:
                        overlap_doc.insert(0, old_s)
                        overlap_len += (len(separator) if len(overlap_doc) > 1 else 0) + len(old_s)
                    else:
                        break
                current_doc = overlap_doc
                current_len = overlap_len

            current_doc.append(s)
            current_len += (len(separator) if len(current_doc) > 1 else 0) + s_len

        if current_doc:
            chunks.append(separator.join(current_doc))

        return chunks

    def _validate_doubly_linked_list(self, chunks: list[Chunk]) -> None:
        total = len(chunks)
        if total == 0:
            return

        if chunks[0].previous_chunk_id is not None:
            logger.error("Chunk validation failed: First chunk has a previous_chunk_id.")
            raise ValidationException("First chunk has a previous_chunk_id.")

        if chunks[-1].next_chunk_id is not None:
            logger.error("Chunk validation failed: Last chunk has a next_chunk_id.")
            raise ValidationException("Last chunk has a next_chunk_id.")

        for i in range(total):
            if i > 0:
                if chunks[i].previous_chunk_id != chunks[i - 1].id:
                    logger.error(f"Chunk validation failed: Orphan chunk link at index {i}.")
                    raise ValidationException(f"Orphan chunk link at index {i}.")
            if i < total - 1:
                if chunks[i].next_chunk_id != chunks[i + 1].id:
                    logger.error(f"Chunk validation failed: Orphan chunk link at index {i}.")
                    raise ValidationException(f"Orphan chunk link at index {i}.")
