from typing import Any

from src.domain.value_objects.identifiers import BookId
from src.shared.domain.base import ValueObject


class PromptSection(ValueObject):
    """Base class for structured prompt sections."""

    def __init__(self, section_type: str, title: str, content: str, order: int) -> None:
        self._section_type = section_type
        self._title = title
        self._content = content
        self._order = order

    @property
    def section_type(self) -> str:
        return self._section_type

    @property
    def title(self) -> str:
        return self._title

    @property
    def content(self) -> str:
        return self._content

    @property
    def order(self) -> int:
        return self._order


class SystemInstructionSection(PromptSection):
    """System Instructions section defining the model's operating boundaries."""

    def __init__(self, content: str, order: int = 1) -> None:
        super().__init__("system_instructions", "System Instructions", content, order)


class TaskDefinitionSection(PromptSection):
    """Task Definition section detailing the current objective."""

    def __init__(self, content: str, order: int = 2) -> None:
        super().__init__("task_definition", "Task Definition", content, order)


class EvidenceSection(PromptSection):
    """Retrieved Evidence section containing reference context chunks."""

    def __init__(self, content: str, order: int = 3) -> None:
        super().__init__("retrieved_evidence", "Retrieved Evidence", content, order)


class QuestionSection(PromptSection):
    """User Question section preserving the original question."""

    def __init__(self, content: str, order: int = 4) -> None:
        super().__init__("user_question", "User Question", content, order)


class ConstraintSection(PromptSection):
    """Constraint rules ensuring grounded and truthful generation."""

    def __init__(self, content: str, order: int = 5) -> None:
        super().__init__("constraints", "Response Constraints", content, order)


class Prompt(ValueObject):
    """Structured, typed prompt aggregate passed to the Generation Engine."""

    def __init__(
        self,
        book_id: BookId,
        items: list[PromptSection],
        statistics: dict[str, Any],
        metadata: dict[str, Any],
    ) -> None:
        self._book_id = book_id
        # Order items by their order attribute to guarantee determinism
        self._items = sorted(items, key=lambda x: x.order)
        self._statistics = statistics
        self._metadata = metadata

    @property
    def book_id(self) -> BookId:
        return self._book_id

    @property
    def items(self) -> list[PromptSection]:
        return self._items

    @property
    def statistics(self) -> dict[str, Any]:
        return self._statistics

    @property
    def metadata(self) -> dict[str, Any]:
        return self._metadata

    def to_string(self) -> str:
        """Serializes the prompt sections into a single standard string."""
        parts = []
        for item in self._items:
            parts.append(f"=== {item.title} ===\n{item.content}")
        return "\n\n".join(parts)
