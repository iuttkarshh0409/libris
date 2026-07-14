# Retrieval-Augmented Generation Pipeline

> "The Retrieval-Augmented Generation (RAG) pipeline transforms raw academic textbooks into an intelligent, searchable knowledge base while ensuring every generated response remains grounded in verifiable evidence."

---

# 1. Overview

The RAG pipeline represents the core operational flow of the application. It consists of two independent and decoupled processes:

1. **Knowledge Ingestion Pipeline**: Executed once when a textbook is uploaded or rebuilt. It parses, chunks, embeds, and indexes textbooks into the knowledge base.
2. **Query Processing Pipeline**: Executed on-demand for every user question. It retrieves relevant evidence, packages it into a prompt, generates a response, and attaches verified citations.

These pipelines are orchestrated at the Application Layer by Application Services and executed by specific Domain Engines. This separation ensures that document indexing concerns never bleed into question-answering workflows.

---

# 2. Pipeline Overview

```
                    KNOWLEDGE INGESTION
                  (Ingestion Workflow)

        PDF File (Textbook)
          │
          ▼
   Document Parsing       ◄── Owned by Document Engine
          │
          ▼
   Text Extraction        ◄── Owned by Document Engine
          │
          ▼
   Text Cleaning          ◄── Owned by Document Engine
          │
          ▼
  Metadata Extraction     ◄── Owned by Document Engine
          │
          ▼
   Document Chunking      ◄── Owned by Chunking Engine
          │
          ▼
  Embedding Generation    ◄── Owned by Embedding Engine
          │
          ▼
    Vector Indexing       ◄── Owned by Indexing Engine
          │
          ▼
    Knowledge Index       ◄── Storage Infrastructure (ChromaDBProvider)


────────────────────────────────────────────────────


                  QUERY PROCESSING
                  (Query Workflow)

        Query
          │
          ▼
   Query Validation       ◄── Orchestrated by Application Layer
          │
          ▼
   Query Embedding        ◄── Owned by Embedding Engine
          │
          ▼
  Semantic Retrieval      ◄── Owned by Retrieval Engine
          │
          ▼
   Context Assembly       ◄── Owned by Retrieval Engine
          │
          ▼
  Prompt Construction     ◄── Owned by Grounding Engine
          │
          ▼
  Response Generation     ◄── Owned by Generation Engine (GeminiProvider)
          │
          ▼
  Citation Formatting     ◄── Owned by Citation Engine
          │
          ▼
   Generated Response     ◄── Delivered to User
```

---

# 3. Knowledge Ingestion Pipeline

Coordinated by the `IngestionApplicationService`, this pipeline converts a static PDF textbook into searchable semantic knowledge. It is designed to be fully deterministic: given identical document files and parsing configurations, it must produce identical chunks and embedding vectors.

---

## Stage 1 – Document Parsing (Document Engine)
- **Purpose**: Access and inspect the uploaded PDF document structure.
- **Responsibilities**: Open PDF files, validate file integrity, determine total page counts, and detect unreadable or corrupted page layouts.
- **Inputs**: Raw PDF document.
- **Outputs**: Ordered document page streams.

## Stage 2 – Text Extraction (Document Engine)
- **Purpose**: Extract character strings from each page of the document.
- **Responsibilities**: Extract machine-readable text while preserving original reading order, page boundaries, paragraph breaks, and heading structures.
- **Outputs**: Raw page text.

## Stage 3 – Text Cleaning (Document Engine)
- **Purpose**: Standardize and sanitize the extracted text for downstream processing.
- **Responsibilities**: Remove duplicate spaces, resolve hyphenation splits at line ends, normalize line breaks, and eliminate encoding anomalies without altering the factual meaning of the textbook content.
- **Outputs**: Cleaned page text.

## Stage 4 – Metadata Extraction (Document Engine)
- **Purpose**: Link structural references to extracted text to support citation mapping.
- **Responsibilities**: Extract and map book title, author, edition, chapter, section title, and physical page number to each page of text.
- **Outputs**: Structured Page entities containing text and metadata.

## Stage 5 – Document Chunking (Chunking Engine)
- **Purpose**: Segment text pages into cohesive, independent knowledge blocks.
- **Responsibilities**: Divide Page text into semantic chunks according to a configured maximum token/character size and overlap, ensuring semantic boundaries (like paragraph ends) are preserved where possible.
- **Outputs**: Knowledge Chunk entities with link references to original pages.

## Stage 6 – Embedding Generation (Embedding Engine)
- **Purpose**: Project text chunks into a high-dimensional semantic vector space.
- **Responsibilities**: Load the configured local embedding model (via SentenceTransformerProvider) and generate a numerical vector (Embedding) representing the semantic meaning of each chunk.
- **Outputs**: Vector Embeddings mapped to Chunk IDs.

## Stage 7 – Vector Indexing (Indexing Engine)
- **Purpose**: Index and persist chunks and vectors for semantic searching.
- **Responsibilities**: Save Chunk entities, Embeddings, and metadata in the Knowledge Index (via ChromaDBProvider), making them immediately searchable.
- **Outputs**: Rebuilt or updated Knowledge Index.

