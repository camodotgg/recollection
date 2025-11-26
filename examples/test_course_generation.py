"""
Example script demonstrating course generation from content.

This script shows how to:
1. Load or create content
2. Generate a course using the course generation system
3. Save the generated course to JSON
"""
from pathlib import Path

from src.content.models import Content, Source, Summary, Section, Format
from src.content.loader.magic import load
from src.course import generate_course
from src.config import get_config


def main():
    """Generate a course from example content."""
    print("=" * 60)
    print("Course Generation Example")
    print("=" * 60)

    # Load configuration
    config = get_config()

    # Create LLMs
    # Use summarization LLM for content analysis
    analysis_llm = config.create_llm("summarization")
    # Use course_generation LLM for course creation
    course_llm = config.create_llm("course_generation")

    print("\n1. Loading content...")

    # Option 1: Load from a URL (e.g., tutorial article)
    # Uncomment to use a real URL:
    # url = "https://realpython.com/python-decorators/"
    # content = load(analysis_llm, url)

    # Option 2: Create sample content manually for demonstration
    content = _create_sample_content()

    print(f"   ✓ Loaded: {content.source.link}")
    print(f"   Content length: {len(content.raw)} characters")

    # Save content for reference
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)

    content_file = output_dir / "sample_content.json"
    content.to_json_file(content_file)
    print(f"   ✓ Saved content to: {content_file}")

    print("\n2. Generating course...")
    print("   This will:")
    print("   - Analyze the content (genre, topics)")
    print("   - Use LLM to determine optimal lesson structure")
    print("   - Generate lessons with objectives and content")
    print("   - Extract key takeaways")

    # Generate course (this will analyze content automatically if needed)
    course = generate_course(
        llm=course_llm,
        contents=[content],
    )

    print(f"\n   ✓ Course generated: {course.title}")
    print(f"   Genre: {course.genre}")
    print(f"   Lessons: {len(course.lessons)}")
    print(f"   Topics: {', '.join([t.name for t in course.topics[:5]])}")
    print(f"   Estimated duration: {course.estimated_duration}")

    # Display lesson details
    print("\n3. Lesson breakdown:")
    for i, lesson in enumerate(course.lessons, 1):
        print(f"\n   Lesson {i}: {lesson.title}")
        print(f"   - Duration: {lesson.estimated_duration}")
        print(f"   - Objectives:")
        for obj in lesson.objectives:
            print(f"     • {obj}")

    # Display takeaways
    print("\n4. Course takeaways:")
    for i, takeaway in enumerate(course.takeaways, 1):
        print(f"\n   {i}. {takeaway.name}")
        print(f"      {takeaway.description}")

    # Save course
    course_file = output_dir / "generated_course.json"
    course.to_json_file(course_file)
    print(f"\n5. Course saved to: {course_file}")

    # Test loading it back
    from src.course.models import Course as CourseModel
    loaded_course = CourseModel.from_json_file(course_file)
    print(f"   ✓ Verified: Course can be loaded from JSON")

    print("\n" + "=" * 60)
    print("Course generation complete!")
    print("=" * 60)


def _create_sample_content() -> Content:
    """
    Create sample content for demonstration.

    In production, you would use load() to load from URLs, files, etc.
    This creates a minimal Content object for testing.
    """
    from datetime import datetime

    # Sample tutorial content about Python decorators
    sample_text = """
Python Decorators: A Complete Guide

Introduction
Decorators are a powerful feature in Python that allow you to modify or enhance
functions and classes without directly changing their source code. They are
commonly used for logging, access control, memoization, and more.

What are Decorators?
A decorator is a function that takes another function as an argument and returns
a new function that usually extends or modifies the behavior of the original function.

Basic Decorator Syntax
You can create decorators using the @ syntax. The decorator wraps the function.

Decorators with Arguments
You can create decorators that accept arguments by adding another layer of nesting.

Common Use Cases
- Timing Functions: Measure execution time of functions
- Logging: Automatically log function calls and returns
- Authentication: Check user permissions before executing functions
- Caching/Memoization: Store and reuse expensive computation results

Best Practices
- Use functools.wraps to preserve function metadata
- Keep decorators simple and focused
- Consider using classes for complex decorators
- Document decorator behavior clearly

Conclusion
Decorators are an essential tool in Python programming. They enable clean,
reusable code and are fundamental to many Python frameworks and libraries.
"""

    # Create Summary structure
    summary = Summary(
        abstract=Section(
            heading="Abstract",
            body="Learn about Python decorators, a powerful feature for modifying function behavior."
        ),
        introduction=Section(
            heading="Introduction",
            body="Decorators allow you to modify or enhance functions and classes without changing their source code."
        ),
        chapters=[
            Section(
                heading="Basic Decorators",
                body="Understanding the basic syntax and structure of Python decorators."
            ),
            Section(
                heading="Advanced Decorators",
                body="Creating decorators with arguments and using them effectively."
            ),
            Section(
                heading="Common Use Cases",
                body="Practical applications including timing, logging, authentication, and caching."
            ),
            Section(
                heading="Best Practices",
                body="Guidelines for writing clean, maintainable decorator code."
            ),
        ],
        conclusion=Section(
            heading="Conclusion",
            body="Decorators are essential tools that enable clean, reusable code in Python."
        ),
    )

    source = Source(
        author="Tutorial Author",
        origin="Web",
        link="https://example.com/python-decorators-guide",
        created_at=datetime.now(),
        format=Format.WEB,
    )

    content = Content(
        summary=summary,
        raw=sample_text,
        source=source,
        metadata={
            "title": "Python Decorators: A Complete Guide",
            "description": "A comprehensive guide to Python decorators",
        },
    )

    return content


if __name__ == "__main__":
    main()
