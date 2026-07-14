# Architectural Decisions & Log

This document outlines the core technical decisions, trade-offs, and design choices made during the creation of Libris.

---

## 1. Core Technology Choices

### Why ChromaDB?
*   **Context**: The platform requires a lightweight vector database to store and retrieve high-dimensional text embeddings locally.
*   **Decision**: We chose **ChromaDB** as the primary vector index provider.
*   **Rationale**:
    *   **In-Memory & Local Persistence**: ChromaDB is easily configured to run in-memory or persist to local folders, removing the need to manage external servers (like Pinecone, Milvus, or Qdrant) for local runs.
    *   **Python SDK**: ChromaDB has native, robust Python bindings that integrate seamlessly with FastAPI.
    *   **Rich Metadata Filtering**: It allows robust metadata tagging (book_id, page_number, chapter, section) which is vital for scoping searches to specific textbooks.

### Why SentenceTransformers?
*   **Context**: We need to transform textual fragments into dense embeddings to perform similarity search.
*   **Decision**: We chose **SentenceTransformers** (`all-MiniLM-L6-v2`) for local embedding generation.
*   **Rationale**:
    *   **Zero API Dependency**: Generation runs completely offline on CPU/GPU without calling commercial APIs (like OpenAI `text-embedding-ada-002`).
    *   **Efficiency**: The `all-MiniLM-L6-v2` model is compact (approx. 80MB) and calculates embeddings quickly while maintaining high search accuracy.
    *   **Normalization**: The model produces normalized vectors, making cosine distance calculations clean.

### Why FastAPI?
*   **Context**: The backend needs to expose endpoints for document ingestion, query execution, and system status checks.
*   **Decision**: We chose **FastAPI** as the Python web framework.
*   **Rationale**:
    *   **High Performance**: Asynchronous event loop design makes it fast.
    *   **Automatic OpenAPI Docs**: Instantly compiles code type hints into interactive Swagger documentation (`/docs`).
    *   **Pydantic Type Safety**: Guarantees request and response payloads strictly validate against API schemas before executing business logic.

### Why React?
*   **Context**: Users require a dynamic, modern, responsive frontend dashboard to manage their textbooks and submit queries.
*   **Decision**: We chose **React (with TypeScript & Vite)**.
*   **Rationale**:
    *   **Modular Component Model**: Allows separating layout components (PageHeader, EmptyState) from interactive features (QueryWorkspace, Library).
    *   **Tailwind CSS Integration**: Simplifies styling with a clean dark mode, responsive grids, and professional glassmorphic interfaces.
    *   **Vite Developer Experience**: Instant Hot Module Replacement (HMR) and fast production builds.

---

## 2. Design Patterns & Architectural Styles

### Why Clean Architecture?
*   **Context**: Porting codebase modules to different infrastructure systems (e.g. switching databases, swapping LLM vendors, replacing frontend layers) often introduces regressions if layers are highly coupled.
*   **Decision**: We structured the backend code according to **Clean Architecture**.
*   **Rationale**:
    *   **Decoupled Domain Logic**: Core business rules (like citation footnotes mapping or prompt grounding) are decoupled from FastAPI framework code, making them easy to unit test and verify.
    *   **Portability**: Swapping ChromaDB or Gemini involves modifying files *only* in the Infrastructure layer, leaving Domain and Application services completely unchanged.

### Why Aggregates & Domain Entities?
*   **Context**: Complex domain structures (like a `Book` containing multiple `Pages` which contain multiple `Chunks`) can become inconsistent if modified concurrently.
*   **Decision**: We introduced the **Aggregate Root** pattern, designating `Book` as the aggregate boundary.
*   **Rationale**:
    *   **Encapsulation**: State changes (like updating `index_status` from `queued` to `completed`) are governed directly by the `Book` aggregate.
    *   **Invariance Enforcement**: Child entities (such as pages) cannot be modified or saved independently of the parent aggregate root, guaranteeing database consistency.

### Why Provider Abstractions?
*   **Context**: Commercial APIs (like Gemini) can experience network outages, quota limits, or API key changes, which should not crash local developer setups.
*   **Decision**: We defined interfaces (contracts) like `LanguageModelProvider` and implemented a concrete `GeminiProvider` with an built-in fallback simulation.
*   **Rationale**:
    *   **Simulation Stability**: If the user lacks an API key, the system automatically routes queries to a smart local simulation that responds contextually, avoiding API timeout errors and keeping the platform runnable offline.
    *   **Interface Decoupling**: If we decide to use a self-hosted LLM (like Llama 3 via Ollama) in the future, we simply write a new provider implementing the contract, without changing the application execution pipeline.
