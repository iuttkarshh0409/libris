from typing import Protocol

from src.domain.entities.prompt import Prompt


class LanguageModelProvider(Protocol):
    """Abstraction interface for executing text generation on an LLM."""

    def invoke(self, prompt: Prompt) -> str:
        """Submits the compiled Prompt to the model and returns the raw output string."""
        ...
