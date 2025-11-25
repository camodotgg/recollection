"""OpenAI LLM provider."""
from pydantic import SecretStr
from langchain_core.language_models import BaseChatModel


def create_openai_llm(
    model: str,
    api_key: str,
    temperature: float,
    max_tokens: int,
    timeout: float,
) -> BaseChatModel:
    """
    Create OpenAI LLM instance.

    Args:
        model: Model name (e.g., gpt-4o)
        api_key: OpenAI API key
        temperature: Temperature for generation
        max_tokens: Maximum tokens to generate
        timeout: Request timeout in seconds

    Returns:
        Configured ChatOpenAI instance

    Raises:
        ImportError: If langchain-openai is not installed
    """
    from langchain_openai import ChatOpenAI

    return ChatOpenAI(
        model=model,
        api_key=SecretStr(api_key),
        temperature=temperature,
        max_completion_tokens=max_tokens,
        timeout=timeout,
    )
