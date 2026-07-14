# Data Model

> "The data model defines the canonical representation of every entity managed by the application. All components must operate on these models to ensure consistency, interoperability, and maintainability."

---

# 1. Overview

The application manages several categories of data:

- Source Documents (Books)
- Document Structure (Chapters, Sections, Pages)
- Knowledge Chunks
- Embeddings (Chunk Embeddings, Query Embeddings)
- Retrieval Results
- Queries
- Prompts
- Generated Responses
- Citations
- Application Configuration
- Benchmark Datasets
- Evaluation Reports

Every entity has a single source of truth and a dedicated owning Engine or Application Service. No component should redefine these models independently.

---

# 2. Entity Relationship Overview

```
Book
 │
 ├── Chapter
 │      │
 │      └── Section
 │              │
 │              └── Page
 │                      │
 │                      └── Chunk
 │                              │
 │                              └── Embedding
 
 
Query ──► Query Embedding ──► Retrieval Result ──► Retrieval Context
                                                        │
                                                        ▼
Generated Response ◄── Citation ◄── Raw Response ◄── Prompt


Benchmark Dataset ──► Query ──► Generated Response ──► Evaluation Report
```

---

# 3. Book

Represents one uploaded textbook.

## Attributes

- Book ID (unique identifier)
- Title (string)
- Author (string)
- Edition (string)
- Subject (string)
- File Name (string)
- File Path (string)
- Upload Timestamp (datetime)
- Total Pages (integer)
- Index Status (queued, processing, completed, failed)

## Responsibilities

A Book acts as the root entity for all extracted structure, text, and chunks.

---

# 4. Chapter

Represents a logical chapter within a textbook.

## Attributes

- Chapter ID (unique identifier)
- Book ID (foreign key reference)
- Chapter Number (integer or string)
- Chapter Title (string)
- Start Page (integer)
- End Page (integer)

Chapters provide logical groupings for context ranking and citation formatting.

---

# 5. Section

Represents a subsection inside a chapter.

## Attributes

- Section ID (unique identifier)
- Chapter ID (foreign key reference)
- Title (string)
- Start Page (integer)
- End Page (integer)

Sections improve chunk grouping and retrieval citation granularity.

---

# 6. Page

Represents one physical page from the source Book.

## Attributes

- Page Number (integer)
- Book ID (foreign key reference)
- Extracted Text (string)
- Character Count (integer)

Pages remain immutable after extraction and serve as the canonical locator for citations.

---

# 7. Chunk

The Chunk is the fundamental knowledge unit of the application. Every indexing, search, and retrieval operation ultimately revolves around chunks.

## Attributes

- Chunk ID (unique identifier)
- Book ID (foreign key reference)
- Chapter ID (foreign key reference, optional)
- Section ID (foreign key reference, optional)
- Page Number (integer)
- Chunk Index (integer)
- Chunk Text (string)
- Character Count (integer)
- Token Count (integer)
- Previous Chunk ID (self-reference for sequence)
- Next Chunk ID (self-reference for sequence)

---

# 8. Embedding

Represents the vector representation of one chunk.

## Attributes

- Embedding ID (unique identifier)
- Chunk ID (foreign key reference)
- Model Identifier (string)
- Vector Dimension (integer)
- Embedding Vector (array of floats)
- Generated Timestamp (datetime)

Each chunk has one embedding per embedding model.

---

# 9. Knowledge Index

Represents the searchable collection of embeddings and chunk metadata. It is a logical view managed by the Indexing Engine, mapped to ChromaDB infrastructure storage.

---

# 10. Query

Represents a question submitted by the user.

## Attributes

- Query ID (unique identifier)
- Original Question (string)
- Query Timestamp (datetime)

Queries are immutable after creation.

---

# 11. Query Embedding

Represents the semantic encoding of the user's question.

## Attributes

- Query ID (foreign key reference)
- Model Identifier (string)
- Vector Representation (array of floats)

Query embeddings are transient. They are generated on-the-fly and do not require permanent database storage.

---

# 12. Retrieval Result

Represents one retrieved chunk and its similarity rating.

## Attributes

- Chunk Reference (Chunk object or ID)
- Similarity Score (float)
- Retrieval Rank (integer)

Multiple Retrieval Results are ranked to form the retrieval context.

---

# 13. Retrieval Context

Represents the ordered collection of retrieved chunks supplied to the grounding pipeline.

## Attributes

- Context ID (unique identifier)
- Query ID (foreign key reference)
- Ordered Chunks (list of Chunk references)
- Total Tokens (integer)

The Retrieval Context defines the strict knowledge boundary for response generation.

