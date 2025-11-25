"""LLM factory for creating language model instances."""
from langchain_core.language_models import BaseChatModel

from .types import ModelId, Provider
from .anthropic import create_anthropic_llm
from .openai import create_openai_llm


def get_provider_for_model(model: ModelId) -> Provider:
    """
    Determine the provider for a given model ID.

    Args:
        model: Model identifier

    Returns:
        Provider name (anthropic or openai)

    Raises:
        ValueError: If model ID is unknown
    """
    if model.startswith("claude-"):
        return "anthropic"
    elif model.startswith("gpt-"):
        return "openai"
    else:
        raise ValueError(f"Unknown model ID: {model}")


def create_llm(
    model: ModelId,
    api_key: str,
    temperature: float = 0.3,
    max_tokens: int = 4096,
    timeout: float = 60.0,
) -> BaseChatModel:
    """
    Create an LLM instance based on model ID.

    Args:
        model: Model identifier
        api_key: API key for the provider
        temperature: Temperature for generation (0.0-2.0)
        max_tokens: Maximum tokens to generate
        timeout: Request timeout in seconds

    Returns:
        Configured LLM instance

    Raises:
        ValueError: If model or provider is unknown
        ImportError: If required provider package is not installed
    """
    provider = get_provider_for_model(model)

    if provider == "anthropic":
        return create_anthropic_llm(
            model=model,
            api_key=api_key,
            temperature=temperature,
            timeout=timeout,
        )
    elif provider == "openai":
        return create_openai_llm(
            model=model,
            api_key=api_key,
            temperature=temperature,
            max_tokens=max_tokens,
            timeout=timeout,
        )
    else:
        raise ValueError(f"Unsupported provider: {provider}")
