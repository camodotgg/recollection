"""Type definitions for LLM module."""
from typing import Literal


# Supported model IDs
ModelId = Literal[
    # Anthropic models
    "claude-3-5-sonnet-20241022",
    "claude-3-5-haiku-20241022",
    "claude-3-opus-20240229",
    # OpenAI models
    "gpt-4-turbo",
    "gpt-4o",
    "gpt-4o-mini",
    "gpt-3.5-turbo",
]


# Provider types
Provider = Literal["anthropic", "openai"]
