from src.application.services.ingestion_application_service import IngestionApplicationService
from src.application.services.query_application_service import QueryApplicationService
from src.domain.engines import (
    DefaultChunkingEngine,
    DefaultCitationEngine,
    DefaultDocumentEngine,
    DefaultEmbeddingEngine,
    DefaultGenerationEngine,
    DefaultGroundingEngine,
    DefaultIndexingEngine,
    DefaultRetrievalEngine,
)
from src.infrastructure.providers.document.pypdf import PyPDFProvider
from src.infrastructure.providers.embedding.sentence_transformers import SentenceTransformerProvider
from src.infrastructure.providers.knowledge_index.chromadb import ChromaDBProvider
from src.infrastructure.providers.language_model.gemini import (
    GeminiPromptCompiler,
    GeminiProvider,
)
from src.infrastructure.providers.storage.local import LocalStorageProvider
from src.infrastructure.repositories.book import LocalBookRepository
from src.infrastructure.repositories.knowledge_index import VectorKnowledgeIndexRepository


class Container:
    """Dependency Injection Container for the RAG platform.

    Wires together infrastructure providers, domain engines, and application services.
    """

    def __init__(self) -> None:
        # 1. Instantiate concrete infrastructure providers (placeholders)
        self.storage_provider = LocalStorageProvider()
        self.document_provider = PyPDFProvider()
        self.index_provider = ChromaDBProvider()
        self.embedding_provider = SentenceTransformerProvider()
        self.prompt_compiler = GeminiPromptCompiler()
        self.llm_provider = GeminiProvider()

        # 2. Instantiate concrete repository implementations (placeholders)
        self.book_repository = LocalBookRepository()
        self.knowledge_index_repository = VectorKnowledgeIndexRepository()

        # 3. Instantiate default domain engines (placeholders)
        self.document_engine = DefaultDocumentEngine(document_provider=self.document_provider)
        self.chunking_engine = DefaultChunkingEngine()
        self.embedding_engine = DefaultEmbeddingEngine(provider=self.embedding_provider)
        self.indexing_engine = DefaultIndexingEngine(provider=self.index_provider)
        self.retrieval_engine = DefaultRetrievalEngine(
            embedding_provider=self.embedding_provider,
            index_provider=self.index_provider,
        )
        self.grounding_engine = DefaultGroundingEngine()
        self.generation_engine = DefaultGenerationEngine(provider=self.llm_provider)
        self.citation_engine = DefaultCitationEngine()

        # 4. Instantiate application services with all engine and provider dependencies injected
        self.ingestion_service = IngestionApplicationService(
            document_engine=self.document_engine,
            chunking_engine=self.chunking_engine,
            embedding_engine=self.embedding_engine,
            indexing_engine=self.indexing_engine,
            book_repository=self.book_repository,
        )
        self.query_service = QueryApplicationService(
            retrieval_engine=self.retrieval_engine,
            grounding_engine=self.grounding_engine,
            generation_engine=self.generation_engine,
            citation_engine=self.citation_engine,
            book_repository=self.book_repository,
        )


# Global container instance for dependency resolution
container = Container()
