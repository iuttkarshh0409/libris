import time
import uuid
from datetime import datetime

from loguru import logger

from src.domain.engines.generation import GenerationEngine
from src.domain.entities.prompt import Prompt
from src.domain.entities.response import GeneratedResponse, ResponseItem
from src.domain.providers.language_model import LanguageModelProvider
from src.domain.value_objects.identifiers import QueryId, ResponseId
from src.shared.exceptions import DomainException, ValidationException


class DefaultGenerationEngine(GenerationEngine):
    """Concrete implementation of GenerationEngine.

    Transforms a compiled Prompt into a GeneratedResponse using the
    LanguageModelProvider.
    """

    def __init__(
        self,
        provider: LanguageModelProvider,
        model_identifier: str = "gemini-1.5-pro",
        temperature: float = 0.0,
    ) -> None:
        self._provider = provider
        self.model_identifier = model_identifier
        self.temperature = temperature

    def generate_response(self, prompt: Prompt) -> GeneratedResponse:
        """Invokes the language model to generate an answer matching prompt constraints."""
        start_time = time.perf_counter()
        logger.info("Generation started")

        # 1. Validate Prompt
        if prompt is None:
            logger.error("Generation failed: Prompt is None")
            raise ValidationException("Prompt cannot be None.")

        if not hasattr(prompt, "items") or not prompt.items:
            logger.error("Generation failed: Prompt items are empty")
            raise ValidationException("Prompt must contain at least one PromptSection.")

        # Serialize exactly once
        serialized_prompt = prompt.to_string()
        logger.info("Prompt serialized")

        if not serialized_prompt or serialized_prompt.strip() == "":
            logger.error("Generation failed: Serialized prompt is empty")
            raise ValidationException("Serialized prompt cannot be empty or blank.")

        # 2. Invoke Provider
        try:
            logger.info("Provider invoked")
            raw_response = self._provider.invoke(prompt)
        except Exception as e:
            logger.error(f"Generation failed: Provider invocation error: {e!s}")
            raise DomainException(f"Provider invocation failed: {e!s}") from e

        logger.info("Response received")

        # 3. Validate Response
        if raw_response is None or raw_response.strip() == "":
            logger.error("Generation failed: Empty model response")
            raise ValidationException("Model returned an empty or blank response.")

        logger.info("Response validated")

        # 4. Extract Query ID from Prompt metadata
        query_id_str = prompt.metadata.get("query_id", "unknown-query-id")
        query_id = QueryId(query_id_str)

        # 5. Build ResponseItem
        response_id = ResponseId(str(uuid.uuid4()))
        gen_timestamp = datetime.now()

        # Token usage estimation
        prompt_chars = len(serialized_prompt)
        response_chars = len(raw_response)
        estimated_prompt_tokens = prompt_chars // 4
        estimated_response_tokens = response_chars // 4

        token_usage = {
            "prompt_tokens": estimated_prompt_tokens,
            "completion_tokens": estimated_response_tokens,
            "total_tokens": estimated_prompt_tokens + estimated_response_tokens,
        }

        item = ResponseItem(
            response_id=response_id,
            query_id=query_id,
            answer_text=raw_response,
            generation_timestamp=gen_timestamp,
            model_identifier=self.model_identifier,
            finish_reason="stop",
            token_usage=token_usage,
        )

        logger.info("GeneratedResponse assembled")

        # 6. Generate statistics and metadata
        duration = time.perf_counter() - start_time

        stats = {
            "generation_duration": duration,
            "prompt_characters": prompt_chars,
            "response_characters": response_chars,
            "estimated_prompt_tokens": estimated_prompt_tokens,
            "estimated_response_tokens": estimated_response_tokens,
        }

        # Resolve provider info dynamically
        provider_name = getattr(self._provider, "provider_name", self._provider.__class__.__name__)
        provider_version = getattr(self._provider, "provider_version", "1.0.0")

        generation_source = getattr(self._provider, "last_generation_source", "Gemini")

        meta = {
            "model_identifier": self.model_identifier,
            "provider_name": provider_name,
            "provider_version": provider_version,
            "generation_temperature": self.temperature,
            "generation_timestamp": gen_timestamp.isoformat(),
            "generation_source": generation_source,
        }

        logger.info("Generation completed")

        return GeneratedResponse(
            book_id=prompt.book_id,
            items=[item],
            statistics=stats,
            metadata=meta,
        )
