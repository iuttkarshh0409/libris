# Product Principles

> "Every feature, architectural decision, and implementation should reinforce these principles. When trade-offs arise, these principles take precedence over convenience."

---

# 1. Purpose Before Intelligence

The system exists to help users locate and understand information within their own academic resources.

It is not designed to replace textbooks, instructors, or the learning process.

Every response should encourage verification from the original source.

---

# 2. Retrieval Before Generation

The application shall always retrieve relevant information before attempting to generate a response.

Generation without supporting evidence is prohibited.

No answer should be produced unless relevant context has first been retrieved from the indexed documents.

This principle defines the core architecture of the application.

---

# 3. Evidence Over Confidence

Every factual statement presented to the user should be supported by retrieved textbook content.

The confidence of the language must never exceed the confidence of the retrieved evidence.

If evidence is weak, the response should clearly communicate that uncertainty.

---

# 4. Transparency Over Completeness

The system should honestly communicate what it knows and what it does not know.

Incomplete but truthful answers are preferable to complete but speculative answers.

When the indexed textbooks do not contain sufficient information, the application shall explicitly state that limitation.

---

# 5. Textbooks Are the Source of Truth

Uploaded textbooks represent the complete knowledge boundary of the application.

No external knowledge sources shall influence factual responses.

The model's role is limited to organizing, summarizing, and explaining retrieved textbook content.

---

# 6. Every Answer Must Be Verifiable

Users should always be able to trace an answer back to its original location.

Each response should include:

- Book name
- Chapter (when available)
- Page number
- Supporting excerpts

The application should make verification effortless.

---

# 7. Preserve Academic Integrity

The system is designed to assist learning, not bypass it.

Features that encourage genuine understanding are encouraged.

Features that automate academic dishonesty are outside the intended scope of the project.

The application should support studying rather than replacing it.

---

# 8. Simplicity Before Complexity

Solutions should remain as simple as possible while satisfying project requirements.

Avoid introducing additional frameworks, services, or infrastructure without clear justification.

Complexity must provide measurable value.

---

# 9. Local-First Architecture

Whenever practical, user documents and Knowledge Indexes should remain on the user's machine.

The application should minimize unnecessary dependence on external services.

This improves:

- privacy
- portability
- reliability
- offline usability

---

# 10. Explainability

Users should understand why a particular answer was produced.

The application should expose:

- retrieved sources
- relevance ordering
- supporting passages
- citations

The retrieval process should never become a black box.

---

# 11. Modular Design

Every major responsibility should belong to a dedicated component.

Examples include:

- PDF parsing
- text preprocessing
- chunking
- embedding generation
- vector storage
- retrieval
- prompt construction
- response formatting

Each component should have clearly defined inputs and outputs.

---

# 12. Deterministic Data Processing

Document ingestion should produce consistent results.

Identical input documents should generate identical chunks, metadata, and embeddings unless configuration changes.

Deterministic preprocessing improves reproducibility and debugging.

---

# 13. Fail Safely

If any stage of the retrieval pipeline fails, the application should fail gracefully.

Examples include:

- corrupted PDFs
- unsupported file formats
- missing Knowledge Indexes
- unavailable embedding models

Failures should provide actionable feedback rather than obscure errors.

---

# 14. User Control

The user owns all uploaded documents and generated indexes.

The application should provide mechanisms to:

- add books
- remove books
- rebuild indexes
- inspect indexed content
- manage storage

No hidden processing should occur without user awareness.

---

# 15. Performance with Purpose

Performance improvements should never compromise retrieval quality.

Fast but inaccurate retrieval is less valuable than slightly slower retrieval with correct evidence.

Optimization should focus on:

- retrieval latency
- indexing efficiency
- memory usage
- responsiveness

without sacrificing correctness.

---

# 16. Scalability Through Abstraction

Although the initial version targets three textbooks, the architecture should not assume this limitation.

Components should remain sufficiently abstract to support:

- additional books
- multiple subjects
- larger collections
- future retrieval strategies

without significant redesign.

---

# 17. Documentation as a First-Class Artifact

Architecture, decisions, and implementation details should be documented alongside the code.

Documentation should remain synchronized with implementation throughout the project's lifecycle.

Well-maintained documentation reduces ambiguity for both human contributors and AI development agents.

---

# Summary

Every implementation decision should be evaluated against a single question:

> "Does this make the system a more trustworthy textbook reference assistant?"

If the answer is no, the decision should be reconsidered.