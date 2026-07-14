# Engine Catalogue

This document defines the roles, input-output boundaries, and invariants of the eight core Domain Engines that power Libris.

---

## 1. Document Engine
*   **Responsibilities**: Validates PDF file integrity, parses pages, chapters, and sections, and structures them into a coherent hierarchy.
*   **Inputs**: Raw PDF byte stream / file path.
*   **Outputs**: `ParsedDocument` aggregate.
*   **Invariants**:
    *   Rejects corrupted or non-PDF files.
    *   Maintains sequential ordering of pages.
    *   No empty text is registered for parsed pages.

---

## 2. Chunking Engine
*   **Responsibilities**: Segments parsed page text into overlapping semantic segments (chunks) to ensure contextual density and retrieval readiness.
*   **Inputs**: `ParsedDocument` aggregate.
*   **Outputs**: `ChunkCollection` aggregate.
*   **Invariants**:
    *   Every chunk belongs to exactly one Book and Page.
    *   Validates configured chunk size and overlap limits.
    *   Preserves structural relationships (chapter/section).

---

## 3. Embedding Engine
*   **Responsibilities**: Translates raw text strings (from Chunks or Queries) into high-dimensional numerical vectors.
*   **Inputs**: `ChunkCollection` or `Query`.
*   **Outputs**: `EmbeddingCollection` or `QueryEmbedding`.
*   **Invariants**:
    *   Dimension size must match the configured embedding model schema exactly.
    *   Immutable vector mappings (vectors are never modified post-generation).

---

## 4. Indexing Engine
*   **Responsibilities**: Persists numerical embeddings and metadata into a persistent index, keeping records synchronized with source files.
*   **Inputs**: `EmbeddingCollection` aggregate.
*   **Outputs**: `KnowledgeIndex` aggregate.
*   **Invariants**:
    *   Rejects writes of duplicate chunk references.
    *   Maintains strict transactional consistency between files and vector indexes.

---

## 5. Retrieval Engine
*   **Responsibilities**: Computes similarity queries across index records to find relevant context, performing ranking and similarity filtering.
*   **Inputs**: `Query` embedding and `KnowledgeIndex`.
*   **Outputs**: `RetrievalContext` aggregate.
*   **Invariants**:
    *   Maintains monotonic decreasing order of similarity scores.
    *   Enforces configured similarity thresholds and limit boundaries.

---

## 6. Grounding Engine
*   **Responsibilities**: Forms the query context window, compiling instructions, constraints, context evidence, and question into a prompt.
*   **Inputs**: `RetrievalContext` and `Query`.
*   **Outputs**: `Prompt` aggregate.
*   **Invariants**:
    *   Never alters original evidence text.
    *   Guarantees structured prompt format (System Instructions -> Constraints -> Evidence -> Question).

---

## 7. Generation Engine
*   **Responsibilities**: Submits a prompt to the LLM provider, manages connection failures, parses outputs, and returns the response.
*   **Inputs**: `Prompt` aggregate.
*   **Outputs**: `GeneratedResponse` aggregate.
*   **Invariants**:
    *   Rejects empty responses from the provider.
    *   Tracks prompt/response token usage and durations.

---

## 8. Citation Engine
*   **Responsibilities**: Resolves citations in the generated response against retrieved chunks, verifying claim origins.
*   **Inputs**: `RetrievalContext` and `GeneratedResponse` aggregates.
*   **Outputs**: `VerifiedResponse` aggregate.
*   **Invariants**:
    *   No orphan citations (every citation maps to a chunk in the RetrievalContext).
    *   Never alters generated answer text.
    *   Preserves retrieval rank ordering.
