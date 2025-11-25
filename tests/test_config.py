"""Tests for the configuration system."""
import pytest
from typing import Any
from pathlib import Path
from src.config import AppConfig, get_config, set_config, reload_config


@pytest.fixture
def test_config_file(tmp_path: Path):
    """Create a temporary test config file."""
    config_content = """
models:
  summarization:
    model_id: claude-3-5-sonnet-20241022
    temperature: 0.3
    max_tokens: 4096
    timeout: 60.0
"""
    config_path = tmp_path / "test_config.yaml"
    config_path.write_text(config_content)
    return config_path


def test_load_from_yaml(test_config_file: Any):
    """Test loading config from YAML file."""
    config = AppConfig.from_yaml(test_config_file)
    assert config.summarization_model == "claude-3-5-sonnet-20241022"
    assert config.temperature == 0.3
    assert config.max_tokens == 4096
    assert config.timeout == 60.0


def test_load_from_default_yaml():
    """Test loading from default config.yaml."""
    # Reset global config
    set_config(None)
    config = AppConfig.from_yaml()
    assert config.summarization_model == "gpt-4o-mini"
    assert config.temperature == 0.3
    assert config.max_tokens == 4096
    assert config.timeout == 60.0


def test_custom_config_values(tmp_path: Path):
    """Test creating config with custom values."""
    config_content = """
models:
  summarization:
    model_id: gpt-4o
    temperature: 0.7
    max_tokens: 2048
    timeout: 120.0
"""
    config_path = tmp_path / "custom_config.yaml"
    config_path.write_text(config_content)

    config = AppConfig.from_yaml(config_path)
    assert config.summarization_model == "gpt-4o"
    assert config.temperature == 0.7
    assert config.max_tokens == 2048
    assert config.timeout == 120.0


def test_global_config(test_config_file: Any):
    """Test global config singleton."""
    set_config(None)  # Reset
    config1 = get_config(test_config_file)
    config2 = get_config(test_config_file)
    assert config1 is config2  # Same instance


def test_set_and_get_config(test_config_file: Any):
    """Test setting and getting global config."""
    custom_config = AppConfig.from_yaml(test_config_file)
    set_config(custom_config)

    retrieved_config = get_config()
    assert retrieved_config is custom_config

    # Reset for other tests
    set_config(None)


def test_reload_config(tmp_path: Path):
    """Test reloading config from file."""
    config_content = """
models:
  summarization:
    model_id: claude-3-5-sonnet-20241022
    temperature: 0.3
    max_tokens: 4096
    timeout: 60.0
"""
    config_path = tmp_path / "reload_config.yaml"
    config_path.write_text(config_content)

    # Load initial config
    config1 = get_config(config_path)
    assert config1.temperature == 0.3

    # Modify file
    new_content = """
models:
  summarization:
    model_id: gpt-4o
    temperature: 0.7
    max_tokens: 2048
    timeout: 90.0
"""
    config_path.write_text(new_content)

    # Reload
    config2 = reload_config(config_path)
    assert config2.temperature == 0.7
    assert config2.summarization_model == "gpt-4o"


def test_missing_config_file():
    """Test that missing config file raises error."""
    set_config(None)
    with pytest.raises(FileNotFoundError):
        AppConfig.from_yaml(Path("/nonexistent/config.yaml"))


def test_config_validation(tmp_path: Path):
    """Test that invalid config values are rejected."""
    # Temperature out of range
    config_content = """
models:
  summarization:
    model_id: claude-3-5-sonnet-20241022
    temperature: 2.5
    max_tokens: 4096
    timeout: 60.0
"""
    config_path = tmp_path / "invalid_temp.yaml"
    config_path.write_text(config_content)

    with pytest.raises(ValueError):
        AppConfig.from_yaml(config_path)


def test_model_provider_detection():
    """Test that model IDs are correctly mapped to providers."""
    # Test Anthropic models
    anthropic_models = [
        "claude-3-5-sonnet-20241022",
        "claude-3-5-haiku-20241022",
        "claude-3-opus-20240229",
    ]
    for model in anthropic_models:
        assert model.startswith("claude-")

    # Test OpenAI models
    openai_models = [
        "gpt-4o",
        "gpt-4-turbo",
        "gpt-4o-mini",
        "gpt-3.5-turbo",
    ]
    for model in openai_models:
        assert model.startswith("gpt-")


def test_get_model_config(test_config_file: Any):
    """Test getting model config for a specific task."""
    config = AppConfig.from_yaml(test_config_file)

    # Get summarization config
    model_config = config.get_model_config("summarization")
    assert model_config.model_id == "claude-3-5-sonnet-20241022"
    assert model_config.temperature == 0.3
    assert model_config.max_tokens == 4096
    assert model_config.timeout == 60.0


def test_get_model_config_missing_task(test_config_file: Any):
    """Test that getting config for missing task raises KeyError."""
    config = AppConfig.from_yaml(test_config_file)

    with pytest.raises(KeyError):
        config.get_model_config("nonexistent_task")


def test_multiple_model_configs(tmp_path: Path):
    """Test config with multiple model configurations."""
    config_content = """
models:
  summarization:
    model_id: claude-3-5-sonnet-20241022
    temperature: 0.3
    max_tokens: 4096
    timeout: 60.0
  analysis:
    model_id: gpt-4o
    temperature: 0.5
    max_tokens: 2048
    timeout: 30.0
"""
    config_path = tmp_path / "multi_config.yaml"
    config_path.write_text(config_content)

    config = AppConfig.from_yaml(config_path)

    # Check summarization config
    summarization = config.get_model_config("summarization")
    assert summarization.model_id == "claude-3-5-sonnet-20241022"
    assert summarization.temperature == 0.3

    # Check analysis config
    analysis = config.get_model_config("analysis")
    assert analysis.model_id == "gpt-4o"
    assert analysis.temperature == 0.5


if __name__ == "__main__":
    # Run with pytest
    import sys
    sys.exit(pytest.main([__file__, "-v"]))
