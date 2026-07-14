# Frontend Specification

> "The Presentation Layer provides a simple, transparent, and distraction-free interface for interacting with Libris. Every interface should reinforce trust, traceability, and efficient academic study."

---

# 1. Design Goals

The frontend should prioritize:

- Simplicity
- Clarity
- Transparency
- Explainability
- Fast navigation
- Academic usability

The interface should never distract from the primary objective:

Finding trustworthy information inside textbooks.

---

# 2. Design Philosophy

The interface should feel closer to an academic research tool than a conversational chatbot.

Primary principles:

- Documents first
- Evidence first
- Minimal visual noise
- Predictable interactions
- Progressive disclosure
- Clear system feedback

Every screen should answer one question:

"What does the user need right now?"

---

# 3. Primary User Workflows

The application supports four primary workflows.

```
Manage Library

↓

Build Knowledge Index

↓

Ask Questions

↓

Review Evidence
```

Everything else is secondary.

---

# 4. Screen Overview

The MVP consists of six primary screens.

1. Dashboard
2. Library
3. Query Workspace
4. Evidence Explorer
5. Configuration
6. System Status

---

# 5. Dashboard

## Purpose

Provide an overview of the current Libris.

---

Displayed Information

- Total books
- Indexed books
- Total pages
- Total chunks
- Embedding model
- Knowledge Index status

---

Available Actions

- Upload Book
- Open Library
- Ask Question
- Open Settings

---

# 6. Library

## Purpose

Manage academic resources.

---

Display

Book Card

- Title
- Author
- Subject
- Edition
- Pages
- Index Status

---

Available Actions

- Upload
- Delete
- Rebuild Index
- View Metadata

---

# 7. Upload Workflow

```
Select PDF

↓

Validate

↓

Upload

↓

Parse

↓

Chunk

↓

Embed

↓

Index

↓

Completed
```

The interface should visualize indexing progress.

---

# 8. Query Workspace

The Query Workspace is the primary study environment.

---

Layout

```
+-----------------------------------------+

 Question Input

------------------------------------------

 Generated Answer

------------------------------------------

 Supporting Citations

------------------------------------------

 Retrieved Sources

+-----------------------------------------+
```

---

Components

Question Input

Answer Panel

Citation Panel

Evidence Panel

---

# 9. Evidence Explorer

Purpose

Allow users to inspect retrieved evidence independently of generated responses.

Displayed Information

- Book
- Chapter
- Page
- Chunk
- Similarity Rank
- Retrieved Text

Users should always be able to inspect why a response was generated.

---

# 10. Configuration

Purpose

Manage configurable platform settings.

Examples

- Chunk size
- Chunk overlap
- Retrieval limit
- Similarity threshold
- Embedding model

Configuration changes should display their expected impact before being applied.

---

# 11. System Status

Purpose

Display current platform health.

Examples

- Document Engine
- Chunking Engine
- Embedding Engine
- Indexing Engine
- Retrieval Engine
- Grounding Engine
- Generation Engine
- Citation Engine
- Storage
- Configuration

Each subsystem should report:

- Healthy
- Busy
- Warning
- Error

---

# 12. Notifications

Notifications should be informative rather than intrusive.

Examples

Book uploaded successfully.

Knowledge Index rebuilt.

Embedding generation completed.

Retrieval failed.

Unsupported document.

Messages should always suggest corrective action when applicable.

---

# 13. Loading States

Long-running operations should always expose progress.

Examples

Uploading

Parsing

Chunking

Embedding

Indexing

Retrieving

Generating

The user should never wonder whether the application is still working.

---

# 14. Empty States

The interface should gracefully handle:

No books uploaded.

No Knowledge Index.

No retrieval results.

No citations available.

Each empty state should guide the user toward the next action.

---

# 15. Error States

Errors should communicate:

What happened.

Why it happened.

What the user can do next.

Internal implementation details should remain hidden.

---

# 16. Accessibility

The interface should support:

- Keyboard navigation
- High contrast
- Readable typography
- Responsive layouts
- Clear focus indicators

Accessibility should be considered from the beginning rather than added later.

---

# 17. Future Enhancements

Future versions may include:

- Split-screen PDF viewer
- Highlight cited passages
- Reading history
- Bookmarks
- Recent queries
- Study sessions
- Flashcards
- Quiz mode
- Diagram viewer
- Multi-book comparison

These features should integrate without disrupting the existing user experience.

---

# Summary

The frontend exists to make textbook knowledge easy to discover, verify, and revisit.

Every interface should strengthen user trust by making the retrieval process visible, understandable, and reproducible.