<h1 align="center">
  recollection
</h1>

<div align="center">
  <h3>
    Transform any content into structured learning courses. <br/>
    Automatically analyze and generate personalized lessons from web articles, PDFs, and videos.
  </h3>
</div>

<br />

<p align="center">
  <a href="https://github.com/camo/recollection/blob/main/LICENSE">
    <img alt="MIT license" src="https://img.shields.io/badge/license-MIT-blue.svg" />
  </a>
  <a href="https://python.org">
    <img alt="Python 3.13+" src="https://img.shields.io/badge/python-3.13+-blue.svg" />
  </a>
</p>

## Features

**Content Loading:**
- 🌐 **Web URLs** - Articles, blog posts, documentation
- 📄 **PDF Documents** - Local files and remote URLs
- 🎥 **YouTube Videos** - Automatic transcript extraction
- 📝 **Text Files** - Markdown and plain text support

**Course Generation:**
- 🎯 **Smart Lesson Design** - LLM analyzes content and creates optimal lesson structure
- 📚 **Genre-Aware Strategies** - Different approaches for tutorials, documentaries, news, and analysis
- ✅ **Learning Objectives** - Clear, actionable goals for each lesson
- 🎓 **Key Takeaways** - Essential insights and skills to master
- 🔗 **Source Traceability** - Links back to original content
- 📊 **Multi-Content Support** - Combine multiple sources into unified courses

## Quick Start

```bash
# Install dependencies
uv sync

# Set up API keys
cp .example.env .env
# Edit .env and add your OPENAI_API_KEY or ANTHROPIC_API_KEY

# Launch the interactive TUI app 🎨
uv run python examples/app.py
```

**The TUI provides a beautiful interactive interface for:**
- 📥 Loading content from URLs
- 🎓 Generating courses with AI
- 📖 Viewing and managing courses
- 💾 Saving/loading courses

## Usage

```python
from src.content.loader.magic import load
from src.course import generate_course
from src.config import get_config

# Load configuration
config = get_config()
analysis_llm = config.create_llm("summarization")
course_llm = config.create_llm("course_generation")

# Load content
content = load(analysis_llm, "https://realpython.com/python-decorators/")

# Generate course
course = generate_course(llm=course_llm, contents=[content])

# Save course
course.to_json_file("my_course.json")
```

## Documentation

For detailed information, see [Course Generation Guide](docs/COURSE_GENERATION.md)

## Configuration

Configure models in `config.yaml`:

```yaml
models:
  summarization:
    model_id: gpt-4o-mini
    temperature: 0.3
    max_tokens: 4096
    timeout: 60.0

  course_generation:
    model_id: gpt-4o-mini
    temperature: 0.7
    max_tokens: 4096
    timeout: 90.0
```

**Supported Models:**
- **Anthropic:** `claude-3-5-sonnet-20241022`, `claude-3-5-haiku-20241022`
- **OpenAI:** `gpt-4o`, `gpt-4o-mini`, `gpt-3.5-turbo`

## How It Works

1. **Load Content** - Automatically detect and load from various sources
2. **Analyze** - LLM classifies genre and extracts key topics
3. **Generate** - Strategy pattern creates optimal lesson structure
4. **Structure** - Organize into lessons with objectives and takeaways

## Examples

```bash
# Interactive TUI app (recommended) 🎨
uv run python examples/app.py

# Command-line examples
uv run python examples/demo.py https://example.com/article
uv run python -m examples.test_course_generation
uv run python -m examples.generate_course_from_url
```

## Project Structure

```
src/
├── content/          # Content loading and analysis
│   ├── loader/       # Magic loader with auto-detection
│   └── analysis/     # Genre classification and topics
├── course/           # Course generation system
│   ├── generator.py  # Main course generation
│   ├── merger.py     # Multi-content merging
│   └── strategies/   # Genre-specific strategies
└── config.py         # Configuration management

examples/
├── app.py            # 🎨 Interactive TUI application
├── demo.py           # Content loading demo
├── test_course_generation.py
└── generate_course_from_url.py
```

## Requirements

- Python 3.13+
- API key for Anthropic or OpenAI

## What's Next

- 🎯 **Activity Generation** - Quizzes, challenges, and games
- 📊 **Progress Tracking** - Monitor learner progress
- 🔄 **Daily Challenges** - Automated practice generation
- 🤖 **Adaptive Learning** - Adjust difficulty based on performance

## Contributing

Contributions welcome! Please feel free to submit issues and pull requests.

## License

MIT License - see [LICENSE](LICENSE) for details
