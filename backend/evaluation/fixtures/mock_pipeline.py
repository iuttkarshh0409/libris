from datetime import datetime
from typing import Any

from src.application.services.query_application_service import QueryApplicationService
from src.domain.engines import (
    DefaultCitationEngine,
    DefaultGenerationEngine,
    DefaultGroundingEngine,
    DefaultRetrievalEngine,
)
from src.domain.entities.book import Book
from src.domain.entities.prompt import Prompt
from src.domain.providers.embedding import EmbeddingBatch, EmbeddingProvider, EmbeddingVector
from src.domain.providers.knowledge_index import (
    CollectionStatistics,
    IndexedVector,
    KnowledgeIndexProvider,
    SearchBatch,
    SearchResult,
)
from src.domain.repositories.book import BookRepository
from src.domain.value_objects.identifiers import BookId


class MockEmbeddingProvider(EmbeddingProvider):
    @property
    def provider_name(self) -> str:
        return "MockEmbedding"

    @property
    def provider_version(self) -> str:
        return "1.0"

    def generate_embeddings(self, texts: list[str], model_name: str) -> EmbeddingBatch:
        vectors = [
            EmbeddingVector(vector=[0.1, 0.2], dimension=2, model_identifier=model_name)
            for _ in texts
        ]
        return EmbeddingBatch(vectors=vectors, processing_time=0.01, model_identifier=model_name)

    def generate_query_embedding(self, query_text: str, model_name: str) -> EmbeddingVector:
        return EmbeddingVector(vector=[0.1, 0.2], dimension=2, model_identifier=model_name)


class MockKnowledgeIndexProvider(KnowledgeIndexProvider):
    def __init__(self, results: list[SearchResult]) -> None:
        self._results = results

    @property
    def provider_name(self) -> str:
        return "MockChroma"

    @property
    def provider_version(self) -> str:
        return "1.0"

    def create_collection(self, collection_name: str) -> None:
        pass

    def delete_collection(self, collection_name: str) -> None:
        pass

    def has_collection(self, collection_name: str) -> bool:
        return True

    def add_vectors(self, collection_name: str, vectors: list[IndexedVector]) -> None:
        pass

    def update_vectors(self, collection_name: str, vectors: list[IndexedVector]) -> None:
        pass

    def delete_vectors(
        self,
        collection_name: str,
        identifiers: list[str] | None = None,
        filter_metadata: dict[str, Any] | None = None,
    ) -> None:
        pass

    def query_similarity(
        self,
        collection_name: str,
        vector: list[float],
        limit: int,
        filter_metadata: dict[str, Any] | None = None,
    ) -> SearchBatch:
        return SearchBatch(
            results=self._results[:limit],
            search_duration=0.01,
            total_candidates=len(self._results),
        )

    def get_statistics(self, collection_name: str) -> CollectionStatistics:
        return CollectionStatistics(
            collection_name=collection_name,
            total_vectors=len(self._results),
            embedding_dimension=2,
            provider_version="1.0",
        )

    def reset_index(self) -> None:
        pass


class MockLanguageModelProvider:
    def __init__(self, response_text: str) -> None:
        self.response_text = response_text
        self.provider_name = "MockLLM"
        self.provider_version = "1.0"

    def invoke(self, prompt: Prompt) -> str:
        return self.response_text


class MockBookRepository(BookRepository):
    def __init__(self, book: Book) -> None:
        self._book = book

    def save(self, book: Book) -> None:
        pass

    def get_by_id(self, book_id: BookId) -> Book | None:
        if book_id.value == self._book.id.value:
            return self._book
        return None

    def list_all(self) -> list[Book]:
        return [self._book]

    def delete(self, book_id: BookId) -> None:
        pass


def create_mock_query_service(
    expected_pages: list[int],
    expected_chunks: list[str],
    expected_answer: str,
    book_title: str = "Test Book",
) -> QueryApplicationService:
    # 1. Prepare search results based on expected_pages and expected_chunks
    search_results = []
    # Mix of expected pages
    for idx, page in enumerate(expected_pages):
        chunk_id = expected_chunks[idx] if idx < len(expected_chunks) else f"chunk_page_{page}"
        search_results.append(
            SearchResult(
                identifier=f"emb_{chunk_id}",
                similarity_score=0.85 - (idx * 0.05),
                metadata={
                    "chunk_id": chunk_id,
                    "chunk_text": f"This is mock evidence content for page {page}.",
                    "page_number": page,
                    "book_title": book_title,
                    "chapter_id": "chapter_1",
                    "section_id": "section_1",
                },
            )
        )

    # 2. Instantiate Mock Providers
    emb_provider = MockEmbeddingProvider()
    index_provider = MockKnowledgeIndexProvider(search_results)
    llm_provider = MockLanguageModelProvider(expected_answer)

    # 3. Instantiate Mock Book Entity & Repository
    book = Book(
        id=BookId("test-book-id"),
        title=book_title,
        author="Mock Author",
        edition="1st",
        subject="Testing",
        file_name="test.pdf",
        file_path="/mock/path/test.pdf",
        upload_timestamp=datetime.now(),
        total_pages=100,
        index_status="completed",
    )
    book_repo = MockBookRepository(book)

    # 4. Instantiate default engines with mock providers
    retrieval_engine = DefaultRetrievalEngine(
        embedding_provider=emb_provider,
        index_provider=index_provider,
        book_id=book.id,
    )
    grounding_engine = DefaultGroundingEngine()
    generation_engine = DefaultGenerationEngine(provider=llm_provider)
    citation_engine = DefaultCitationEngine()

    # 5. Wire into QueryApplicationService
    return QueryApplicationService(
        retrieval_engine=retrieval_engine,
        grounding_engine=grounding_engine,
        generation_engine=generation_engine,
        citation_engine=citation_engine,
        book_repository=book_repo,
    )
