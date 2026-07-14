import re
import time
from datetime import datetime

from loguru import logger

from src.domain.engines.citation import CitationEngine
from src.domain.entities.citation import Citation
from src.domain.entities.context import RetrievalContext
from src.domain.entities.response import GeneratedResponse, VerifiedResponse, VerifiedResponseItem
from src.domain.value_objects.identifiers import CitationId
from src.shared.exceptions import ValidationException


class DefaultCitationEngine(CitationEngine):
    """Concrete implementation of CitationEngine.

    Reconciles retrieved chunks and generated response to build a VerifiedResponse
    with verified references and excerpts.
    """

    def extract_supporting_citations(
        self, response: GeneratedResponse, context: RetrievalContext
    ) -> list[Citation]:
        """Extracts and verifies citation references from a response and context."""
        if response is None:
            raise ValidationException("GeneratedResponse cannot be None.")
        if context is None:
            raise ValidationException("RetrievalContext cannot be None.")

        # Ensure answer text is present
        answer_text = response.generated_answer

        chunk_id_map = {chunk.chunk_id.value: chunk for chunk in context.items}
        explicit_cited_chunks = []

        # 1. Check for explicit chunk ID occurrences in answer_text
        for chunk_id_str, chunk in chunk_id_map.items():
            if chunk_id_str in answer_text:
                if chunk not in explicit_cited_chunks:
                    explicit_cited_chunks.append(chunk)

        # 2. Check for bracketed citation rank references: e.g. [1], [2]
        bracket_pattern = re.compile(r"\[(\d+)\]")
        matches = bracket_pattern.findall(answer_text)
        for match in matches:
            rank = int(match)
            matched_chunk = None
            for chunk in context.items:
                if chunk.retrieval_rank == rank:
                    matched_chunk = chunk
                    break
            if matched_chunk:
                if matched_chunk not in explicit_cited_chunks:
                    explicit_cited_chunks.append(matched_chunk)
            else:
                # Bracketed number matches nothing in context => orphan citation rank
                raise ValidationException(
                    f"Orphan citation rank reference [{rank}] found in response text."
                )

        # 3. Check for general orphan chunk ID references in text (e.g. chunk-999)
        chunk_ref_pattern = re.compile(r"chunk-([a-zA-Z0-9_-]+)")
        chunk_refs = chunk_ref_pattern.findall(answer_text)
        for ref in chunk_refs:
            full_ref = f"chunk-{ref}"
            if full_ref not in chunk_id_map:
                raise ValidationException(
                    f"Orphan citation chunk reference '{full_ref}' found in response text."
                )

        # Determine supporting chunks (preserve context ranking order)
        if explicit_cited_chunks:
            supporting_chunks = [c for c in context.items if c in explicit_cited_chunks]
        else:
            # Fallback: cite all retrieved context chunks if no explicit marks are found
            supporting_chunks = list(context.items)

        citations = []
        for chunk in supporting_chunks:
            citation = Citation(
                id=CitationId(f"cit-{chunk.chunk_id.value}"),
                book_title=context.metadata.get("book_title", "Unknown Book"),
                page_number=chunk.page_number,
                chunk_reference=chunk.chunk_id,
                chapter=chunk.chapter_id.value if chunk.chapter_id else None,
                section=chunk.section_id.value if chunk.section_id else None,
                embedding_id=chunk.embedding_id,
                retrieval_rank=chunk.retrieval_rank,
                similarity_score=chunk.similarity_score,
            )
            citations.append(citation)

        return citations

    def verify_citations(
        self, response: GeneratedResponse, context: RetrievalContext
    ) -> VerifiedResponse:
        """Validates response content against source context to attach verified citations."""
        start_time = time.perf_counter()
        logger.info("Citation verification started")

        # 1. Base validations
        if response is None:
            logger.error("Citation verification failed: GeneratedResponse is None")
            raise ValidationException("GeneratedResponse cannot be None.")
        if context is None:
            logger.error("Citation verification failed: RetrievalContext is None")
            raise ValidationException("RetrievalContext cannot be None.")

        # 2. Book ID consistency check
        if context.book_id != response.book_id:
            logger.error("Citation verification failed: Inconsistent BookIds")
            raise ValidationException(
                f"Inconsistent book IDs: context has {context.book_id.value}, "
                f"response has {response.book_id.value}."
            )

        # 3. RetrievedChunks data integrity checks
        seen_chunk_ids = set()
        for chunk in context.items:
            if not chunk.chunk_id or not chunk.chunk_id.value.strip():
                raise ValidationException("RetrievedChunk must have a valid chunk_id.")
            if chunk.chunk_id.value in seen_chunk_ids:
                raise ValidationException(
                    f"Duplicate chunk found in context: {chunk.chunk_id.value}"
                )
            seen_chunk_ids.add(chunk.chunk_id.value)

            if chunk.page_number is None or chunk.page_number <= 0:
                raise ValidationException(
                    f"Chunk {chunk.chunk_id.value} is missing a valid page number."
                )
            if not chunk.chunk_text or chunk.chunk_text.strip() == "":
                raise ValidationException(f"Chunk {chunk.chunk_id.value} is missing chunk text.")

        # 4. Extract citations
        citations = self.extract_supporting_citations(response, context)
        logger.info("Evidence validated")
        logger.info("Citations assembled")

        # Map supporting excerpts directly from chunk texts
        supporting_chunks = []
        chunk_map = {chunk.chunk_id.value: chunk for chunk in context.items}
        for cit in citations:
            matched_chunk = chunk_map.get(cit.chunk_reference.value)
            if matched_chunk:
                supporting_chunks.append(matched_chunk)

        supporting_excerpts = [c.chunk_text for c in supporting_chunks]
        logger.info("Supporting excerpts attached")

        # 5. Build VerifiedResponseItem
        verification_timestamp = datetime.now()
        original_item = response.items[0] if response.items else None
        if not original_item:
            logger.error("Citation verification failed: No ResponseItem in response")
            raise ValidationException("GeneratedResponse must contain at least one item.")

        verified_item = VerifiedResponseItem(
            response_id=original_item.response_id,
            query_id=original_item.query_id,
            answer_text=original_item.answer_text,
            supporting_citations=citations,
            supporting_excerpts=supporting_excerpts,
            verification_timestamp=verification_timestamp,
        )

        # 6. Compile statistics
        duration = time.perf_counter() - start_time
        unique_pages = len({cit.page_number for cit in citations})
        unique_chapters = len({cit.chapter for cit in citations if cit.chapter})

        avg_similarity = 0.0
        if supporting_chunks:
            avg_similarity = sum(chunk.similarity_score for chunk in supporting_chunks) / len(
                supporting_chunks
            )

        stats = {
            "total_citations": len(citations),
            "unique_pages": unique_pages,
            "unique_chapters": unique_chapters,
            "average_similarity": avg_similarity,
            "verification_duration": duration,
        }

        # 7. Compile metadata
        retrieval_strat = context.metadata.get("retrieval_strategy", "semantic_similarity")
        compilation_strat = response.metadata.get("compilation_strategy", "rank_ordered_inclusion")
        meta = {
            "citation_version": "1.0.0",
            "verification_strategy": "reconciled_matching",
            "retrieval_strategy": retrieval_strat,
            "compilation_strategy": compilation_strat,
            "generation_source": response.metadata.get("generation_source", "Gemini"),
        }

        logger.info("VerifiedResponse assembled")
        logger.info("Citation verification completed")

        return VerifiedResponse(
            book_id=response.book_id,
            items=[verified_item],
            statistics=stats,
            metadata=meta,
        )
