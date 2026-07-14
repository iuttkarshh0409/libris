from collections.abc import Iterator
from contextlib import contextmanager
from typing import BinaryIO

import pypdf
from loguru import logger

from src.domain.providers.document import DocumentProvider, ExtractedDocument, ExtractedPage
from src.shared.contracts.result import Failure, Result, Success
from src.shared.exceptions import ProviderException


class PyPDFProvider(DocumentProvider):
    """Concrete implementation of DocumentProvider using PyPDF.

    Performs validation and structured raw text extraction from PDF sources (paths or streams).
    """

    @contextmanager
    def _open_source(self, file_source: str | BinaryIO) -> Iterator[BinaryIO]:
        if isinstance(file_source, str):
            try:
                with open(file_source, "rb") as f:
                    yield f
            except FileNotFoundError as e:
                raise ProviderException(f"File not found: {file_source}") from e
            except Exception as e:
                raise ProviderException(f"Failed to open file {file_source}: {e!s}") from e
        else:
            yield file_source

    def validate_pdf(self, file_source: str | BinaryIO) -> Result[None]:
        """Validates the PDF structure and characteristics (encryption, corruption)."""
        logger.info("Validating PDF source")
        try:
            with self._open_source(file_source) as stream:
                stream.seek(0, 2)
                size = stream.tell()
                stream.seek(0)
                if size == 0:
                    logger.error("Empty document detected")
                    return Failure(ProviderException("Empty document detected."))

                reader = pypdf.PdfReader(stream)
                if reader.is_encrypted:
                    logger.error("Encrypted PDF detected")
                    return Failure(ProviderException("Encrypted PDF detected."))

                _ = len(reader.pages)
            logger.info("PDF validated successfully")
            return Success(None)
        except Exception as e:
            logger.error(f"Invalid or corrupted PDF format: {e!s}")
            return Failure(ProviderException(f"Invalid or corrupted PDF format: {e!s}"))

    def extract_document(self, file_source: str | BinaryIO) -> Result[ExtractedDocument]:
        """Extracts standard metadata, page count, and page texts into a unified structure."""
        logger.info("Extracting document from PDF source")
        try:
            with self._open_source(file_source) as stream:
                # 1. Validate stream first
                stream.seek(0, 2)
                size = stream.tell()
                stream.seek(0)
                if size == 0:
                    logger.error("Empty document detected")
                    return Failure(ProviderException("Empty document detected."))

                reader = pypdf.PdfReader(stream)
                if reader.is_encrypted:
                    logger.error("Encrypted PDF detected")
                    return Failure(ProviderException("Encrypted PDF detected."))

                # 2. Extract metadata
                meta = reader.metadata
                metadata = {
                    "title": meta.title if meta and meta.title else None,
                    "author": meta.author if meta and meta.author else None,
                    "subject": meta.subject if meta and meta.subject else None,
                    "creator": meta.creator if meta and meta.creator else None,
                    "producer": meta.producer if meta and meta.producer else None,
                    "creation_date": meta.get("/CreationDate") if meta else None,
                    "modification_date": meta.get("/ModDate") if meta else None,
                }

                # 3. Extract pages
                page_count = len(reader.pages)
                extracted_pages = []

                for idx in range(page_count):
                    page_number = idx + 1
                    page = reader.pages[idx]
                    text = page.extract_text()
                    if text is None:
                        text = ""
                    # Normalize line endings and trim unnecessary whitespace
                    normalized_text = text.replace("\r\n", "\n").replace("\r", "\n").strip()
                    extracted_pages.append(
                        ExtractedPage(page_number=page_number, text=normalized_text)
                    )

                logger.info(f"Extraction completed successfully. Pages extracted: {page_count}")
                doc = ExtractedDocument(
                    metadata=metadata,
                    page_count=page_count,
                    pages=extracted_pages,
                )
                return Success(doc)

        except Exception as e:
            logger.error(f"Extraction failed: {e!s}")
            return Failure(ProviderException(f"Extraction failed: {e!s}"))
