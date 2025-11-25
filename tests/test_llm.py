"""Tests for LLM module."""
import pytest
from unittest.mock import Mock, patch

from src.llm import create_llm, get_provider_for_model
from src.llm.types import ModelId


def test_get_provider_for_anthropic_models():
    """Test provider detection for Anthropic models."""
    assert get_provider_for_model("claude-3-5-sonnet-20241022") == "anthropic"
    assert get_provider_for_model("claude-3-5-haiku-20241022") == "anthropic"
    assert get_provider_for_model("claude-3-opus-20240229") == "anthropic"


def test_get_provider_for_openai_models():
    """Test provider detection for OpenAI models."""
    assert get_provider_for_model("gpt-4o") == "openai"
    assert get_provider_for_model("gpt-4-turbo") == "openai"
    assert get_provider_for_model("gpt-4o-mini") == "openai"
    assert get_provider_for_model("gpt-3.5-turbo") == "openai"


def test_get_provider_for_unknown_model():
    """Test that unknown models raise ValueError."""
    with pytest.raises(ValueError, match="Unknown model ID"):
        get_provider_for_model("unknown-model")  # type: ignore


@patch("langchain_anthropic.ChatAnthropic")
def test_create_anthropic_llm(mock_chat_anthropic):
    """Test creating Anthropic LLM."""
    mock_llm = Mock()
    mock_chat_anthropic.return_value = mock_llm

    llm = create_llm(
        model="claude-3-5-sonnet-20241022",
        api_key="test-key",
        temperature=0.5,
        max_tokens=2048,
        timeout=30.0,
    )

    assert llm is mock_llm
    mock_chat_anthropic.assert_called_once()
    call_kwargs = mock_chat_anthropic.call_args[1]
    assert call_kwargs["model_name"] == "claude-3-5-sonnet-20241022"
    assert call_kwargs["temperature"] == 0.5
    assert call_kwargs["timeout"] == 30.0


@patch("langchain_openai.ChatOpenAI")
def test_create_openai_llm(mock_chat_openai):
    """Test creating OpenAI LLM."""
    mock_llm = Mock()
    mock_chat_openai.return_value = mock_llm

    llm = create_llm(
        model="gpt-4o",
        api_key="test-key",
        temperature=0.7,
        max_tokens=1024,
        timeout=60.0,
    )

    assert llm is mock_llm
    mock_chat_openai.assert_called_once()
    call_kwargs = mock_chat_openai.call_args[1]
    assert call_kwargs["model"] == "gpt-4o"
    assert call_kwargs["temperature"] == 0.7
    assert call_kwargs["max_completion_tokens"] == 1024
    assert call_kwargs["timeout"] == 60.0


def test_create_llm_default_parameters():
    """Test that create_llm accepts default parameters."""
    # We can't actually call it without mocking, but we can check the signature
    from inspect import signature
    sig = signature(create_llm)

    # Check default values
    assert sig.parameters["temperature"].default == 0.3
    assert sig.parameters["max_tokens"].default == 4096
    assert sig.parameters["timeout"].default == 60.0


if __name__ == "__main__":
    # Run with pytest
    import sys
    sys.exit(pytest.main([__file__, "-v"]))
