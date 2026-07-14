from typing import Protocol

from src.domain.entities.prompt import Prompt
from src.domain.entities.response import GeneratedResponse


class GenerationEngine(Protocol):
    """Protocol defining LLM execution and response production responsibilities."""

    def generate_response(self, prompt: Prompt) -> GeneratedResponse:
        """Invokes the language model to generate an answer matching prompt constraints."""
        ...
