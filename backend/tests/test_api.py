import io
from collections.abc import Generator
from datetime import datetime
from unittest.mock import Mock

import pytest
from fastapi.testclient import TestClient

from src.application.contracts.dto import CitationDto, IngestDocumentResponse, QueryResponse
from src.application.services.ingestion_application_service import IngestionApplicationService
from src.application.services.query_application_service import QueryApplicationService
from src.domain.entities.book import Book
from src.domain.entities.citation import Citation
from src.domain.entities.response import VerifiedResponse, VerifiedResponseItem
from src.domain.value_objects.identifiers import (
    BookId,
    ChunkId,
    CitationId,
    EmbeddingId,
    QueryId,
    ResponseId,
)
from src.main import app
from src.presentation.api.dependencies.core import get_ingestion_service, get_query_service
from src.shared.contracts.result import Success
from src.shared.exceptions import (
    ProviderException,
    RetrievalException,
    ValidationException,
)

client = TestClient(app, raise_server_exceptions=False)


@pytest.fixture(autouse=True)
def clean_overrides() -> Generator[None]:
    app.dependency_overrides.clear()
    yield
    app.dependency_overrides.clear()


def test_read_root() -> None:
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the Libris API"}


def test_health_check() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_system_status() -> None:
    response = client.get("/api/v1/status")
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["success"] is True
    assert json_data["data"]["health_state"] == "healthy"
    assert "index_provider" in json_data["data"]["provider_status"]
    assert json_data["metadata"]["api_version"] == "1.0"
    assert json_data["metadata"]["architecture_version"] == "1.0"


def test_read_config() -> None:
    response = client.get("/api/v1/config")
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["success"] is True
    assert "chunk_size" in json_data["data"]
    assert "gemini_api_key" not in json_data["data"]


def test_list_books_success() -> None:
    mock_service = Mock(spec=IngestionApplicationService)
    book = Book(
        id=BookId("book-123"),
        title="Test Book",
        author="Test Author",
        edition="1st",
        subject="Testing",
        file_name="test.pdf",
        file_path="/path/test.pdf",
        upload_timestamp=datetime.utcnow(),
        total_pages=10,
        index_status="completed",
    )
    mock_service.list_books.return_value = Success([book])
    app.dependency_overrides[get_ingestion_service] = lambda: mock_service

    response = client.get("/api/v1/books")
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["success"] is True
    assert len(json_data["data"]) == 1
    assert json_data["data"][0]["id"] == "book-123"
    assert json_data["data"][0]["title"] == "Test Book"


def test_get_book_success() -> None:
    mock_service = Mock(spec=IngestionApplicationService)
    book = Book(
        id=BookId("book-123"),
        title="Test Book",
        author="Test Author",
        edition="1st",
        subject="Testing",
        file_name="test.pdf",
        file_path="/path/test.pdf",
        upload_timestamp=datetime.utcnow(),
        total_pages=10,
        index_status="completed",
    )
    mock_service.get_book.return_value = Success(book)
    app.dependency_overrides[get_ingestion_service] = lambda: mock_service

    response = client.get("/api/v1/books/book-123")
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["success"] is True
    assert json_data["data"]["id"] == "book-123"


def test_get_book_not_found() -> None:
    mock_service = Mock(spec=IngestionApplicationService)
    mock_service.get_book.return_value = Success(None)
    app.dependency_overrides[get_ingestion_service] = lambda: mock_service

    response = client.get("/api/v1/books/book-nonexistent")
    assert response.status_code == 400
    json_data = response.json()
    assert json_data["success"] is False
    assert "not found" in json_data["errors"][0]


def test_upload_book_success() -> None:
    mock_service = Mock(spec=IngestionApplicationService)
    mock_service.ingest_document.return_value = Success(
        IngestDocumentResponse(book_id=BookId("book-123"), total_pages=10, total_chunks=50)
    )
    book = Book(
        id=BookId("book-123"),
        title="Uploaded Book",
        author="Author",
        edition="1st",
        subject="Subject",
        file_name="uploaded.pdf",
        file_path="/path/uploaded.pdf",
        upload_timestamp=datetime.utcnow(),
        total_pages=10,
        index_status="completed",
    )
    mock_service.get_book.return_value = Success(book)
    app.dependency_overrides[get_ingestion_service] = lambda: mock_service

    dummy_pdf = io.BytesIO(b"%PDF-1.4 dummy content")
    response = client.post(
        "/api/v1/books", files={"file": ("uploaded.pdf", dummy_pdf, "application/pdf")}
    )
    assert response.status_code == 201
    json_data = response.json()
    assert json_data["success"] is True
    assert json_data["data"]["id"] == "book-123"
    assert json_data["data"]["title"] == "Uploaded Book"


