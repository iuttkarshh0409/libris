# Evaluation Framework

> "The Evaluation Framework defines how the quality of Libris is measured. Unlike software testing, which verifies functional correctness, evaluation measures retrieval effectiveness, response quality, trustworthiness, and overall user value."

---

# 1. Purpose

The objective of evaluation is to determine whether the platform fulfills its primary mission:

> Helping users locate accurate, verifiable information within their academic textbooks.

Evaluation focuses on retrieval quality rather than software correctness.

A fully functional application can still perform poorly if it retrieves irrelevant evidence or generates unsupported responses.

---

# 2. Verification vs Validation

The platform distinguishes between two complementary quality processes.

| Verification | Validation |
|---------------|------------|
| Testing Strategy | Evaluation Framework |
| Does the software work correctly? | Does the retrieval system work well? |
| Functional correctness | Information quality |
| Pass / Fail | Quantitative Metrics |
| Engineering | Information Retrieval |

Testing verifies implementation.

Evaluation measures usefulness.

---

# 3. Evaluation Principles

The platform should prioritize:

- Trustworthiness
- Groundedness
- Retrieval quality
- Citation accuracy
- Explainability
- Reproducibility

Every evaluation should be repeatable using the same benchmark dataset.

---

# 4. Evaluation Pipeline

```
Benchmark Dataset

        │

Query

        │

Retrieval Engine

        │

Retrieved Context

        │

Grounding Engine

        │

Generation Engine

        │

Citation Engine

        │

Evaluation Metrics

        │

Performance Report
```

Evaluation measures every stage independently whenever possible.

---

# 5. Benchmark Dataset

Evaluation should use a curated benchmark rather than arbitrary questions.

Each benchmark entry should include:

- Question
- Expected Topic
- Expected Book
- Expected Chapter
- Expected Pages
- Expected Concepts

Example

| Question | Expected Topic |
|-----------|----------------|
| Explain CRC | Error Detection |
| What is Go-Back-N? | Data Link Layer |
| Define Congestion Control | Transport Layer |

The benchmark dataset should evolve throughout the project.

---

# 6. Retrieval Evaluation

The Retrieval Engine should be evaluated independently from the language model.

Metrics include:

---

## Recall@K

Measures whether the correct chunk appears within the first K retrieved chunks.

Higher values indicate better retrieval coverage.

---

## Precision@K

Measures how many retrieved chunks are actually relevant.

Higher precision reduces context noise.

---

## Hit Rate

Measures whether at least one relevant chunk was successfully retrieved.

---

## Mean Reciprocal Rank (MRR)

Measures how early the first relevant chunk appears.

Earlier retrieval generally produces better responses.

---

## Context Coverage

Measures whether sufficient supporting evidence was retrieved.

Retrieving only part of the required explanation should reduce coverage.

---

# 7. Generation Evaluation

Generation quality should be measured separately.

Metrics include:

---

## Groundedness

Every factual statement should be supported by retrieved evidence.

Target:

100%

---

## Faithfulness

The generated response should preserve the meaning of retrieved passages.

No unsupported interpretations.

---

## Completeness

The response should answer the user's question without omitting important retrieved information.

---

## Clarity

Responses should remain academically clear and logically organized.

---

## Consistency

Repeated executions under identical conditions should produce equivalent responses.

---

# 8. Citation Evaluation

Citation quality is a first-class metric.

Evaluation includes:

- Correct book
- Correct page
- Correct metadata
- Correct supporting excerpt

Target:

Every citation should resolve directly back to its originating chunk.

---

# 9. Hallucination Evaluation

Hallucinations are considered critical failures.

A hallucination occurs when the platform generates factual information unsupported by retrieved textbook evidence.

Examples include:

- invented definitions
- invented citations
- invented page numbers
- invented protocols
- unsupported conclusions

Target Hallucination Rate

0%

---

# 10. Performance Evaluation

Operational metrics include:

Knowledge Ingestion

- Parsing Time
- Chunking Time
- Embedding Time
- Indexing Time

Query Processing

- Retrieval Latency
- Prompt Construction Time
- Generation Time
- Total Response Time

Performance should never compromise retrieval quality.

---

# 11. Robustness Evaluation

The platform should remain reliable under challenging conditions.

Examples include:

- Large textbooks
- Small textbooks
- Poor formatting
- Empty pages
- Duplicate content
- Complex terminology

Evaluation should verify graceful degradation rather than catastrophic failure.

---

# 12. Explainability Evaluation

Users should understand why an answer was produced.

Evaluation should verify that:

- retrieved evidence is visible
- citations are complete
- supporting excerpts are accessible
- retrieval order is understandable

Transparency is considered a quality metric.

---

# 13. User-Centric Evaluation

The platform should improve the user's study experience.

Representative evaluation questions include:

- Was the correct topic retrieved?
- Was the answer understandable?
- Were citations useful?
- Could the answer be verified?
- Did retrieval reduce manual searching?

---

# 14. Evaluation Report

Every evaluation should produce a structured report.

Example

```
Libris Evaluation

Retrieval

Recall@5 ............. 96%

Precision@5 .......... 91%

MRR .................. 0.89

Generation

Groundedness ......... 100%

Faithfulness ......... 98%

Completeness ......... 95%

Citation Accuracy .... 100%

Hallucination Rate ... 0%

Performance

Average Query ........ 1.21 s

Average Index ........ 37.6 s
```

Evaluation reports should be archived for future comparison.

---

# 15. Continuous Evaluation

Evaluation should occur:

- After major architectural changes
- After embedding model changes
- After retrieval strategy updates
- After prompt modifications
- Before releases

Metrics should be compared against previous baselines to detect regressions.

---

# 16. Success Criteria

The platform is considered successful when it satisfies the following objectives:

✓ High retrieval relevance

✓ Complete citation traceability

✓ Zero hallucinations

✓ Fast interactive performance

✓ Deterministic behavior

✓ Strong user trust

---

# Evaluation Summary

The purpose of the Evaluation Framework is not to determine whether the software executes correctly.

Its purpose is to determine whether Libris fulfills its educational mission by retrieving trustworthy evidence, generating grounded responses, and enabling users to verify every answer through their academic sources.

A successful platform is not the one that generates the most impressive answers.

It is the one that users can trust without hesitation.