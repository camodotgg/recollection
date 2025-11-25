# recollection

A content summarization and learning tool that automatically loads content from various sources and generates structured summaries using LLM.

## Features

### Magic Loader

The Magic Loader automatically detects content type from URLs or file paths and loads content using LangChain's document loader ecosystem. It supports:

- **Web URLs** - Articles, blog posts, web pages
- **PDF Documents** - Local files and remote URLs
- **YouTube Videos** - Automatic transcript extraction
- **Text Files** - Local `.txt` and `.md` files

Each source is loaded and summarized with:
- Abstract (2-3 sentence overview)
- Introduction (context and themes)
- Chapters (logical sections with headings)
- Conclusion (key takeaways)

## Installation

```bash
# Install dependencies
uv sync

# Install with dev dependencies (includes pytest)
uv sync --extra dev

# Set up API keys
cp .example.env .env
# Then edit .env and add your API key(s)
```

## Usage

### Basic Detection Test

```bash
python examples/demo.py
```

### Load and Summarize Content

```bash
# Make sure you've set up your .env file with API keys (see Installation)

# Load a web article
uv run python examples/demo.py https://example.com/article

# Load a PDF
uv run python examples/demo.py https://example.com/document.pdf

# Load a YouTube video
uv run python examples/demo.py https://youtube.com/watch?v=video_id
```

### Programmatic Usage

```python
from src.content.loader.magic import MagicLoader
from src.config import get_config

# Get config and create LLM for summarization task
config = get_config()
llm = config.create_llm("summarization")  # or just config.create_llm() - defaults to "summarization"

# Create loader with LLM (reusable for multiple loads)
loader = MagicLoader(llm)

# Load content from multiple sources
content1 = loader.load("https://example.com/article")
content2 = loader.load("https://example.com/paper.pdf")
content3 = loader.load("https://youtube.com/watch?v=xyz")

# Access structured data
print(content1.summary.abstract.body)
print(content1.summary.introduction.body)
for chapter in content1.summary.chapters:
    print(f"{chapter.heading}: {chapter.body}")
print(content1.summary.conclusion.body)

# Access source metadata
print(f"Author: {content1.source.author}")
print(f"Format: {content1.source.format.value}")

# Access raw content
print(content1.raw)
```

## Testing

Run the test suite with pytest:

```bash
# Run all tests
uv run pytest

# Run with verbose output
uv run pytest -v

# Run specific test file
uv run pytest tests/test_config.py

# Run specific test
uv run pytest tests/test_config.py::test_default_config
```

The test suite includes:
- **test_config.py** - Configuration system tests (7 tests)
- **test_detector.py** - Content type detection tests (8 tests)
- **test_llm.py** - LLM factory and provider tests (6 tests)
- **test_magic_loader.py** - MagicLoader unit tests (8 tests)

**Total: 29 tests** ✅

## Project Structure

```
src/
├── config.py             # Application configuration (AppConfig)
├── llm/                  # LLM provider module
│   ├── __init__.py       # Main exports
│   ├── types.py          # Type definitions (ModelId, Provider)
│   ├── factory.py        # LLM factory and provider detection
│   ├── anthropic.py      # Anthropic/Claude provider
│   └── openai.py         # OpenAI/GPT provider
└── content/
    ├── models.py         # Pydantic models for Content, Summary, Source
    └── loader/
        ├── base.py       # BaseLoader abstract class
        ├── magic.py      # MagicLoader implementation
        ├── detector.py   # Content type detection
        ├── summarizer.py # LLM-powered summarization
        └── wrappers/     # LangChain loader wrappers
            ├── web_loader.py
            ├── pdf_loader.py
            ├── youtube_loader.py
            └── text_loader.py

tests/
├── test_config.py        # Configuration tests
├── test_detector.py      # Detection tests
├── test_llm.py           # LLM module tests
└── test_magic_loader.py  # MagicLoader tests

examples/
└── demo.py              # Interactive demo script
```

## Configuration

The application uses a YAML-based configuration system. Edit `config.yaml` to customize settings:

```yaml
# config.yaml
models:
  summarization:
    model_id: claude-3-5-sonnet-20241022
    temperature: 0.3
    max_tokens: 4096
    timeout: 60.0

  # You can add more model configs for different tasks
  # analysis:
  #   model_id: gpt-4o
  #   temperature: 0.5
  #   max_tokens: 2048
  #   timeout: 30.0
```

You can also load custom config files programmatically:

```python
from pathlib import Path
from src.config import get_config, reload_config

# Load from custom path
config = get_config(Path("my_custom_config.yaml"))

# Get model config for a specific task
model_config = config.get_model_config("summarization")

# Create LLM for a specific task
llm = config.create_llm("summarization")

# Reload config after changes
config = reload_config()
```

### Supported Models

**Anthropic:**
- `claude-3-5-sonnet-20241022` (default)
- `claude-3-5-haiku-20241022`
- `claude-3-opus-20240229`

**OpenAI:**
- `gpt-4o`
- `gpt-4-turbo`
- `gpt-4o-mini`
- `gpt-3.5-turbo`

### Environment Variables

API keys are loaded automatically from a `.env` file in the project root:

```bash
# Copy the example file
cp .example.env .env

# Edit .env and add your key(s)
# ANTHROPIC_API_KEY=your_anthropic_key
# OPENAI_API_KEY=your_openai_key
```

Alternatively, you can still set them as environment variables:
```bash
export ANTHROPIC_API_KEY=your_anthropic_key
# OR
export OPENAI_API_KEY=your_openai_key
```

The system automatically detects which provider to use based on the model ID.

## Requirements

- Python 3.13+
- API key for your chosen LLM provider (Anthropic or OpenAI)

# Plan

- Summarize YT videos
    - Pull from playlist?
    - Exract the transcript
    - Exract core concepts
- Create quizzes to help with recall
    - Create a learning plan
    - Create a cron job schedule
    - Push quizzes
- Generate on a daily basis
    - Cron job to generate quizzes
    - Notify via email

# Research
- https://github.com/jimmc414/onefilellm
    - Extract multiple different sources into a single file
    - CLI/Python lib
