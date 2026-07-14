from dataclasses import dataclass
from typing import BinaryIO, Protocol

from src.shared.contracts.result import Result


@dataclass(frozen=True)
class ExtractedPage:
    """Represents raw extracted text and number of a page, before domain model transformation."""

    page_number: int
    text: str


@dataclass(frozen=True)
class ExtractedDocument:
    """Represents raw parsed document metadata and pages, before domain model transformation."""

    metadata: dict[str, str | None]
    page_count: int
    pages: list[ExtractedPage]


class DocumentProvider(Protocol):
    """Abstraction interface for raw PDF file validation and document extraction."""

    def validate_pdf(self, file_source: str | BinaryIO) -> Result[None]:
        """Validates the PDF structure and characteristics (encryption, corruption)."""
        ...

    def extract_document(self, file_source: str | BinaryIO) -> Result[ExtractedDocument]:
        """Extracts standard metadata, page count, and page texts into a unified structure."""
        ...
