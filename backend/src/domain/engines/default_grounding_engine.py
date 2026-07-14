import time

from loguru import logger

from src.domain.engines.grounding import GroundingEngine
from src.domain.entities.context import RetrievalContext, RetrievedChunk
from src.domain.entities.prompt import (
    ConstraintSection,
    EvidenceSection,
    Prompt,
    QuestionSection,
    SystemInstructionSection,
    TaskDefinitionSection,
)
from src.domain.entities.query import Query
from src.shared.exceptions import ValidationException


class DefaultGroundingEngine(GroundingEngine):
    """Concrete implementation of GroundingEngine.

    Transforms retrieved context evidence and user query into a structured,
    deterministic Prompt aggregate according to the Prompting Contract.
    """

    SYSTEM_INSTRUCTIONS_DEFAULT = (
        "You are an academic assistant. Your task is to answer user queries using only the "
        "retrieved textbook evidence. You must adhere to the following rules:\n"
        "1. Answer queries strictly using the provided Retrieved Evidence. Do not assume or "
        "extrapolate beyond what is explicitly written in the evidence.\n"
        "2. If the Retrieved Evidence is insufficient or missing, you must respond with exactly: "
        '"The indexed textbooks do not contain sufficient information to answer this question."\n'
        "3. Never introduce prior knowledge, external assumptions, or internet facts.\n"
        "4. Maintain a neutral, academic, and professional tone."
    )

    TASK_DEFINITION_DEFAULT = (
        "Provide a detailed explanation answering the user's question. "
        "Format your response to include: a direct Answer, followed by Key Points, "
        "a Supporting Explanation, and appropriate Citations matching the evidence."
    )

    CONSTRAINTS_DEFAULT = (
        "Constraints:\n"
        "- You must answer ONLY using the supplied evidence.\n"
        "- Never fabricate information, page numbers, or citations.\n"
        "- If evidence is insufficient, state: "
        '"The indexed textbooks do not contain sufficient information to answer this question."\n'
        "- Every factual statement must cite its source (Book, Page, Chapter, Section)."
    )

    def __init__(
        self,
        max_prompt_chars: int = 100000,
        prompt_version: str = "1.0.0",
        prompting_contract_version: str = "1.0.0",
        system_instructions: str = SYSTEM_INSTRUCTIONS_DEFAULT,
        task_definition: str = TASK_DEFINITION_DEFAULT,
        constraints: str = CONSTRAINTS_DEFAULT,
    ) -> None:
        """Initializes the grounding engine with customizable bounds and instructions."""
        self.max_prompt_chars = max_prompt_chars
        self.prompt_version = prompt_version
        self.prompting_contract_version = prompting_contract_version
        self.system_instructions = system_instructions
        self.task_definition = task_definition
        self.constraints = constraints

    def _format_chunk(self, chunk: RetrievedChunk, book_id_val: str) -> str:
        """Formats a single RetrievedChunk into a standard evidence representation."""
        chapter_info = f", Chapter: {chunk.chapter_id.value}" if chunk.chapter_id else ""
        section_info = f", Section: {chunk.section_id.value}" if chunk.section_id else ""
        return (
            f"[Rank: {chunk.retrieval_rank}] (Book: {book_id_val}, Page: {chunk.page_number}"
            f"{chapter_info}{section_info})\n"
            f"Text: {chunk.chunk_text}"
        )

    def compile_prompt(self, query: Query, context: RetrievalContext) -> Prompt:
        """Assembles a contract-compliant Prompt from query and retrieved context."""
        start_time = time.perf_counter()
        logger.info("Grounding started")

        # 1. Validate Input Entities
        if query is None:
            logger.error("Grounding failed: Query is None")
            raise ValidationException("Query cannot be None.")

        if (
            not hasattr(query, "original_question")
            or not query.original_question
            or query.original_question.strip() == ""
        ):
            logger.error("Grounding failed: Query text is empty or blank")
            raise ValidationException("Query text cannot be empty or blank.")

        if context is None:
            logger.error("Grounding failed: RetrievalContext is None")
            raise ValidationException("RetrievalContext cannot be None.")

        if not context.items:
            logger.error("Grounding failed: RetrievalContext items are empty")
            raise ValidationException("RetrievalContext has no retrieved chunks.")

        # 2. Validate Retrieved Chunks
        seen_chunk_ids = set()
        actual_ranks = []
        for chunk in context.items:
            # Missing chunk text validation
            if not chunk.chunk_text or chunk.chunk_text.strip() == "":
                logger.error(f"Grounding failed: Missing chunk text for {chunk.chunk_id.value}")
                raise ValidationException(
                    f"Missing chunk text in RetrievedChunk '{chunk.chunk_id.value}'."
                )

            # Duplicate chunk validation
            if chunk.chunk_id.value in seen_chunk_ids:
                logger.error(f"Grounding failed: Duplicate ChunkId: {chunk.chunk_id.value}")
                raise ValidationException(
                    f"Duplicate ChunkId '{chunk.chunk_id.value}' in RetrievalContext."
                )
            seen_chunk_ids.add(chunk.chunk_id.value)
            actual_ranks.append(chunk.retrieval_rank)

        # Validate retrieval rank sequence (must be 1, 2, 3, ...)
        expected_ranks = list(range(1, len(context.items) + 1))
        if actual_ranks != expected_ranks:
            logger.error("Grounding failed: Invalid retrieval rank order")
            raise ValidationException("Invalid retrieval rank order in context items.")

        logger.info("Evidence validated")

        # 3. Core Prompt Compilation & Truncation logic
        # Build base sections first to check baseline character budget
        sys_sec = SystemInstructionSection(self.system_instructions)
        task_sec = TaskDefinitionSection(self.task_definition)
        quest_sec = QuestionSection(f"Question: {query.original_question}")
        const_sec = ConstraintSection(self.constraints)

        base_parts = [
            f"=== {sys_sec.title} ===\n{sys_sec.content}",
            f"=== {task_sec.title} ===\n{task_sec.content}",
            f"=== {quest_sec.title} ===\n{quest_sec.content}",
            f"=== {const_sec.title} ===\n{const_sec.content}",
        ]
        base_char_count = sum(len(part) for part in base_parts) + (len(base_parts) - 1) * 2

        # Check if the base prompt itself exceeds the limit
        if base_char_count > self.max_prompt_chars:
            logger.error("Grounding failed: Base prompt size exceeds max limit")
            msg = (
                f"Base prompt size ({base_char_count} chars) "
                f"exceeds limit of {self.max_prompt_chars}."
            )
            raise ValidationException(msg)

        # Progressively add chunks by rank until character limit is reached
        included_chunks = []
        evidence_strings: list[str] = []
        book_id_val = context.book_id.value

        for chunk in context.items:
            chunk_str = self._format_chunk(chunk, book_id_val)
            # Calculate what the total character length would be if this chunk is added
            temp_evidence_strings = [*evidence_strings, chunk_str]
            temp_evidence_content = "\n\n".join(temp_evidence_strings)
            temp_evidence_section = f"=== Retrieved Evidence ===\n{temp_evidence_content}"

            total_temp_chars = base_char_count + 2 + len(temp_evidence_section)

            if total_temp_chars <= self.max_prompt_chars:
                included_chunks.append(chunk)
                evidence_strings.append(chunk_str)
            else:
                # Truncation point reached: stop adding lower-rank chunks
                logger.warning(
                    f"Prompt truncation triggered: excluded chunk {chunk.chunk_id.value} "
                    f"(rank {chunk.retrieval_rank}) to stay within character limit."
                )
                break

        # Check if we could fit at least one chunk
        if not included_chunks:
            logger.error("Grounding failed: Prompt is too small to include even the top rank chunk")
            raise ValidationException(
                f"Cannot fit even the top-ranked chunk within the {self.max_prompt_chars} limit."
            )

        # Assemble final sections
        evidence_content = "\n\n".join(evidence_strings)
        evidence_sec = EvidenceSection(evidence_content)

        sections = [sys_sec, task_sec, evidence_sec, quest_sec, const_sec]
        logger.info("Prompt sections assembled")

        # 4. Generate statistics & metadata
        duration = time.perf_counter() - start_time

        # Calculate final prompt characters
        final_prompt_parts = []
        for sec in sorted(sections, key=lambda x: x.order):
            final_prompt_parts.append(f"=== {sec.title} ===\n{sec.content}")
        total_p_chars = sum(len(p) for p in final_prompt_parts)
        separator_chars = (len(final_prompt_parts) - 1) * 2
        final_char_count = total_p_chars + separator_chars

        stats = {
            "total_sections": len(sections),
            "evidence_chunks": len(included_chunks),
            "total_prompt_characters": final_char_count,
            "total_prompt_tokens_estimate": final_char_count // 4,
            "compilation_duration": duration,
        }

        meta = {
            "query_id": query.id.value,
            "prompt_version": self.prompt_version,
            "prompting_contract_version": self.prompting_contract_version,
            "retrieval_strategy": context.metadata.get("retrieval_strategy", "semantic_similarity"),
            "compilation_strategy": "rank_ordered_inclusion",
        }

        logger.info("Prompt compiled")
        logger.info("Grounding completed")

        return Prompt(
            book_id=context.book_id,
            items=sections,
            statistics=stats,
            metadata=meta,
        )