---

# 14. Prompt

Represents the structured, typed prompt passed to the Generation Engine. It is a domain entity, not a simple serialized string.

## Attributes

- Prompt ID (unique identifier)
- Query ID (foreign key reference)
- Context ID (foreign key reference)
- System Instructions (string, enforcing Knowledge Boundary rules)
- Task Definition (string, specifying output format)
- Raw Prompt String (compiled prompt string ready for inference)

The Prompt is constructed by the Grounding Engine.

---

# 15. Generated Response

Represents the final verifiable answer produced by the application.

## Attributes

- Response ID (unique identifier)
- Query ID (foreign key reference)
- Generated Answer (string)
- Supporting Citations (list of Citation objects)
- Supporting Excerpts (list of strings)
- Generation Timestamp (datetime)

Generated Responses should never exist without supporting citations.

---

# 16. Citation

Represents traceable evidence supporting part of a response.

## Attributes

- Citation ID (unique identifier)
- Book Title (string)
- Chapter (string, optional)
- Section (string, optional)
- Page Number (integer)
- Chunk Reference (Chunk ID)

Every citation must resolve back to a specific, verifiable Chunk in the database.

---

# 17. Configuration

Represents configurable parameters of the system.

## Attributes

- Config ID (unique identifier)
- Chunk Size (integer)
- Chunk Overlap (integer)
- Embedding Model Identifier (string)
- Similarity Threshold (float)
- Retrieval Limit (integer)
- Language Model Parameters (JSON string/object)

Configuration exists outside the application code to allow adjustments without recompilation.

---

# 18. Benchmark Dataset

Represents a curated dataset of evaluation test cases.

## Attributes

- Dataset ID (unique identifier)
- Name (string)
- Subject / Domain (string)
- Created Timestamp (datetime)
- Test Cases (list of Query-Context-Expected Response triplets)

Benchmark Datasets are used to perform quantitative evaluation of the retrieval and generation stages.

---

# 19. Evaluation Report

Represents the results of running an evaluation run against a Benchmark Dataset.

## Attributes

- Report ID (unique identifier)
- Dataset ID (foreign key reference)
- Timestamp (datetime)
- Recall At K (float)
- Precision At K (float)
- Groundedness Rate (float)
- Hallucination Rate (float)
- Average Latency MS (float)
- Detailed Results (list of validation outcomes per test case)

Evaluation Reports are archived for regression tracking.

---

# 20. Data Lifecycle

```
[ Books ]
    │
    ▼
[ Pages ]
    │
    ▼
[ Chunks ]
    │
    ▼
[ Embeddings ]
    │
    ▼
[ Knowledge Index ]

──────────────────────────────

[ Query ]
    │
    ▼
[ Query Embedding ]
    │
    ▼
[ Retrieval Results ]
    │
    ▼
[ Retrieval Context ]
    │
    ▼
[ Prompt ]
    │
    ▼
[ Generated Response ]
```

---

# 21. Entity Ownership

Every entity is owned by exactly one core Domain Engine or Application Service, which is responsible for its creation, validation, and lifecycle.

| Entity | Owner |
|---|---|
| **Book** | Document Engine |
| **Chapter** | Document Engine |
| **Section** | Document Engine |
| **Page** | Document Engine |
| **Chunk** | Chunking Engine |
| **Embedding** | Embedding Engine |
| **Knowledge Index** | Indexing Engine |
| **Query** | Retrieval Engine |
| **Query Embedding** | Embedding Engine |
| **Retrieval Result** | Retrieval Engine |
| **Retrieval Context** | Retrieval Engine |
| **Prompt** | Grounding Engine |
| **Generated Response** | Generation Engine |
| **Citation** | Citation Engine |
| **Configuration** | Application Service |
| **Benchmark Dataset** | Application Service |
| **Evaluation Report** | Application Service |

---

# 22. Design Principles

The data model is built on the following rules:

- **Immutability of Source Data**: Once Book, Chapter, Page, and Chunk entities are indexed, they are immutable.
- **Traceability**: Every output (Generated Response, Citation) must trace back through Prompt and Retrieval Context to raw Chunks.
- **Explicit Engine Ownership**: No entity should be created or mutated by a component other than its owning Engine (or Application Service for global configuration and evaluation entities).
- **Infrastructure Independence**: Entities are defined as pure data objects in the Domain Layer, independent of database schemas or API frameworks.

---

# Summary

The data model establishes a canonical representation of academic knowledge, retrieval states, prompts, and responses. Every component in the system exchanges information using these standardized entities, ensuring consistency and correctness across the entire application lifecycle.