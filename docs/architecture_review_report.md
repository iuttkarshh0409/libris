# Architecture Review Pass Report

This report summarizes the outcomes of the Architecture Review and Synchronization Pass performed on Libris documentation. 

The review was carried out systematically to ensure a coherent, unified, and scalable architecture, strictly adhering to Clean Architecture, feature-first folder organization, and evidence-first principles without introducing unnecessary new features.

---

## 1. Ubiquitous Language Review

### Changes Made
- Standardized terminology across the entire documentation suite:
  - **Books** (from PDF/textbook/document) as the domain root entity.
  - **Generated Response** (from answer/raw response/output) as the final verified output.
  - **Retrieval Context** as the authoritative evidence package passed to prompting.
  - **Prompt Object** as the structured, typed domain model wrapping context and instructions.
- Synchronized all 8 core domain engines: **Document**, **Chunking**, **Embedding**, **Indexing**, **Retrieval**, **Grounding**, **Generation**, and **Citation**.
- Removed outdated terms: `Response Engine` (renamed to `Generation Engine`), `Response Generator`, and `Citation Formatter`.

### Affected Documents
- `02_system_architecture.md`
- `03_rag_pipeline.md`
- `04_data_model.md`
- `05_retrieval_strategy.md`
- `08_frontend_spec.md`
- `adr_002.md`

### Architectural Improvements
- Eliminates terminology drift, ensuring both development teams and AI agents share a single dictionary of concepts.

---

## 2. Architecture Consistency Review

### Changes Made
- Realigned `02_system_architecture.md` from a mixed 7-layer model to the standard **4 Clean Architecture Layers** defined in `ADR-001`:
  1. **Presentation Layer**: Exposes UI and routes inputs.
  2. **Application Layer**: Coordinates use-case workflows.
  3. **Domain Layer**: Contains business rules, Entities, and Engines.
  4. **Infrastructure Layer**: Implements adapters for storage, vector indexing, parsing, and LLM APIs.
- Introduced **Application Services** to orchestrate workflows involving multiple Engines:
  - `IngestionApplicationService`: Orchestrates Document, Chunking, Embedding, and Indexing engines to register and index a book.
  - `QueryApplicationService`: Orchestrates Retrieval, Grounding, Generation, and Citation engines to answer questions.

### Affected Documents
- `02_system_architecture.md`
- `03_rag_pipeline.md`

### Architectural Improvements
- Restores clean inward dependency direction (Presentation -> Application -> Domain <- Infrastructure).
- Prevents technical details (e.g. databases, model clients) from leaking into domain business rules.

---

## 3. Domain Model Review

### Changes Made
- Formally defined the missing **Prompt Object** domain entity in `04_data_model.md`, documenting its fields (`Prompt ID`, `Query ID`, `Context ID`, `System Instructions`, `Task Definition`, and `Raw Prompt String`).
- Standardized relationships and ownership of entities in the data model (e.g. `Query Embedding` owned by `Embedding Engine`, `Generated Response` owned by `Generation Engine`).
- Adjusted the entity-relationship map and data lifecycle lists to represent the correct sequence from book parsing to citation formatting.

### Affected Documents
- `04_data_model.md`

### Architectural Improvements
- Every domain model now maps to a single owner within the Engine Catalogue, ensuring clear creation boundaries and database integrity.

---

## 4. ADR Synchronization Pass

### Changes Made
- Updated **ADR-002: Adopt Feature-First Project Structure** to specify feature-first folders for *both* frontend and backend codebases.
- Aligned backend src folder structure layout with vertical feature slices (e.g. `features/library`, `features/query`, `features/system`, `shared`) instead of root-level layer folders, resolving discrepancies.
- Verified that decisions in ADR-001 (Clean Architecture), ADR-007 (Engines), and ADR-008 (Evidence-First) are fully represented across the updated documents.

### Affected Documents
- `docs/adr/adr_002.md`
- `02_system_architecture.md`

### Architectural Improvements
- Unifies folder architecture on frontend and backend, enabling clean modular development and making it simple to add future features (e.g. Flashcards, Quiz Mode) as isolated, vertical modules.

---

## 5. Responsibility Review

### Changes Made
- Formally associated every ingestion and query processing stage in `03_rag_pipeline.md` with its owning Engine:
  - parsing, extraction, cleaning, and metadata mapping -> **Document Engine**
  - semantic segmentation -> **Chunking Engine**
  - vector generation -> **Embedding Engine**
  - database persistence -> **Indexing Engine**
  - search and ranking -> **Retrieval Engine**
  - prompt building -> **Grounding Engine**
  - LLM inference -> **Generation Engine**
  - source mapping -> **Citation Engine**
- Clarified that Application Services (`IngestionApplicationService` and `QueryApplicationService`) act as the orchestrators for these stages, keeping the engines cohesive.

### Affected Documents
- `03_rag_pipeline.md`
- `02_system_architecture.md`

### Architectural Improvements
- Confirms zero responsibility overlap between engines, simplifying code reviews and enabling independent unit testing of each stage.

---

## 6. Diagram Review

### Changes Made
- Re-drawn and updated high-level ASCII diagrams:
  - Clean Architecture concentric circle diagram in `02_system_architecture.md` showing layer bounds.
  - End-to-end workflow charts in `02_system_architecture.md` and `03_rag_pipeline.md` to show the correct interaction of Application Services, Engines, and data artifacts.
  - Entity-relationship sequence in `04_data_model.md` showing the flow of Prompt Objects and Retrieval Contexts.

### Affected Documents
- `02_system_architecture.md`
- `03_rag_pipeline.md`
- `04_data_model.md`

### Architectural Improvements
- Visual assets now strictly match the written code spec, preventing cognitive friction when reading the documentation.

---

## 7. Scalability Review

### Changes Made
- Verified that the language across all updated documents describes a generic, domain-agnostic **Libris**.
- Confirmed that there are no hardcoded assumptions regarding the Computer Networks textbooks; the platform supports indexing textbooks of any academic subject (e.g., Biology, CS, History) without architectural changes.
- Ensured future capabilities (e.g. hybrid retrieval, table/diagram indexing, personalized quiz generation) are described in the roadmap as plugins that fit naturally into the existing four layers.

### Affected Documents
- All updated files.

### Architectural Improvements
- Confirms long-term reusable asset value for the repository.

---

## 8. Documentation Polish

### Changes Made
- Polished formatting, spacing, page titles, alert blocks, lists, and section numbering.
- Corrected minor grammatical inconsistencies and validated that all inter-document cross-references are valid.
- Ensured the core architectural intent was preserved throughout the process.

### Affected Documents
- All updated files.

---

## Remaining Observations

1. **Implementation Readiness**: The project's documentation is now 100% synchronized and represents a single, cohesive architectural vision. The foundation is set to begin code development for Phase 1 (Project Foundation) using a feature-first clean architecture pattern.
2. **EDD Integration**: The Evaluation-Driven Development (EDD) principles defined in `adr_009.md` and `12_evaluation_framework.md` are well integrated, ensuring that future performance benchmarks can run deterministically against the retrieval pipelines.
3. **No Unplanned Features**: All adjustments made were strictly corrective to align existing specifications with architectural decisions.
