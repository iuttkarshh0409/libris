# Aggregate Catalogue

This document catalogues the domain aggregate models of Libris, defining their responsibilities, constructors, producing engines, and consuming engines.

---

## 1. Aggregate Mapping Overview

| Aggregate | Owner Engine | Produced By | Consumed By |
|---|---|---|---|
| **ParsedDocument** | `DocumentEngine` | `DocumentEngine` | `ChunkingEngine` |
| **ChunkCollection** | `ChunkingEngine` | `ChunkingEngine` | `EmbeddingEngine` |
| **EmbeddingCollection** | `EmbeddingEngine` | `EmbeddingEngine` | `IndexingEngine` |
| **KnowledgeIndex** | `IndexingEngine` | `IndexingEngine` | `RetrievalEngine` |
| **RetrievalContext** | `RetrievalEngine` | `RetrievalEngine` | `GroundingEngine` + `CitationEngine` |
| **Prompt** | `GroundingEngine` | `GroundingEngine` | `GenerationEngine` |
| **GeneratedResponse** | `GenerationEngine` | `GenerationEngine` | `CitationEngine` |
| **VerifiedResponse** | `CitationEngine` | `CitationEngine` | Presentation Layer / Client |

---

## 2. Detailed Aggregate Reference

### ParsedDocument
*   **Purpose**: Represents the complete parsed structure of a book, organized into hierarchical entities.
*   **Key Fields**:
    *   `book_id: BookId`
    *   `title: str`
    *   `chapters: list[Chapter]`
    *   `pages: list[Page]`
    *   `metadata: dict`
    *   `statistics: dict`

### ChunkCollection
*   **Purpose**: Holds the set of semantic text chunks generated from a document.
*   **Key Fields**:
    *   `book_id: BookId`
    *   `chunks: list[Chunk]`
    *   `statistics: dict`
    *   `metadata: dict`

### EmbeddingCollection
*   **Purpose**: Pairs original text chunks with their generated vector embeddings.
*   **Key Fields**:
    *   `book_id: BookId`
    *   `embeddings: list[Embedding]`
    *   `statistics: dict`
    *   `metadata: dict`

### KnowledgeIndex
*   **Purpose**: Represents the persisted, searchable index records for a given book.
*   **Key Fields**:
    *   `book_id: BookId`
    *   `records: list[IndexRecord]`
    *   `statistics: dict`
    *   `metadata: dict`

### RetrievalContext
*   **Purpose**: Encapsulates the rank-ordered set of relevant chunks matching a search query.
*   **Key Fields**:
    *   `book_id: BookId`
    *   `items: list[RetrievedChunk]`
    *   `statistics: dict`
    *   `metadata: dict`

### Prompt
*   **Purpose**: The fully compiled, structured prompt ready for submission to the language model.
*   **Key Fields**:
    *   `book_id: BookId`
    *   `items: list[PromptSection]` (SystemInstruction, Constraint, Evidence, Question, etc.)
    *   `statistics: dict`
    *   `metadata: dict`

### GeneratedResponse
*   **Purpose**: Holds the raw generated response content and telemetry from the language model provider.
*   **Key Fields**:
    *   `book_id: BookId`
    *   `items: list[ResponseItem]`
    *   `statistics: dict`
    *   `metadata: dict`

### VerifiedResponse
*   **Purpose**: The final user-facing response with resolved citation mappings and verifiable excerpts.
*   **Key Fields**:
    *   `book_id: BookId`
    *   `items: list[VerifiedResponseItem]`
    *   `statistics: dict`
    *   `metadata: dict`
