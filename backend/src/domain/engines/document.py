from typing import Protocol

from src.domain.entities.parsed_document import ParsedDocument


class DocumentEngine(Protocol):
    """Protocol defining textbook structural validation and parsing responsibilities."""

    def parse_pdf(self, file_path: str) -> ParsedDocument:
        """Parses a textbook PDF file into a structured ParsedDocument."""
        ...
