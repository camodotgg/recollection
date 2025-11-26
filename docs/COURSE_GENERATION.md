# Course Generation System

The course generation system automatically creates structured learning courses from content (web articles, PDFs, YouTube videos, etc.). It uses LLMs to analyze content, determine optimal lesson structure, and generate learning objectives based on the content's genre.

## Overview

The system consists of several key components:

1. **Content Merger**: Combines multiple content sources into a unified representation
2. **Genre Strategies**: Different approaches for different content types (tutorials, documentaries, news, analysis)
3. **Course Generator**: Main orchestrator that uses LLMs to create structured courses

## Quick Start

### Basic Usage

```python
from src.content.loader.magic import load
from src.course import generate_course
from src.config import get_config

# Load configuration
config = get_config()
analysis_llm = config.create_llm("summarization")
course_llm = config.create_llm("course_generation")

# Load content from a URL
content = load(analysis_llm, "https://realpython.com/python-decorators/")

# Generate course
course = generate_course(
    llm=course_llm,
    contents=[content],
)

# Save course to JSON
course.to_json_file("my_course.json")
```

### Using the Example Script

```bash
# Generate course from a URL
uv run python -m examples.generate_course_from_url

# Or use the sample content example
uv run python -m examples.test_course_generation
```

## Architecture

### Content Flow

```
URL/File → Magic Loader → Content → Analyzer → AnalyzedContent
                                                       ↓
                                    Course Generator ← Strategy
                                                       ↓
                                                    Course
                                                       ↓
                                              Lessons + Takeaways
```

### Genre Strategies

The system uses different strategies based on content genre:

#### Tutorial Strategy
- **Focus**: Step-by-step skill building
- **Lessons**: Progressive complexity, hands-on practice
- **Completion**: Requires demonstrating practical skills
- **Example Content**: Programming tutorials, how-to guides

#### Documentary Strategy
- **Focus**: Comprehension and retention
- **Lessons**: Organized around themes and narrative arcs
- **Completion**: Demonstrates understanding of key facts
- **Example Content**: Historical content, educational videos

#### News Strategy
- **Focus**: Current events understanding
- **Lessons**: Background → Analysis → Implications
- **Completion**: Understanding context and multiple perspectives
- **Example Content**: News articles, current events

#### Analysis Strategy
- **Focus**: Critical thinking and evaluation
- **Lessons**: Arguments → Evidence → Perspectives → Synthesis
- **Completion**: Demonstrates analytical skills
- **Example Content**: Opinion pieces, analytical essays, reviews

## Data Models

### Course

A complete learning program with metadata, lessons, and takeaways.

```python
class Course(BaseModel):
    id: str
    title: str
    description: str
    objective: str

    # Source content references
    source_content: Sequence[ContentReference]

    # Metadata
    genre: Genre
    topics: Sequence[Topic]
    difficulty_level: DifficultyLevel
    estimated_duration: timedelta

    # Structure
    lessons: Sequence[Lesson]
    takeaways: Sequence[Takeaway]

    # Completion
    completion_criteria: CompletionCriteria

    # Timestamps
    created_at: datetime
    updated_at: datetime
```

### Lesson

Individual learning unit within a course.

```python
class Lesson(BaseModel):
    id: str
    title: str
    description: str
    order: int

    # Learning objectives
    objectives: Sequence[str]
    prerequisites: Sequence[str]

    # Content
    content_sections: Sequence[ContentSection]
    activities: Sequence[Any]  # Activities added later

    # Completion
    completion_criteria: CompletionCriteria
    estimated_duration: timedelta
```

### Content Section

A discrete piece of learning material within a lesson.

```python
class ContentSection(BaseModel):
    id: str
    title: str
    body: str  # Markdown or rich text
    order: int
    type: ContentSectionType  # TEXT, CODE_EXAMPLE, etc.
    source_reference: Optional[ContentReference]
```

## Multi-Content Courses

You can generate courses from multiple related content sources:

```python
# Load multiple content sources
content1 = load(analysis_llm, "https://example.com/tutorial-part1")
content2 = load(analysis_llm, "https://example.com/tutorial-part2")

# Generate unified course
course = generate_course(
    llm=course_llm,
    contents=[content1, content2],
)
```

The merger will:
- Combine summaries from all sources
- Deduplicate topics
- Determine primary genre
- Maintain references to all source content

## Customization

### Using Different LLM Models

Configure different models in `config.yaml`:

```yaml
models:
  summarization:
    model_id: gpt-4o-mini
    temperature: 0.3
    max_tokens: 4096
    timeout: 60.0

  course_generation:
    model_id: gpt-4o-mini  # Or use claude-3-5-sonnet-20241022
    temperature: 0.7       # Higher for creativity
    max_tokens: 4096
    timeout: 90.0
```

### Pre-Analyzing Content

If you've already analyzed content, pass it to avoid re-analysis:

