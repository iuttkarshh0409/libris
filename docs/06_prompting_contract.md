# Prompting Contract

> "The Prompting Contract defines the immutable rules governing every interaction between the application and the language model. The language model is treated as a reasoning component rather than a knowledge source."

---

# 1. Purpose

The purpose of the Prompting Contract is to ensure that every generated response is:

- grounded
- reproducible
- explainable
- verifiable
- bounded by retrieved evidence

The contract establishes a strict separation between retrieval and generation.

Knowledge originates from retrieved textbook content.

The language model exists only to communicate that knowledge.

---

# 2. Architectural Position

```
Retrieval Engine
        │
        ▼
Grounding Engine
        │
        ▼
Prompt
        │
        ▼
Generation Engine
        │
        ▼
Raw Response
        │
        ▼
Citation Engine
```

The Grounding Engine is solely responsible for constructing prompts.

The Generation Engine must never construct prompts independently.

---

# 3. Knowledge Boundary

The language model must assume that the supplied Retrieval Context represents the complete available knowledge.

It must never:

- invent missing facts
- infer unsupported conclusions
- supplement information from prior knowledge
- incorporate internet knowledge
- fabricate examples

If information is absent from the Retrieval Context, it is considered unavailable.

---

# 4. Prompt Components

Every prompt consists of four sections:

```
System Instructions

↓

Task Definition

↓

Retrieved Context

↓

Query
```

No additional information may be injected.

---

# 5. System Instructions

The system instructions establish the operating rules of the language model.

These instructions remain constant for every request.

They define:

- knowledge boundaries
- response behavior
- citation requirements
- uncertainty policy
- formatting expectations

---

# 6. Task Definition

The task definition specifies the objective of the current request.

Examples include:

- explanation
- comparison
- definition
- summary
- classification

Task definitions describe *what* should be produced.

They never introduce additional knowledge.

---

# 7. Retrieved Context

The Retrieval Context is the authoritative evidence package.

It contains:

- ordered chunks
- metadata
- page references
- book references

The language model must treat this section as the only factual source.

---

# 8. Query

The original Query should be preserved exactly.

The application should not silently rewrite user questions.

Future versions may introduce optional query expansion before retrieval, but the original Query should always remain available.

---

# 9. Mandatory Rules

The language model shall:

- answer only from supplied context
- preserve factual meaning
- avoid unsupported claims
- communicate uncertainty
- produce academically appropriate language
- maintain logical structure

These rules are mandatory.

---

# 10. Prohibited Behavior

The language model shall never:

- answer from memory
- fabricate citations
- fabricate page numbers
- fabricate quotations
- invent textbook sections
- invent definitions
- merge external knowledge with retrieved evidence

Violations of these rules constitute prompt failure.

---

# 11. Missing Information Policy

If the Retrieval Context does not contain sufficient evidence, the response should state:

> "The indexed textbooks do not contain sufficient information to answer this question."

The response should not speculate.

---

# 12. Contradictory Evidence

If retrieved passages appear contradictory, the response should:

- acknowledge the inconsistency
- present both viewpoints
- avoid selecting one without evidence

The application should prioritize transparency over certainty.

---

# 13. Citation Requirements

Every factual statement should be traceable to retrieved evidence.

Responses should include citations containing:

- Book
- Chapter (when available)
- Page

Supporting excerpts should remain available for verification.

---

# 14. Response Structure

Responses should generally follow this structure:

```
Answer

↓

Key Points

↓

Supporting Explanation

↓

Citations
```

The exact presentation is handled by the Citation Engine.

---

# 15. Language Style

Responses should be:

- academically neutral
- concise
- technically accurate
- grammatically correct
- easy to verify

The language model should not exaggerate confidence.

---

# 16. Determinism

Prompt construction should be deterministic.

Given:

- identical Retrieval Context
- identical configuration
- identical Query

the Grounding Engine should construct identical prompts.

---

# 17. Prompt Versioning

Prompt templates should be versioned.

Changes to prompt behavior should be tracked through Architecture Decision Records (ADRs).

This ensures reproducibility during evaluation.

---

# 18. Future Extensions

The Prompting Contract may later support:

- multiple response styles
- explain-like-I'm-learning mode
- revision mode
- quiz mode
- citation-first mode
- comparison mode

These modes should extend the contract without violating its core principles.

---

# 19. Responsibilities

Grounding Engine

Responsible for:

- prompt construction
- evidence ordering
- instruction injection
- context packaging

Generation Engine

Responsible for:

- model invocation
- raw response generation

Citation Engine

Responsible for:

- citation attachment
- evidence mapping
- response formatting

Responsibilities should never overlap.

---

# 20. Contract Summary

The language model is not the source of knowledge.

The indexed textbooks are the source of knowledge.

The language model exists solely to transform retrieved textbook evidence into clear, well-structured, and verifiable academic responses.

Whenever evidence and model intuition conflict, evidence always takes precedence.