from loguru import logger

from src.application.contracts.dto import IngestDocumentRequest, IngestDocumentResponse
from src.domain.engines.chunking import ChunkingEngine
from src.domain.engines.document import DocumentEngine
from src.domain.engines.embedding import EmbeddingEngine
from src.domain.engines.indexing import IndexingEngine
from src.domain.entities.book import Book
from src.domain.repositories.book import BookRepository
from src.domain.value_objects.identifiers import BookId
from src.shared.contracts.result import Failure, Result, Success
from src.shared.exceptions import DomainException, ValidationException


class IngestionApplicationService:
    """Orchestrates the ingestion pipeline workflow.

    Coordinates document parsing, chunking, embedding generation, and indexing.
    """

    def __init__(
        self,
        document_engine: DocumentEngine,
        chunking_engine: ChunkingEngine,
        embedding_engine: EmbeddingEngine,
        indexing_engine: IndexingEngine,
        book_repository: BookRepository,
    ) -> None:
        self._document_engine = document_engine
        self._chunking_engine = chunking_engine
        self._embedding_engine = embedding_engine
        self._indexing_engine = indexing_engine
        self._book_repository = book_repository

    def ingest_document(self, request: IngestDocumentRequest) -> Result[IngestDocumentResponse]:
        """Executes document ingestion end-to-end."""
        logger.info("Workflow Started")

        try:
            # 1. Validate workflow inputs
            if not request.file_path or not request.file_path.strip():
                raise ValidationException("File path cannot be empty.")
            logger.info("Request Validated")

            # 2. Parse PDF structure into hierarchical entities aggregate
            logger.info("Document Engine Invoked")
            parsed_doc = self._document_engine.parse_pdf(request.file_path)

            # 3. Save book metadata
            logger.info("Book Repository Invoked")
            self._book_repository.save(parsed_doc.book)

            # 4. Segment pages into semantic overlapping chunks using the parsed document
            logger.info("Chunking Engine Invoked")
            chunk_collection = self._chunking_engine.generate_chunks(parsed_doc)

            # 5. Generate embedding vectors for chunks
            logger.info("Embedding Engine Invoked")
            embeddings_collection = self._embedding_engine.embed_chunks(chunk_collection)

            # 6. Add chunks and embeddings to the persistent index
            logger.info("Indexing Engine Invoked")
            self._indexing_engine.add_to_index(chunk_collection, embeddings_collection)

            # 7. Update book indexing status to completed
            logger.info("Updating book index status to completed")
            parsed_doc.book.index_status = "completed"
            self._book_repository.save(parsed_doc.book)

            logger.info("Workflow Completed")
            response = IngestDocumentResponse(
                book_id=parsed_doc.book.id,
                total_pages=len(parsed_doc.pages),
                total_chunks=chunk_collection.total_chunks,
            )
            return Success(response)

        except DomainException as e:
            logger.error(f"Domain failure during ingestion workflow: {e!s}")
            return Failure(e)
        except Exception as e:
            logger.error(f"Unexpected failure during ingestion workflow: {e!s}")
            return Failure(DomainException(f"Ingestion failed: {e!s}"))

    def list_books(self) -> Result[list[Book]]:
        """Retrieves all indexed books."""
        try:
            books = self._book_repository.list_all()
            return Success(books)
        except DomainException as e:
            return Failure(e)
        except Exception as e:
            return Failure(DomainException(f"List books failed: {e!s}"))

    def get_book(self, book_id: BookId) -> Result[Book | None]:
        """Retrieves a book by its BookId."""
        try:
            book = self._book_repository.get_by_id(book_id)
            return Success(book)
        except DomainException as e:
            return Failure(e)
        except Exception as e:
            return Failure(DomainException(f"Get book failed: {e!s}"))

    def delete_book(self, book_id: BookId) -> Result[None]:
        """Deletes a book and its knowledge index records."""
        try:
            logger.info(f"Deleting book {book_id.value} from knowledge index")
            self._indexing_engine.delete_book_from_index(book_id)
            logger.info(f"Deleting book {book_id.value} from metadata repository")
            self._book_repository.delete(book_id)
            return Success(None)
        except DomainException as e:
            return Failure(e)
        except Exception as e:
            return Failure(DomainException(f"Delete book failed: {e!s}"))
