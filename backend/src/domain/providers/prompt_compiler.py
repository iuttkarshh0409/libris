from typing import Protocol

from src.domain.entities.prompt import Prompt


class PromptCompiler(Protocol):
    """Abstraction interface for compiling a logical Prompt entity

    into a provider-specific string.
    """

    def compile(self, prompt: Prompt) -> str:
        """Serializes the Prompt entity into the target prompt string."""
        ...
