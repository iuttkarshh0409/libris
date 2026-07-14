from typing import Any

from src.domain.value_objects.identifiers import BookId, ResponseId
from src.shared.domain.base import ValueObject


class IngestDocumentRequest(ValueObject):
    """Data transfer object for document ingestion requests."""

    def __init__(
        self,
        file_path: str,
        title: str | None = None,
        author: str | None = None,
        edition: str | None = None,
        subject: str | None = None,
    ) -> None:
        self.file_path = file_path
        self.title = title
        self.author = author
        self.edition = edition
        self.subject = subject


class IngestDocumentResponse(ValueObject):
    """Data transfer object for document ingestion responses."""

    def __init__(self, book_id: BookId, total_pages: int, total_chunks: int) -> None:
        self.book_id = book_id
        self.total_pages = total_pages
        self.total_chunks = total_chunks


class QueryRequest(ValueObject):
    """Data transfer object for academic query requests."""

    def __init__(
        self,
        query_text: str,
        similarity_threshold: float | None = None,
        limit: int | None = None,
        book_id: str | None = None,
    ) -> None:
        self.query_text = query_text
        self.similarity_threshold = similarity_threshold
        self.limit = limit
        self.book_id = book_id


class CitationDto(ValueObject):
    """Data transfer object representing a citation reference in a response."""

    def __init__(
        self,
        citation_id: str,
        book_title: str,
        page_number: int,
        chapter: str | None = None,
        section: str | None = None,
    ) -> None:
        self.citation_id = citation_id
        self.book_title = book_title
        self.page_number = page_number
        self.chapter = chapter
        self.section = section


class QueryResponse(ValueObject):
    """Data transfer object for query answers with citations."""

    def __init__(
        self,
        response_id: ResponseId,
        generated_answer: str,
        citations: list[CitationDto],
        verified_response: Any = None,
    ) -> None:
        self.response_id = response_id
        self.generated_answer = generated_answer
        self.citations = citations
        self.verified_response = verified_response
