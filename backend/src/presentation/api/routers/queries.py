from typing import Any

from fastapi import APIRouter, Depends
from loguru import logger

from src.application.contracts.dto import QueryRequest as DtoQueryRequest
from src.application.services.query_application_service import QueryApplicationService
from src.presentation.api.dependencies.core import get_query_service
from src.presentation.api.schemas.common import StandardApiResponse, wrap_success
from src.presentation.api.schemas.queries import (
    CitationSchema,
    QueryRequestSchema,
    VerifiedResponseItemSchema,
    VerifiedResponseSchema,
)

router = APIRouter(prefix="/queries", tags=["queries"])


@router.post("", response_model=StandardApiResponse[VerifiedResponseSchema])
async def submit_query(
    request: QueryRequestSchema,
    query_service: QueryApplicationService = Depends(get_query_service),
) -> dict[str, Any]:
    logger.info("Incoming request: POST /queries")
    logger.info("Request validated")

    dto_req = DtoQueryRequest(
        query_text=request.query_text,
        similarity_threshold=request.similarity_threshold,
        limit=request.limit,
        book_id=request.book_id,
    )

    logger.info("Application Service invoked: execute_query")
    res = query_service.execute_query(dto_req)
    if not res.is_success:
        logger.error(f"Query execution failed: {res.error}")
        raise res.error

    # Map VerifiedResponse aggregate to response schema
    verified = res.value.verified_response
    citation_schemas = [
        CitationSchema(
            citation_id=cit.id.value,
            book_title=cit.book_title,
            page_number=cit.page_number,
            chapter=cit.chapter,
            section=cit.section,
            embedding_id=cit.embedding_id.value if cit.embedding_id else None,
            retrieval_rank=cit.retrieval_rank,
            similarity_score=cit.similarity_score,
        )
        for cit in verified.supporting_citations
    ]
    item_schema = VerifiedResponseItemSchema(
        response_id=verified.id.value,
        query_id=verified.query_id.value,
        answer_text=verified.generated_answer,
        supporting_citations=citation_schemas,
        supporting_excerpts=verified.supporting_excerpts,
        verification_timestamp=verified.generation_timestamp.isoformat(),
    )
    verified_schema = VerifiedResponseSchema(
        book_id=verified.book_id.value,
        items=[item_schema],
        statistics=verified.statistics,
        metadata=verified.metadata,
    )

    logger.info("Successful response: POST /queries")
    return wrap_success(verified_schema)
