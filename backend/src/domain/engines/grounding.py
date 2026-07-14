from typing import Protocol

from src.domain.entities.context import RetrievalContext
from src.domain.entities.prompt import Prompt
from src.domain.entities.query import Query


class GroundingEngine(Protocol):
    """Protocol defining Prompt construction and knowledge bounding responsibilities."""

    def compile_prompt(self, query: Query, context: RetrievalContext) -> Prompt:
        """Assembles a contract-compliant Prompt from query and retrieved context."""
        ...