```python
from src.content.analysis.analyze import analyze

# Analyze content separately
analyzed = analyze(analysis_llm, content)

# Generate course with pre-analyzed content
course = generate_course(
    llm=course_llm,
    contents=[content],
    analyzed_contents=[analyzed],
)
```

### Custom Strategies

To create a custom strategy for a new genre:

```python
from src.course.strategies.base import CourseGenerationStrategy, LessonPlan
from src.content.models import Genre
from typing import List

class MyCustomStrategy(CourseGenerationStrategy):
    def __init__(self):
        super().__init__(Genre.CUSTOM)

    def get_lesson_structure_prompt(self, content_summary: str, topics: List[Topic]) -> str:
        # Return custom LLM prompt for lesson structure
        pass

    def get_takeaways_prompt(self, content_summary: str, topics: List[Topic], lesson_plans: List[LessonPlan]) -> str:
        # Return custom LLM prompt for takeaways
        pass

    def get_completion_criteria(self, total_lessons: int, estimated_duration: timedelta) -> CompletionCriteria:
        # Return custom completion criteria
        pass
```

## API Reference

### `generate_course()`

Main function for course generation.

```python
def generate_course(
    llm: BaseChatModel,
    contents: Sequence[Content],
    analyzed_contents: Optional[Sequence[AnalyzedContent]] = None,
    **kwargs,
) -> Course:
    """
    Generate a course from one or more Content objects.

    Args:
        llm: Language model for course generation
        contents: Sequence of Content objects to generate course from
        analyzed_contents: Optional pre-analyzed content (if None, will analyze)
        **kwargs: Additional options (e.g., course_id)

    Returns:
        Course object with structured lessons and learning materials
    """
```

### `merge_contents()`

Combine multiple content sources.

```python
def merge_contents(
    contents: Sequence[Content],
    analyzed_contents: Sequence[AnalyzedContent],
) -> MergedContent:
    """
    Merge multiple Content objects into a unified representation.

    Args:
        contents: Sequence of Content objects to merge
        analyzed_contents: Corresponding AnalyzedContent objects with genre/topics

    Returns:
        MergedContent object with combined information
    """
```

### `get_strategy_for_genre()`

Get the appropriate strategy for a content genre.

```python
def get_strategy_for_genre(genre: Genre) -> CourseGenerationStrategy:
    """
    Get the appropriate course generation strategy for a genre.

    Args:
        genre: The content genre

    Returns:
        CourseGenerationStrategy instance for the genre
    """
```

## Examples

### Example 1: Tutorial Course from Web Article

```python
from src.content.loader.magic import load
from src.course import generate_course
from src.config import get_config

config = get_config()
analysis_llm = config.create_llm("summarization")
course_llm = config.create_llm("course_generation")

# Load tutorial content
content = load(analysis_llm, "https://realpython.com/python-decorators/")

# Generate course
course = generate_course(course_llm, [content])

# Print lesson details
for lesson in course.lessons:
    print(f"\n{lesson.title}")
    print(f"Duration: {lesson.estimated_duration}")
    for obj in lesson.objectives:
        print(f"  • {obj}")
```

### Example 2: Multi-Part Course

```python
# Load multiple related tutorials
urls = [
    "https://example.com/python-basics-part1",
    "https://example.com/python-basics-part2",
    "https://example.com/python-basics-part3",
]

contents = [load(analysis_llm, url) for url in urls]

# Generate unified course
course = generate_course(course_llm, contents)
```

### Example 3: Save and Load Courses

```python
# Generate and save
course = generate_course(course_llm, [content])
course.to_json_file("courses/python_decorators.json")

# Load later
from src.course.models import Course
loaded_course = Course.from_json_file("courses/python_decorators.json")
```

## Future Enhancements

The current implementation creates course structure. Future additions will include:

1. **Activity Generation**: Quiz questions, challenges, and games generated during daily practice
2. **Progress Tracking**: Track learner progress through lessons and activities
3. **Adaptive Learning**: Adjust difficulty based on performance
4. **Daily Challenges**: Generate practice activities based on weak areas

## Troubleshooting

### LLM API Key Errors

Ensure your `.env` file has valid API keys:

```bash
# For OpenAI models (gpt-4o-mini, etc.)
OPENAI_API_KEY=sk-...

# For Anthropic models (claude-3-5-sonnet, etc.)
ANTHROPIC_API_KEY=sk-ant-...
```

### Import Errors

If you see import errors, ensure you're running from the project root:

```bash
# Run from project root
cd /path/to/recollection
uv run python -m examples.generate_course_from_url
```

### Content Loading Failures

Some websites may block automated access. Try different URLs or use PDF/YouTube content instead.

## Contributing

To add new genre strategies or improve existing ones:

1. Create new strategy class in `src/course/strategies/`
2. Update `get_strategy_for_genre()` mapping
3. Add tests and examples
4. Update documentation
