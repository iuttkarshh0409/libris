# API Contract

> "The API Contract defines the external interface between the Presentation Layer and the Application Layer. It specifies every supported operation, expected inputs, outputs, validation rules, and failure behavior while remaining independent of implementation details."

---

# 1. Design Principles

The API follows several principles.

- Stateless communication
- Deterministic responses
- Explicit validation
- Predictable error handling
- Stable request/response schemas
- Versionable endpoints

The API exposes application capabilities rather than internal implementation details.

---

# 2. API Architecture

```
Frontend

      │

HTTP API

      │

Application Layer

      │

Domain Engines
```

The frontend never communicates directly with individual engines.

All requests pass through the Application Layer.

## Endpoint Mapping

| Endpoint | Application Service |
| --- | --- |
| `POST /books` | `IngestionApplicationService` |
| `POST /queries` | `QueryApplicationService` |

---

# 3. Workflow Overview

The API supports four primary workflows.

```
Book Management

↓

Knowledge Indexing

↓

Question Answering

↓

System Management
```

---

# 4. Book Management

## Upload Book

Purpose

Register a new textbook.

Input

- PDF file

Output

- Book metadata
- Upload status

Possible Errors

- Unsupported format
- Empty document
- Duplicate upload

---

## List Books

Purpose

Retrieve all indexed books.

Output

- Book list
- Metadata
- Index status

---

## Get Book

Purpose

Retrieve metadata for one book.

Output

- Book details
- Statistics
- Index information

---

## Delete Book

Purpose

Remove a book and its associated Knowledge Index.

Output

Deletion confirmation.

---

# 5. Knowledge Indexing

## Build Index

Purpose

Process one uploaded book into searchable knowledge.

Pipeline

```
Parse

↓

Chunk

↓

Embed

↓

Index
```

Output

- Index status
- Processing statistics

---

## Rebuild Index

Purpose

Discard and regenerate an existing Knowledge Index.

---

## Index Status

Purpose

Report current indexing progress.

Information

- queued
- processing
- completed
- failed

---

# 6. Question Answering

## Submit Query

Purpose

Answer a natural-language question.

Input

Question text

Output

- Answer
- Citations
- Supporting excerpts

Possible Errors

- No indexed books
- Retrieval failure
- Empty query

---

## Retrieve Sources

Purpose

Return only supporting evidence.

Useful for debugging and evaluation.

Output

Retrieved chunks.

No generated answer.

---

## Explain Retrieval

Purpose

Display how evidence was selected.

Output

- similarity ranking
- retrieved chunks
- metadata

This endpoint supports transparency and evaluation.

---

# 7. Configuration

## Read Configuration

Returns active application configuration.

---

## Update Configuration

Allows modification of configurable values.

Examples

- chunk size
- overlap
- retrieval limit
- similarity threshold

Configuration updates should require validation.

---

# 8. System Status

Returns overall application health.

Examples

- embedding model loaded
- Knowledge Index available
- storage available
- configuration valid

---

# 9. Request Validation

Every request should be validated before execution.

Validation includes:

- required fields
- supported file types
- input length
- encoding
- duplicate uploads

Invalid requests must never reach domain engines.

---

# 10. Response Model

Every successful response should include:

- status
- message
- payload

Responses should remain consistent across endpoints.

---

# 11. Error Model

Every failed response should include:

- error code
- human-readable message
- recoverability
- suggested action

Internal implementation details should never be exposed.

---

# 12. Versioning

The API should support explicit versioning.

Example

```
/api/v1/
```

Breaking changes require a new version.

---

# 13. Security

Current MVP assumptions:

- local application
- single user
- no authentication

Future versions may introduce authentication without changing existing workflows.

---

# 14. Future Endpoints

Future capabilities may include:

- batch queries
- study sessions
- flashcard generation
- quiz generation
- retrieval evaluation
- benchmark execution
- export citations
- export notes

These extensions should preserve existing API contracts.

---

# Summary

The API represents the public interface of the application.

It exposes workflows rather than implementation details, allowing the internal architecture to evolve without affecting external consumers.