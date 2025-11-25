import os
import yaml
from pathlib import Path
from typing import Optional, Dict
from pydantic import BaseModel, Field
from langchain_core.language_models import BaseChatModel
from dotenv import load_dotenv

from src.llm import create_llm as _create_llm
from src.llm.types import ModelId

# Load environment variables from .env file
load_dotenv()


class ModelConfig(BaseModel):
    """
    Configuration for a single LLM model.
    """

    model_id: ModelId = Field(
        description="Model identifier (e.g., claude-3-5-sonnet-20241022)"
    )

    temperature: float = Field(
        ge=0.0,
        le=2.0,
        description="Temperature for LLM generation (lower = more consistent)"
    )

    max_tokens: int = Field(
        gt=0,
        description="Maximum tokens to generate"
    )

    timeout: float = Field(
        gt=0.0,
        description="Request timeout in seconds"
    )


class AppConfig(BaseModel):
    """
    Application configuration with LLM settings for different tasks.
    """

    # Model configurations for different tasks
    models: Dict[str, ModelConfig] = Field(
        description="Model configurations keyed by task name"
    )

    # API keys (loaded from environment)
    anthropic_api_key: Optional[str] = Field(
        default=None,
        description="Anthropic API key"
    )

    openai_api_key: Optional[str] = Field(
        default=None,
        description="OpenAI API key"
    )

    @property
    def summarization_model(self) -> ModelId:
        """Get the summarization model ID for backwards compatibility."""
        return self.models["summarization"].model_id

    @property
    def temperature(self) -> float:
        """Get the summarization temperature for backwards compatibility."""
        return self.models["summarization"].temperature

    @property
    def max_tokens(self) -> int:
        """Get the summarization max_tokens for backwards compatibility."""
        return self.models["summarization"].max_tokens

    @property
    def timeout(self) -> float:
        """Get the summarization timeout for backwards compatibility."""
        return self.models["summarization"].timeout

    def get_model_config(self, task: str) -> ModelConfig:
        """
        Get model configuration for a specific task.

        Args:
            task: Task name (e.g., "summarization")

        Returns:
            ModelConfig for the specified task

        Raises:
            KeyError: If task is not configured
        """
        return self.models[task]

    def create_llm(self, task: str = "summarization") -> BaseChatModel:
        """
        Create an LLM instance for a specific task.

        Args:
            task: Task name (e.g., "summarization")

        Returns:
            Configured LLM instance

        Raises:
            ValueError: If API key is not set for the model's provider
            KeyError: If task is not configured
        """
        model_config = self.get_model_config(task)

        # Determine which API key to use based on model
        api_key: Optional[str] = None
        if model_config.model_id.startswith("claude-"):
            api_key = self.anthropic_api_key
            if not api_key:
                raise ValueError(
                    "ANTHROPIC_API_KEY environment variable is required for Claude models"
                )
        elif model_config.model_id.startswith("gpt-"):
            api_key = self.openai_api_key
            if not api_key:
                raise ValueError(
                    "OPENAI_API_KEY environment variable is required for GPT models"
                )
        else:
            raise ValueError(f"Unknown model type: {model_config.model_id}")

        return _create_llm(
            model=model_config.model_id,
            api_key=api_key,
            temperature=model_config.temperature,
            max_tokens=model_config.max_tokens,
            timeout=model_config.timeout,
        )

    @classmethod
    def from_yaml(cls, config_path: Optional[Path] = None) -> "AppConfig":
        """
        Create config from YAML file and environment variables.

        Args:
            config_path: Path to config file. If None, uses default config.yaml in project root.

        Returns:
            AppConfig instance loaded from YAML with API keys from environment

        Raises:
            FileNotFoundError: If config file doesn't exist
            ValueError: If config file is invalid
        """
        if config_path is None:
            # Default to config.yaml in project root
            config_path = Path(__file__).parent.parent / "config.yaml"

        if not config_path.exists():
            raise FileNotFoundError(
                f"Config file not found: {config_path}\n"
                f"Please create a config.yaml file or specify a valid path."
            )

        with open(config_path, "r") as f:
            config_data = yaml.safe_load(f)

        # Parse model configurations
        models_data = config_data.get("models", {})
        models = {
            task: ModelConfig(**config)
            for task, config in models_data.items()
        }

        return cls(
            models=models,
            anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"),
            openai_api_key=os.getenv("OPENAI_API_KEY"),
        )


# Global config instance
_config: Optional[AppConfig] = None


def get_config(config_path: Optional[Path] = None) -> AppConfig:
    """
    Get or create the global config instance.

    Args:
        config_path: Path to config file. If None, uses default config.yaml.

    Returns:
        AppConfig instance loaded from YAML file

    Raises:
        FileNotFoundError: If config file doesn't exist
    """
    global _config
    if _config is None:
        _config = AppConfig.from_yaml(config_path)
    return _config


def set_config(config: Optional[AppConfig]) -> None:
    """
    Set the global config instance.

    Args:
        config: AppConfig instance to use, or None to reset
    """
    global _config
    _config = config


def reload_config(config_path: Optional[Path] = None) -> AppConfig:
    """
    Reload configuration from file.

    Args:
        config_path: Path to config file. If None, uses default config.yaml.

    Returns:
        Newly loaded AppConfig instance
    """
    set_config(None)
    return get_config(config_path)
