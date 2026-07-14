# Guardrails

> "These guardrails define the non-negotiable operating boundaries of the application. Every component, prompt, feature, and implementation must comply with these constraints."

---

# 1. Knowledge Boundary

The application is a textbook retrieval system.

It is not a general-purpose AI assistant.

Its knowledge is strictly limited to the documents that have been indexed.

No component may introduce factual information originating from outside the uploaded documents.

---

# 2. No External Knowledge

The application shall never:

- answer using model pretraining knowledge
- answer using internet knowledge
- answer using assumptions
- supplement textbook content with external facts
- combine textbook content with uncited information

Every factual response must originate from retrieved document context.

---

# 3. Retrieval Is Mandatory

Generation without retrieval is prohibited.

The retrieval pipeline must execute before every response.

If retrieval returns no sufficiently relevant context, the application shall not attempt to answer from memory.

Instead, it should explain that no relevant information could be found within the indexed documents.

---

# 4. Citation Requirement

Every factual response must include supporting citations.

At minimum, citations should contain:

- Book title
- Page number

When available, responses should also include:

- Chapter
- Section
- Retrieved excerpt

Responses without supporting citations are considered invalid.

---

# 5. No Fabricated References

The application shall never invent:

- page numbers
- chapter names
- section titles
- quotations
- diagrams
- figures
- tables
- references

If metadata cannot be determined reliably, it should be omitted rather than fabricated.

---

# 6. Uncertainty Must Be Explicit

When the retrieved evidence is:

- incomplete
- ambiguous
- conflicting
- insufficient

the application must communicate this clearly.

Confidence should never exceed the quality of the retrieved evidence.

---

# 7. Missing Information Policy

If the indexed textbooks do not contain sufficient information to answer a question, the response should explicitly state:

> "The indexed textbooks do not contain sufficient information to answer this question."

The application shall never attempt to "fill in the gaps."

---

# 8. No Internet Access

The application is intentionally isolated from external knowledge sources.

It shall not:

- search the web
- access online encyclopedias
- retrieve online documentation
- query search engines
- consult external APIs for factual content

All answers originate exclusively from indexed documents.

---

# 9. Academic Integrity

The application exists to support learning.

It must never intentionally facilitate academic dishonesty.

The system should avoid features whose primary purpose is:

- bypassing study
- fabricating assignments
- generating examination answers without supporting evidence
- disguising AI-generated work

Instead, it should encourage verification through textbook citations.

---

# 10. Transparency

Users should always understand:

- where information came from
- why it was retrieved
- which documents were used
- which pages support the response

The retrieval process should remain explainable.

---

# 11. Preserve Original Meaning

Retrieved passages may be:

- summarized
- reorganized
- simplified

provided that the original meaning is preserved.

The application must never alter the factual intent of the textbook.

---

# 12. No Silent Corrections

The application shall not silently modify textbook content.

If an OCR issue, parsing problem, or formatting ambiguity is detected, it should be reported rather than silently corrected.

---

# 13. Deterministic Retrieval

Given:

- identical indexed documents
- identical retrieval settings
- identical Query

the retrieval stage should produce consistent results.

Deterministic behavior simplifies debugging and evaluation.

---

# 14. User Data Ownership

All uploaded books remain the property of the user.

The application should:

- process documents locally whenever possible
- avoid unnecessary data transmission
- allow complete deletion of indexed content
- never retain documents after explicit deletion

---

# 15. Minimal Permissions

The application should request only the permissions necessary for operation.

It should not require:

- internet connectivity
- cloud accounts
- user authentication
- telemetry

unless explicitly enabled by the user in future versions.

---

# 16. Error Handling

Errors should be informative.

Instead of exposing stack traces or internal implementation details, the application should provide actionable guidance.

Examples include:

- unsupported PDF
- empty document
- failed embedding generation
- missing Knowledge Index
- corrupted metadata

---

# 17. Feature Acceptance Test

Before any new feature is accepted, it should satisfy the following questions:

1. Does it strengthen textbook-based learning?

2. Does it preserve citation transparency?

3. Does it respect the knowledge boundary?

4. Can every generated statement be traced to a source?

5. Does it avoid encouraging academic dishonesty?

If any answer is "No", the feature should be reconsidered.

---

# 18. Implementation Priority

When implementation trade-offs occur, prioritize in the following order:

1. Correctness
2. Trustworthiness
3. Transparency
4. Reproducibility
5. Maintainability
6. Performance
7. Convenience

Performance optimizations must never compromise retrieval quality or factual accuracy.

---

# Final Principle

This application is not designed to be the smartest assistant.

It is designed to be the most trustworthy reference assistant.

Whenever correctness and creativity conflict, correctness must always prevail.