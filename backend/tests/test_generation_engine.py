import time
from unittest.mock import Mock

import pytest

from src.domain.engines.default_generation_engine import DefaultGenerationEngine
from src.domain.entities.prompt import Prompt, SystemInstructionSection, TaskDefinitionSection
from src.domain.entities.response import GeneratedResponse
from src.domain.providers.language_model import LanguageModelProvider
from src.domain.value_objects.identifiers import BookId
from src.shared.exceptions import DomainException, ValidationException


@pytest.fixture
def mock_provider() -> Mock:
    """Fixture returning a mocked LanguageModelProvider."""
    provider = Mock(spec=LanguageModelProvider)
    provider.provider_name = "MockLLMProvider"
    provider.provider_version = "2.3.4"
    return provider


@pytest.fixture
def sample_prompt() -> Prompt:
    """Fixture returning a standard valid Prompt."""
    return Prompt(
        book_id=BookId("test-textbook"),
        items=[
            SystemInstructionSection("You are a helpful assistant."),
            TaskDefinitionSection("Explain the context."),
        ],
        statistics={"total_sections": 2},
        metadata={"query_id": "query-uuid-123"},
    )


def test_generation_success(mock_provider: Mock, sample_prompt: Prompt) -> None:
    """Verifies successful generation, metadata propagation, and statistics."""
    mock_provider.invoke.return_value = "This is a generated answer from the mock provider."

    engine = DefaultGenerationEngine(
        provider=mock_provider,
        model_identifier="test-gemini-pro",
        temperature=0.7,
    )
    response = engine.generate_response(sample_prompt)

    # 1. Assert return type and structure
    assert isinstance(response, GeneratedResponse)
    assert response.book_id.value == "test-textbook"
    assert len(response.items) == 1

    # 2. ResponseItem verification
    item = response.items[0]
    assert item.answer_text == "This is a generated answer from the mock provider."
    assert item.query_id.value == "query-uuid-123"
    assert item.model_identifier == "test-gemini-pro"
    assert item.finish_reason == "stop"
    assert item.response_id is not None

    # Token usage checking
    token_usage = item.token_usage
    assert token_usage["prompt_tokens"] > 0
    assert token_usage["completion_tokens"] > 0
    expected_total = token_usage["prompt_tokens"] + token_usage["completion_tokens"]
    assert token_usage["total_tokens"] == expected_total

    # 3. Statistics assertions
    stats = response.statistics
    assert stats["generation_duration"] >= 0.0
    assert stats["prompt_characters"] == len(sample_prompt.to_string())
    assert stats["response_characters"] == len(item.answer_text)
    assert stats["estimated_prompt_tokens"] == stats["prompt_characters"] // 4
    assert stats["estimated_response_tokens"] == stats["response_characters"] // 4

    # 4. Metadata assertions
    meta = response.metadata
    assert meta["model_identifier"] == "test-gemini-pro"
    assert meta["provider_name"] == "MockLLMProvider"
    assert meta["provider_version"] == "2.3.4"
    assert meta["generation_temperature"] == 0.7
    assert meta["generation_timestamp"] is not None

    # Check provider was invoked correctly exactly once
    mock_provider.invoke.assert_called_once_with(sample_prompt)


def test_generation_empty_prompt(mock_provider: Mock) -> None:
    """Verifies that passing None prompt raises ValidationException."""
    engine = DefaultGenerationEngine(provider=mock_provider)

    with pytest.raises(ValidationException, match="Prompt cannot be None"):
        engine.generate_response(None)  # type: ignore


def test_generation_missing_prompt_sections(mock_provider: Mock) -> None:
    """Verifies that a prompt with empty items raises ValidationException."""
    engine = DefaultGenerationEngine(provider=mock_provider)
    empty_prompt = Prompt(
        book_id=BookId("test"),
        items=[],
        statistics={},
        metadata={},
    )

    with pytest.raises(ValidationException, match="Prompt must contain at least one PromptSection"):
        engine.generate_response(empty_prompt)


def test_generation_empty_serialized_prompt(mock_provider: Mock) -> None:
    """Verifies that a prompt which serializes to an empty string raises ValidationException."""
    engine = DefaultGenerationEngine(provider=mock_provider)

    # Mock a prompt that returns empty string on to_string()
    bad_prompt = Mock(spec=Prompt)
    bad_prompt.items = [SystemInstructionSection("test")]
    bad_prompt.to_string.return_value = ""

    with pytest.raises(ValidationException, match="Serialized prompt cannot be empty or blank"):
        engine.generate_response(bad_prompt)


def test_generation_provider_failure(mock_provider: Mock, sample_prompt: Prompt) -> None:
    """Verifies that a provider exception is caught and raises DomainException."""
    mock_provider.invoke.side_effect = RuntimeError("Connection timed out")

    engine = DefaultGenerationEngine(provider=mock_provider)

    with pytest.raises(DomainException, match="Provider invocation failed"):
        engine.generate_response(sample_prompt)


def test_generation_empty_provider_response(mock_provider: Mock, sample_prompt: Prompt) -> None:
    """Verifies that an empty response from the provider raises ValidationException."""
    # Return empty/spaces
    mock_provider.invoke.return_value = "   "

    engine = DefaultGenerationEngine(provider=mock_provider)

    with pytest.raises(ValidationException, match="Model returned an empty or blank response"):
        engine.generate_response(sample_prompt)


def test_generation_determinism(mock_provider: Mock, sample_prompt: Prompt) -> None:
    """Verifies that generating from the same input twice maps fields deterministically."""
    mock_provider.invoke.return_value = "Determined response."

    engine = DefaultGenerationEngine(provider=mock_provider)

    res1 = engine.generate_response(sample_prompt)
    time.sleep(0.01)  # Ensure a tiny clock delta for timestamp check
    res2 = engine.generate_response(sample_prompt)

    # Outputs must be equivalent in data content
    assert res1.items[0].answer_text == res2.items[0].answer_text
    assert res1.items[0].query_id == res2.items[0].query_id

    # Metadata and statistics mapping structure should be exactly identical
    assert res1.metadata["model_identifier"] == res2.metadata["model_identifier"]
    assert res1.metadata["provider_name"] == res2.metadata["provider_name"]
    assert res1.metadata["provider_version"] == res2.metadata["provider_version"]

    assert res1.statistics["prompt_characters"] == res2.statistics["prompt_characters"]
    assert res1.statistics["response_characters"] == res2.statistics["response_characters"]
