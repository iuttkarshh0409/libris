# Libris

[![Python Version](https://img.shields.io/badge/python-3.10%20%7C%203.11-blue.svg)](https://www.python.org/)
[![React Version](https://img.shields.io/badge/react-18.x-cyan.svg)](https://react.dev/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-emerald.svg)](https://fastapi.tiangolo.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Tests Passing](https://img.shields.io/badge/tests-passing-brightgreen.svg)](scripts/test_all.ps1)
[![Code Style: Ruff](https://img.shields.io/badge/code%20style-ruff-black.svg)](https://github.com/astral-sh/ruff)
[![Type Checker: mypy](https://img.shields.io/badge/types-mypy-blue.svg)](https://github.com/python/mypy)

An Explainable Knowledge Retrieval Platform for trustworthy academic question answering.

Libris transforms textbooks into searchable semantic knowledge using a modular retrieval pipeline featuring:
*   **Clean Architecture**: Separation of domain rules, application coordinates, presentation API routers, and infrastructure providers.
*   **Semantic Retrieval**: Vector similarity queries on dense embeddings generated offline.
*   **Grounded Prompt Construction**: Context injection with safety constraints and threshold validation to prevent hallucinations.
*   **Citation Verification**: Automatic footnoted excerpt matching back to physical textbook page boundaries.
*   **Explainable Responses**: Live processing visualizer steps showing query progression, retrieval metrics, similarity scores, and LLM source info.
*   **Evaluation Framework**: Multi-dimensional benchmark suites to measure precision, grounding safety, and citation verification metrics.

---

## 1. Motivation

Commercial Retrieval-Augmented Generation (RAG) systems often treat uploaded documents as flat, unstructured text dumps. This approach discards textbook structure, leading to poor retrieval context, broken chapter mappings, and hallucinated answers.

**Libris** addresses this by preserving document structural relationships. It maps extracted chunks to exact pages and outline boundaries, ensuring that generated answers are strictly grounded in textbook evidence and are verifiable through exact citation hyperlinks.

---

## 2. Integrated System Architecture

The Libris platform separates ingestion and querying pipelines, coordinating single-purpose Domain Engines through Application Orchestrators.

```text
       INGESTION PIPELINE                            QUERY / RAG PIPELINE
   ┌─────────────────────────┐                   ┌─────────────────────────┐
   │      Textbook PDF       │                   │    User Query String    │
   └────────────┬────────────┘                   └────────────┬────────────┘
                │                                             │
   ┌────────────▼────────────┐                   ┌────────────▼────────────┐
   │     Document Engine     │                   │    Retrieval Engine     │
   │  (PyPDF Outline & Pages)│                   │   (ChromaDB Cosine Sim) │
   └────────────┬────────────┘                   └────────────┬────────────┘
                │                                             │
   ┌────────────▼────────────┐                   ┌────────────▼────────────┐
   │     Chunking Engine     │                   │    Grounding Engine     │
   │ (Overlapping Splitter)  │                   │ (Prompt Verification)   │
   └────────────┬────────────┘                   └────────────┬────────────┘
                │                                             │
   ┌────────────▼────────────┐                   ┌────────────▼────────────┐
   │    Embedding Engine     │                   │    Generation Engine    │
   │   (SentenceTransformers)│                   │  (Gemini API / Fallback)│
   └────────────┬────────────┘                   └────────────┬────────────┘
                │                                             │
   ┌────────────▼────────────┐                   ┌────────────▼────────────┐
   │     Indexing Engine     │                   │     Citation Engine     │
   │  (Persist to ChromaDB)  │                   │ (Source Footnotes Match)│
   └─────────────────────────┘                   └─────────────────────────┘
```

For a comprehensive pipeline walkthrough, see the [Libris Architecture Walkthrough](docs/17_architecture_walkthrough.md).

---

## 3. Technology Stack

*   **Backend Framework**: FastAPI (Python)
*   **Vector Database**: ChromaDB (local in-memory/file storage)
*   **Embeddings**: SentenceTransformers (`all-MiniLM-L6-v2` - 384 dimensions)
*   **PDF Parser**: PyPDF
*   **LLM Provider**: Google Gemini Pro (with automatic mock fallback simulation for offline running)
*   **Frontend UI**: React, TypeScript, Vite, Tailwind CSS, Lucide Icons

---

## 4. Key Features

*   **Hierarchical Ingestion**: Maps and extracts PDF outlines, chapter hierarchies, and page numbers.
*   **Book-Scoped Retrieval**: Users can scope query parameters to a single textbook or search across the entire library.
*   **Grounding Guardrails**: Automatically blocks LLM execution if the best retrieval similarity score falls below a set threshold.
*   **Interactive Citations**: Renders Markdown outputs with clickable footnotes. Clicking a citation scrolls the UI to highlight the corresponding excerpt.
*   **Execution Diagnostics**: Highlights search speed, chunk metadata, matched ranks, and the generation source (Gemini API vs. Local Simulation).
*   **Resilient Fallback**: Instantly triggers local synthesis responses if the Gemini API key is missing or invalid.

---

## 5. Abbreviated Project Structure

```text
libris/ (repository root)
├── backend/                  # FastAPI Backend Server
│   ├── src/
│   │   ├── domain/           # Core Entities, Engines & Interfaces
│   │   ├── application/      # Orchestrations, Use Cases & DTOs
│   │   ├── infrastructure/   # DB Adapters, PDF Parsers & API Clients
│   │   └── presentation/     # FastAPI Routers & Middleware
│   ├── tests/                # Pytest Test Suites
│   └── requirements.txt      # Python Dependencies
├── frontend/                 # Vite + React Frontend App
│   ├── src/
│   │   ├── components/       # Reusable Presentation Components
│   │   ├── features/         # Page Views (Library, Workspace, Status)
│   │   ├── layouts/          # Root Layout & Sidebar Navigation
│   │   └── shared/           # API Services & Type Declarations
│   └── package.json          # Node.js Dependencies
├── docs/                     # Architectural Documentation & ADRs
├── scripts/                  # Unified Automation & Developer Scripts
└── run_e2e_flow.py           # End-to-End System Validation Runner
```

---

## 6. Developer Quick Start

Get your development environment set up and run a local demonstration in under 10 minutes:

### 1. Installation
Run the setup script from the project root directory:

*   **Windows (PowerShell)**:
    ```powershell
    ./scripts/setup.ps1
    ```
*   **macOS / Linux (Bash)**:
    ```bash
    ./scripts/setup.sh
    ```

### 2. Configure Environment
Create a `.env` file in the `backend/` directory:
```env
PORT=8000
GEMINI_API_KEY=your_optional_api_key
CHROMADB_PERSIST_DIR=./data/chroma
BOOK_METADATA_DIR=./data/metadata
```

### 3. Running Servers
Start the backend and frontend dev servers simultaneously in separate terminal windows:
```powershell
./scripts/start_all.ps1
```

### 4. Running the E2E Demo
Verify that all Libris pipelines (ingestion, vector search, Gemini generation, citation verification) function correctly by executing our E2E runner:
```powershell
./scripts/demo.ps1
```

---

## 7. Testing & Quality Assurance

### Code Quality (Linting & Formatting)
Ensure code meets styling rules:
```powershell
./scripts/format_all.ps1
./scripts/lint_all.ps1
```

### Execution Verification (Tests)
Execute both backend and frontend test suites:
```powershell
./scripts/test_all.ps1
```

---

## 8. Architecture Principles

1.  **Strict Layer Boundaries**: The presentation layer never bypasses application services or accesses domain layers directly.
2.  **DIP (Dependency Inversion)**: Infrastructure providers inherit from interfaces declared inside domain or application layers.
3.  **Encapsulation**: State manipulation is controlled exclusively through aggregate roots (`Book`).

For details, review the [Libris Getting Started Guide](docs/15_getting_started.md), [Libris Developer Guide](docs/16_developer_guide.md), and [Libris Architectural Decision Log](docs/18_decision_log.md).

---

## 9. Roadmap

*   **v1.1.0**: Admin configuration module (adjust chunk sizes, models, and overlaps in real-time from the UI).
*   **v1.2.0**: Integrated OCR support for scanned physical textbooks.
*   **v1.3.0**: Production deployment scripts (Docker compose, Kubernetes Helm charts).

---

## 10. License & Contributing

This project is licensed under the [MIT License](LICENSE). 

For contribution guidelines, see [CONTRIBUTING.md](CONTRIBUTING.md).
