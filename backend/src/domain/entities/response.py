from datetime import datetime
from typing import Any

from src.domain.entities.citation import Citation
from src.domain.value_objects.identifiers import BookId, QueryId, ResponseId
from src.shared.domain.base import ValueObject


class ResponseItem(ValueObject):
    """Represents a single generated answer within the GeneratedResponse aggregate."""

    def __init__(
        self,
        response_id: ResponseId,
        query_id: QueryId,
        answer_text: str,
        generation_timestamp: datetime,
        model_identifier: str,
        finish_reason: str,
        token_usage: dict[str, int] | None = None,
    ) -> None:
        self._response_id = response_id
        self._query_id = query_id
        self._answer_text = answer_text
        self._generation_timestamp = generation_timestamp
        self._model_identifier = model_identifier
        self._finish_reason = finish_reason
        self._token_usage = token_usage or {}

    @property
    def response_id(self) -> ResponseId:
        return self._response_id

    @property
    def query_id(self) -> QueryId:
        return self._query_id

    @property
    def answer_text(self) -> str:
        return self._answer_text

    @property
    def generation_timestamp(self) -> datetime:
        return self._generation_timestamp

    @property
    def model_identifier(self) -> str:
        return self._model_identifier

    @property
    def finish_reason(self) -> str:
        return self._finish_reason

    @property
    def token_usage(self) -> dict[str, int]:
        return self._token_usage


class GeneratedResponse(ValueObject):
    """Structured, typed final response aggregate."""

    def __init__(
        self,
        book_id: BookId,
        items: list[ResponseItem],
        statistics: dict[str, Any],
        metadata: dict[str, Any],
        supporting_citations: list[Citation] | None = None,
        supporting_excerpts: list[str] | None = None,
    ) -> None:
        self._book_id = book_id
        self._items = items
        self._statistics = statistics
        self._metadata = metadata
        self._supporting_citations = supporting_citations or []
        self._supporting_excerpts = supporting_excerpts or []

    @property
    def book_id(self) -> BookId:
        return self._book_id

    @property
    def items(self) -> list[ResponseItem]:
        return self._items

    @property
    def statistics(self) -> dict[str, Any]:
        return self._statistics

    @property
    def metadata(self) -> dict[str, Any]:
        return self._metadata

    # --- Backward Compatibility Properties ---

    @property
    def id(self) -> ResponseId:
        return self._items[0].response_id if self._items else ResponseId("")

    @property
    def query_id(self) -> QueryId:
        return self._items[0].query_id if self._items else QueryId("")

    @property
    def generated_answer(self) -> str:
        return self._items[0].answer_text if self._items else ""

    @property
    def generation_timestamp(self) -> datetime:
        return self._items[0].generation_timestamp if self._items else datetime.now()

    @property
    def supporting_citations(self) -> list[Citation]:
        return self._supporting_citations

    @property
    def supporting_excerpts(self) -> list[str]:
        return self._supporting_excerpts


class VerifiedResponseItem(ValueObject):
    """Represents a single verified answer with its references."""

    def __init__(
        self,
        response_id: ResponseId,
        query_id: QueryId,
        answer_text: str,
        supporting_citations: list[Citation],
        supporting_excerpts: list[str],
        verification_timestamp: datetime,
    ) -> None:
        self._response_id = response_id
        self._query_id = query_id
        self._answer_text = answer_text
        self._supporting_citations = supporting_citations
        self._supporting_excerpts = supporting_excerpts
        self._verification_timestamp = verification_timestamp

    @property
    def response_id(self) -> ResponseId:
        return self._response_id

    @property
    def query_id(self) -> QueryId:
        return self._query_id

    @property
    def answer_text(self) -> str:
        return self._answer_text

    @property
    def supporting_citations(self) -> list[Citation]:
        return self._supporting_citations

    @property
    def supporting_excerpts(self) -> list[str]:
        return self._supporting_excerpts

    @property
    def verification_timestamp(self) -> datetime:
        return self._verification_timestamp


class VerifiedResponse(ValueObject):
    """Structured, typed final verified response aggregate."""

    def __init__(
        self,
        book_id: BookId,
        items: list[VerifiedResponseItem],
        statistics: dict[str, Any],
        metadata: dict[str, Any],
    ) -> None:
        self._book_id = book_id
        self._items = items
        self._statistics = statistics
        self._metadata = metadata

    @property
    def book_id(self) -> BookId:
        return self._book_id

    @property
    def items(self) -> list[VerifiedResponseItem]:
        return self._items

    @property
    def statistics(self) -> dict[str, Any]:
        return self._statistics

    @property
    def metadata(self) -> dict[str, Any]:
        return self._metadata

    # --- Backward Compatibility Properties ---

    @property
    def id(self) -> ResponseId:
        return self._items[0].response_id if self._items else ResponseId("")

    @property
    def query_id(self) -> QueryId:
        return self._items[0].query_id if self._items else QueryId("")

    @property
    def generated_answer(self) -> str:
        return self._items[0].answer_text if self._items else ""

    @property
    def generation_timestamp(self) -> datetime:
        return self._items[0].verification_timestamp if self._items else datetime.now()

    @property
    def supporting_citations(self) -> list[Citation]:
        return self._items[0].supporting_citations if self._items else []

    @property
    def supporting_excerpts(self) -> list[str]:
        return self._items[0].supporting_excerpts if self._items else []
