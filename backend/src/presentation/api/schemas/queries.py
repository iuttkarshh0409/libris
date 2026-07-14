from typing import Any

from pydantic import BaseModel, Field


class QueryRequestSchema(BaseModel):
    query_text: str = Field(..., min_length=1)
    similarity_threshold: float | None = None
    limit: int | None = None
    book_id: str | None = None


class CitationSchema(BaseModel):
    citation_id: str
    book_title: str
    page_number: int
    chapter: str | None = None
    section: str | None = None
    embedding_id: str | None = None
    retrieval_rank: int | None = None
    similarity_score: float | None = None


class VerifiedResponseItemSchema(BaseModel):
    response_id: str
    query_id: str
    answer_text: str
    supporting_citations: list[CitationSchema]
    supporting_excerpts: list[str]
    verification_timestamp: str


class VerifiedResponseSchema(BaseModel):
    book_id: str
    items: list[VerifiedResponseItemSchema]
    statistics: dict[str, Any]
    metadata: dict[str, Any]
