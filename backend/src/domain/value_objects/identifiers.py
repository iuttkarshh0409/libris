from src.shared.domain.base import Identifier


class BookId(Identifier):
    """Unique identifier for a Book."""

    pass


class ChapterId(Identifier):
    """Unique identifier for a Chapter."""

    pass


class SectionId(Identifier):
    """Unique identifier for a Section."""

    pass


class PageId(Identifier):
    """Unique identifier for a Page."""

    pass


class ChunkId(Identifier):
    """Unique identifier for a Chunk."""

    pass


class EmbeddingId(Identifier):
    """Unique identifier for an Embedding."""

    pass


class QueryId(Identifier):
    """Unique identifier for a Query."""

    pass


class ContextId(Identifier):
    """Unique identifier for a Retrieval Context."""

    pass


class PromptId(Identifier):
    """Unique identifier for a Prompt."""

    pass


class ResponseId(Identifier):
    """Unique identifier for a Generated Response."""

    pass


class CitationId(Identifier):
    """Unique identifier for a Citation."""

    pass


class DatasetId(Identifier):
    """Unique identifier for a Benchmark Dataset."""

    pass


class ReportId(Identifier):
    """Unique identifier for an Evaluation Report."""

    pass
