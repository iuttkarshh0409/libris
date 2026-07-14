import uuid
from datetime import datetime

from loguru import logger

from src.application.contracts.dto import CitationDto, QueryRequest, QueryResponse
from src.domain.engines.citation import CitationEngine
from src.domain.engines.generation import GenerationEngine
from src.domain.engines.grounding import GroundingEngine
from src.domain.engines.retrieval import RetrievalEngine
from src.domain.entities.query import Query
from src.domain.repositories.book import BookRepository
from src.domain.value_objects.identifiers import BookId, QueryId
from src.shared.contracts.result import Failure, Result, Success
from src.shared.exceptions import DomainException, ValidationException


class QueryApplicationService:
    """Orchestrates the retrieval and generation query pipeline workflow.

    Coordinates retrieval context extraction, grounding validation, response generation,
    and citation formatting.
    """

    def __init__(
        self,
        retrieval_engine: RetrievalEngine,
        grounding_engine: GroundingEngine,
        generation_engine: GenerationEngine,
        citation_engine: CitationEngine,
        book_repository: BookRepository,
    ) -> None:
        self._retrieval_engine = retrieval_engine
        self._grounding_engine = grounding_engine
        self._generation_engine = generation_engine
        self._citation_engine = citation_engine
        self._book_repository = book_repository

    def execute_query(self, request: QueryRequest) -> Result[QueryResponse]:
        """Executes RAG query pipeline."""
        logger.info("Workflow Started")

        try:
            # 1. Validate workflow inputs
            if not request.query_text or not request.query_text.strip():
                raise ValidationException("Query text cannot be empty.")
            logger.info("Request Validated")

            # 2. Initialize query model
            query_id = QueryId(str(uuid.uuid4()))
            query = Query(
                id=query_id,
                original_question=request.query_text,
                query_timestamp=datetime.now(),
            )

            # Set retrieval engine book ID to user requested book, or fallback to the latest
            if hasattr(request, "book_id") and request.book_id:
                self._retrieval_engine.book_id = BookId(request.book_id)
                logger.info(f"Scoping query to book: {request.book_id}")
            else:
                try:
                    books = self._book_repository.list_all()
                    if books:
                        latest_book = sorted(books, key=lambda b: b.upload_timestamp, reverse=True)[
                            0
                        ]
                        if hasattr(self._retrieval_engine, "book_id"):
                            self._retrieval_engine.book_id = latest_book.id
                            logger.info(
                                f"Auto-selected latest book: {latest_book.title} "
                                f"(ID: {latest_book.id.value})"
                            )
                except Exception as e:
                    logger.warning(f"Failed to auto-select latest book for retrieval: {e}")

            # 3. Retrieve context directly by passing query entity
            logger.info("Retrieval Engine Invoked")
            retrieval_context = self._retrieval_engine.retrieve_context(
                query,
                similarity_threshold=request.similarity_threshold,
                limit=request.limit,
            )

            # Resolve book title for downstream citation attribution
            try:
                book = self._book_repository.get_by_id(retrieval_context.book_id)
                if book and book.title:
                    retrieval_context.metadata["book_title"] = book.title
            except Exception as e:
                logger.warning(f"Failed to lookup book title for citation: {e}")

            # 4. Ground response via prompt compilation
            logger.info("Grounding Engine Invoked")
            prompt = self._grounding_engine.compile_prompt(query, retrieval_context)

            # 5. Execute text generation from prompt
            logger.info("Generation Engine Invoked")
            response = self._generation_engine.generate_response(prompt)

            # 6. Formulate verified citation references
            logger.info("Citation Engine Invoked")
            verified_response = self._citation_engine.verify_citations(response, retrieval_context)

            # 7. Map to returnable DTO
            logger.info("Workflow Completed")
            citations = [
                CitationDto(
                    citation_id=c.id.value,
                    book_title=c.book_title,
                    page_number=c.page_number,
                    chapter=c.chapter,
                    section=c.section,
                )
                for c in verified_response.supporting_citations
            ]
            query_response = QueryResponse(
                response_id=verified_response.id,
                generated_answer=verified_response.generated_answer,
                citations=citations,
                verified_response=verified_response,
            )
            return Success(query_response)

        except DomainException as e:
            logger.error(f"Domain failure during query workflow: {e!s}")
            return Failure(e)
        except Exception as e:
            logger.error(f"Unexpected failure during query workflow: {e!s}")
            return Failure(DomainException(f"Query execution failed: {e!s}"))
