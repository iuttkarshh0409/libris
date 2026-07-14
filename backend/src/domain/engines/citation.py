from typing import Protocol

from src.domain.entities.citation import Citation
from src.domain.entities.context import RetrievalContext
from src.domain.entities.response import GeneratedResponse, VerifiedResponse


class CitationEngine(Protocol):
    """Protocol defining citation verification and reference formatting responsibilities."""

    def verify_citations(
        self, response: GeneratedResponse, context: RetrievalContext
    ) -> VerifiedResponse:
        """Validates response content against source context to attach verified citations."""
        ...

    def extract_supporting_citations(
        self, response: GeneratedResponse, context: RetrievalContext
    ) -> list[Citation]:
        """Extracts and verifies citation references from a response and context."""
        ...