def test_delete_book_success() -> None:
    mock_service = Mock(spec=IngestionApplicationService)
    book = Book(
        id=BookId("book-123"),
        title="Test Book",
        author="Test Author",
        edition="1st",
        subject="Testing",
        file_name="test.pdf",
        file_path="/path/test.pdf",
        upload_timestamp=datetime.utcnow(),
        total_pages=10,
        index_status="completed",
    )
    mock_service.get_book.return_value = Success(book)
    mock_service.delete_book.return_value = Success(None)
    app.dependency_overrides[get_ingestion_service] = lambda: mock_service

    response = client.delete("/api/v1/books/book-123")
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["success"] is True
    assert "deleted" in json_data["data"]["message"]


def test_submit_query_success() -> None:
    mock_service = Mock(spec=QueryApplicationService)

    citation = Citation(
        id=CitationId("cit-1"),
        book_title="Test Book",
        page_number=1,
        chunk_reference=ChunkId("chunk-1"),
        chapter="Chapter 1",
        section="Section 1",
        embedding_id=EmbeddingId("chunk-1"),
        retrieval_rank=1,
        similarity_score=0.9,
    )
    item = VerifiedResponseItem(
        response_id=ResponseId("resp-1"),
        query_id=QueryId("q-1"),
        answer_text="Compiled Answer",
        supporting_citations=[citation],
        supporting_excerpts=["Snippet of text"],
        verification_timestamp=datetime.utcnow(),
    )
    verified = VerifiedResponse(
        book_id=BookId("book-123"),
        items=[item],
        statistics={"duration": 1.5},
        metadata={"model": "gemini"},
    )
    dto_res = QueryResponse(
        response_id=ResponseId("resp-1"),
        generated_answer="Compiled Answer",
        citations=[CitationDto("cit-1", "Test Book", 1, "Chapter 1", "Section 1")],
        verified_response=verified,
    )

    mock_service.execute_query.return_value = Success(dto_res)
    app.dependency_overrides[get_query_service] = lambda: mock_service

    response = client.post(
        "/api/v1/queries", json={"query_text": "How does clean architecture work?"}
    )
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["success"] is True
    assert json_data["data"]["book_id"] == "book-123"
    assert json_data["data"]["items"][0]["answer_text"] == "Compiled Answer"
    assert json_data["data"]["items"][0]["supporting_citations"][0]["similarity_score"] == 0.9


def test_exception_handler_validation() -> None:
    mock_service = Mock(spec=IngestionApplicationService)
    mock_service.list_books.side_effect = ValidationException("Invalid format.")
    app.dependency_overrides[get_ingestion_service] = lambda: mock_service

    response = client.get("/api/v1/books")
    assert response.status_code == 400
    json_data = response.json()
    assert json_data["success"] is False
    assert "Invalid format." in json_data["errors"]


def test_exception_handler_retrieval() -> None:
    mock_service = Mock(spec=QueryApplicationService)
    mock_service.execute_query.side_effect = RetrievalException("Failed to retrieve chunks.")
    app.dependency_overrides[get_query_service] = lambda: mock_service

    response = client.post("/api/v1/queries", json={"query_text": "test"})
    assert response.status_code == 422
    json_data = response.json()
    assert json_data["success"] is False
    assert "Failed to retrieve chunks." in json_data["errors"]


def test_exception_handler_provider() -> None:
    mock_service = Mock(spec=IngestionApplicationService)
    mock_service.list_books.side_effect = ProviderException("ChromaDB connection lost.")
    app.dependency_overrides[get_ingestion_service] = lambda: mock_service

    response = client.get("/api/v1/books")
    assert response.status_code == 502
    json_data = response.json()
    assert json_data["success"] is False
    assert "External provider service error." in json_data["errors"]
    assert "ChromaDB" not in str(json_data)


def test_exception_handler_unhandled() -> None:
    mock_service = Mock(spec=IngestionApplicationService)
    mock_service.list_books.side_effect = RuntimeError("Database corruption!")
    app.dependency_overrides[get_ingestion_service] = lambda: mock_service

    response = client.get("/api/v1/books")
    assert response.status_code == 500
    json_data = response.json()
    assert json_data["success"] is False
    assert "An unexpected error occurred." in json_data["errors"]
    assert "Database corruption" not in str(json_data)
