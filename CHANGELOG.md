# Changelog

All notable changes to **Libris** will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.0.0] - 2026-07-14

Initial release of **Libris v1.0**, an Explainable Knowledge Retrieval Platform for trustworthy academic question answering.

### Added
*   **Hierarchical Document Parsing**: `PyPDFProvider` extracted PDF chapter outlines, section headings, and physical page mappings.
*   **Semantic Chunking Engine**: Implemented character-based chunking with sliding overlaps to preserve context across block boundaries.
*   **SentenceTransformer Vector Embeddings**: Integrated native local embedding generation (`all-MiniLM-L6-v2`) mapping chunks to 384-dimensional dense vectors.
*   **Vector Storage**: Configured `ChromaDBProvider` with local file persistence and scoped textbook vector queries.
*   **FastAPI Backend Services**: Constructed clean architectural layers (Domain, Application, Infrastructure, Presentation) with dependency injection.
*   **React Frontend Dashboard**: Built responsive UI containing Library upload forms, interactive Query Workspace, System Status panels, and RAG execution diagnostics.
*   **Evaluation Framework**: Implemented benchmarking tools for retrieval accuracy and Grounding Guardrails.
*   **Release Tooling & Developer Scripts**: Provided utility scripts (`setup.ps1`, `start_all.ps1`, `test_all.ps1`, `lint_all.ps1`, `format_all.ps1`, `demo.ps1`) for onboarding automation.

### Changed
*   **Normalized Metrics**: Adjusted the retrieval similarity calculation to display cosine values normalized between `0.0` and `1.0`.
*   **Title Propagation**: Updated the RAG output schema to dynamically resolve and propagate source textbook titles instead of using placeholders.
*   **Resilient Fallback**: Upgraded the local simulation fallback in `GeminiProvider` to produce high-quality structured markdown list answers for academic questions during key offline states.
*   **State Propagation**: Configured aggregate index transitions to update the status to `completed` upon index commitment.
