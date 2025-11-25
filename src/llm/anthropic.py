"""Anthropic LLM provider."""
from pydantic import SecretStr
from langchain_core.language_models import BaseChatModel


def create_anthropic_llm(
    model: str,
    api_key: str,
    temperature: float,
    timeout: float,
) -> BaseChatModel:
    """
    Create Anthropic Claude LLM instance.

    Args:
        model: Model name (e.g., claude-3-5-sonnet-20241022)
        api_key: Anthropic API key
        temperature: Temperature for generation
        timeout: Request timeout in seconds

    Returns:
        Configured ChatAnthropic instance

    Raises:
        ImportError: If langchain-anthropic is not installed
    """
    from langchain_anthropic import ChatAnthropic

    return ChatAnthropic(
        model_name=model,
        api_key=SecretStr(api_key),
        temperature=temperature,
        timeout=timeout,
        stop=None,
    )
