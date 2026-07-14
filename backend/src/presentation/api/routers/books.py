import os
import uuid
from typing import Any

from fastapi import APIRouter, Depends, File, UploadFile
from loguru import logger

from src.application.contracts.dto import IngestDocumentRequest
from src.application.services.ingestion_application_service import IngestionApplicationService
from src.domain.value_objects.identifiers import BookId
from src.presentation.api.dependencies.core import get_ingestion_service
from src.presentation.api.schemas.books import BookSummaryResponse
from src.presentation.api.schemas.common import StandardApiResponse, wrap_success
from src.shared.exceptions import DomainException, ValidationException

router = APIRouter(prefix="/books", tags=["books"])


@router.post("", response_model=StandardApiResponse[BookSummaryResponse], status_code=201)
async def upload_book(
    file: UploadFile = File(...),
    ingestion_service: IngestionApplicationService = Depends(get_ingestion_service),
) -> dict[str, Any]:
    logger.info("Incoming request: POST /books")
    if not file.filename or not file.filename.endswith(".pdf"):
        logger.warning("Request validation failed: Only PDF files are supported.")
        raise ValidationException("Only PDF files are supported.")

    temp_dir = os.path.join(os.getcwd(), "temp_uploads")
    os.makedirs(temp_dir, exist_ok=True)
    temp_file_path = os.path.join(temp_dir, f"{uuid.uuid4()}_{file.filename}")

    try:
        with open(temp_file_path, "wb") as f:
            content = await file.read()
            if len(content) == 0:
                logger.warning("Request validation failed: Uploaded file is empty.")
                raise ValidationException("Uploaded file is empty.")
            f.write(content)

        logger.info("Request validated")
        req = IngestDocumentRequest(file_path=temp_file_path)
        logger.info("Application Service invoked: ingest_document")
        res = ingestion_service.ingest_document(req)
        if not res.is_success:
            logger.error(f"Ingestion failed: {res.error}")
            raise res.error

        book_res = ingestion_service.get_book(res.value.book_id)
        if not book_res.is_success or not book_res._value:
            logger.error("Failed to retrieve ingested book details.")
            raise DomainException("Failed to retrieve ingested book details.")

        book = book_res._value
        summary = BookSummaryResponse(
            id=book.id.value,
            title=book.title,
            author=book.author,
            subject=book.subject,
            edition=book.edition,
            pages=book.total_pages,
            index_status=book.index_status,
            file_name=book.file_name,
            upload_timestamp=book.upload_timestamp.isoformat(),
        )
        logger.info("Successful response: POST /books")
        return wrap_success(summary)
    finally:
        if os.path.exists(temp_file_path):
            try:
                os.remove(temp_file_path)
            except Exception as e:
                logger.warning(f"Failed to remove temp file {temp_file_path}: {e}")


@router.get("", response_model=StandardApiResponse[list[BookSummaryResponse]])
async def list_books(
    ingestion_service: IngestionApplicationService = Depends(get_ingestion_service),
) -> dict[str, Any]:
    logger.info("Incoming request: GET /books")
    res = ingestion_service.list_books()
    if not res.is_success:
        logger.error(f"List books failed: {res.error}")
        raise res.error

    summaries = [
        BookSummaryResponse(
            id=b.id.value,
            title=b.title,
            author=b.author,
            subject=b.subject,
            edition=b.edition,
            pages=b.total_pages,
            index_status=b.index_status,
            file_name=b.file_name,
            upload_timestamp=b.upload_timestamp.isoformat(),
        )
        for b in res.value
    ]
    logger.info("Successful response: GET /books")
    return wrap_success(summaries)


@router.get("/{book_id}", response_model=StandardApiResponse[BookSummaryResponse])
async def get_book(
    book_id: str,
    ingestion_service: IngestionApplicationService = Depends(get_ingestion_service),
) -> dict[str, Any]:
    logger.info(f"Incoming request: GET /books/{book_id}")
    res = ingestion_service.get_book(BookId(book_id))
    if not res.is_success:
        logger.error(f"Get book failed: {res.error}")
        raise res.error
    if not res._value:
        logger.warning(f"Book with ID {book_id} not found.")
        raise ValidationException(f"Book with ID {book_id} not found.")

    b = res._value
    summary = BookSummaryResponse(
        id=b.id.value,
        title=b.title,
        author=b.author,
        subject=b.subject,
        edition=b.edition,
        pages=b.total_pages,
        index_status=b.index_status,
        file_name=b.file_name,
        upload_timestamp=b.upload_timestamp.isoformat(),
    )
    logger.info(f"Successful response: GET /books/{book_id}")
    return wrap_success(summary)


@router.delete("/{book_id}", response_model=StandardApiResponse[dict[str, str]])
async def delete_book(
    book_id: str,
    ingestion_service: IngestionApplicationService = Depends(get_ingestion_service),
) -> dict[str, Any]:
    logger.info(f"Incoming request: DELETE /books/{book_id}")
    res = ingestion_service.get_book(BookId(book_id))
    if not res.is_success:
        logger.error(f"Get book check failed: {res.error}")
        raise res.error
    if not res._value:
        logger.warning(f"Book with ID {book_id} not found.")
        raise ValidationException(f"Book with ID {book_id} not found.")

    del_res = ingestion_service.delete_book(BookId(book_id))

    if not del_res.is_success:
        logger.error(f"Delete book failed: {del_res.error}")
        raise del_res.error

    logger.info(f"Successful response: DELETE /books/{book_id}")
    return wrap_success({"message": f"Book {book_id} has been successfully deleted."})