---

# 4. Query Processing Pipeline

Coordinated by the `QueryApplicationService`, this pipeline processes a student's natural language question, retrieves supporting evidence, and generates a grounded, cited answer.

---

## Stage 1 – Query Validation (Application Layer)
- **Purpose**: Enforce entry boundaries before invoking heavy downstream engines.
- **Responsibilities**: Inspect question text length, verify encoding, and reject empty or invalid requests.
- **Outputs**: Validated Query.

## Stage 2 – Query Embedding (Embedding Engine)
- **Purpose**: Encode the user's question into the same vector space as the document chunks.
- **Responsibilities**: Generate a numerical vector representing the semantic intent of the query using the active embedding model (via SentenceTransformerProvider).
- **Outputs**: Query Embedding.

## Stage 3 – Semantic Retrieval (Retrieval Engine)
- **Purpose**: Locate candidate textbook chunks that match the query embedding.
- **Responsibilities**: Query the Knowledge Index (via ChromaDBProvider) to fetch candidates, filter out low-similarity chunks, and remove exact or near duplicates.
- **Outputs**: Deduplicated candidate chunks.

## Stage 4 – Context Assembly (Retrieval Engine)
- **Purpose**: Assemble the best candidate chunks into a structured evidence package.
- **Responsibilities**: Rank candidates by similarity score, expand neighboring chunks to maintain context continuity, and enforce Language Model context budgets by discarding lower-ranked blocks.
- **Outputs**: Retrieval Context.

## Stage 5 – Prompt Construction (Grounding Engine)
- **Purpose**: Construct the input prompt for the language model, wrapping evidence and instructions.
- **Responsibilities**: Construct a typed Prompt object containing System Instructions (enforcing the Knowledge Boundary), Task Definition, Retrieval Context, and the original Query.
- **Outputs**: Structured Prompt.

## Stage 6 – Response Generation (Generation Engine)
- **Purpose**: Execute model inference on the prompt.
- **Responsibilities**: Submit the Prompt to the Language Model Provider (via GeminiProvider), handle timeout and API exceptions, and capture the raw response.
- **Outputs**: Raw response text.

## Stage 7 – Citation Formatting (Citation Engine)
- **Purpose**: Map claims in the response back to original sources.
- **Responsibilities**: Verify that statements are supported by the Retrieval Context, match citations to actual page/chapter numbers, format citations, and extract supporting excerpts.
- **Outputs**: Verified academic response.

## Stage 8 – Response Delivery (Application Layer)
- **Purpose**: Package and return the results to the client interface.
- **Responsibilities**: Map the output to DTO schemas and send it to the Presentation Layer.
- **Outputs**: DTO containing answer, citations, excerpts, and retrieval metadata.

---

# 5. Information Flow

The pipeline enforces a strict information boundary: the language model never reads the original textbook directly. It is fed only the Retrieval Context assembled from the Knowledge Index.

```
  Ingestion Workflow                   Query Workflow
  
      [ Books ]                           [ Query ]
          │                                   │
          ▼                                   ▼
      [ Pages ]                       [ Query Embedding ]
          │                                   │
          ▼                                   ▼
      [ Chunks ]                      [ Similarity Search ]
          │                                   │
          ▼                                   ▼
    [ Embeddings ]                    [ Retrieval Context ]
          │                                   │
          ▼                                   ▼
   [ Knowledge Index ] ──────────────────────►[ Prompt ]
                                              │
                                              ▼
                                       [ Raw Response ]
                                              │
                                              ▼
                                     [ Generated Response ]
                                     (with cited evidence)
```

---

# 6. Pipeline Characteristics

The RAG pipeline is designed to satisfy the following core requirements:

- **Deterministic Processing**: Identical documents and settings produce identical chunks, metadata, and embeddings.
- **Grounded Generation**: Response generation is strictly gated by retrieval. No response is generated if retrieval fails or returns insufficient confidence.
- **Citation Traceability**: Every factual statement in the final answer is linked directly to a page citation and verifiable chunk excerpt.
- **Infrastructure Abstraction**: Embedding, indexing, parsing, and Language Model APIs are accessed through interfaces (Providers), making the pipeline runtime-agnostic.
- **Observability**: Execution times, similarity scores, token counts, and intermediate prompts are logged at the Application Layer.

---

# 7. Failure Handling

Each pipeline stage is self-contained. If a stage fails, execution is aborted immediately to prevent bad state propagation:
- **Ingestion Failures**: Corrupted PDFs or embedding failures abort the indexing process, roll back Knowledge Index changes, and report the issue without affecting existing library items.
- **Query Failures**: Empty search results or API timeouts trigger a fallback answer: *"The indexed textbooks do not contain sufficient information to answer this question."*

---

# Pipeline Summary

The RAG pipeline divides document management from query processing. By enforcing clear engine ownership at each stage, it guarantees that textbooks are ingested systematically, query retrieval is deterministic, and response generation is strictly grounded in cited evidence.