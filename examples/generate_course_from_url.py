"""
Generate a course from a real URL.

This example demonstrates loading content from a web URL and generating
a structured course with lessons, objectives, and takeaways.
"""
from pathlib import Path

from src.content.loader.magic import load
from src.course import generate_course
from src.config import get_config


def main():
    """Generate a course from a web URL."""
    # Example URLs you can use:
    # - Tutorial: "https://realpython.com/python-decorators/"
    # - Tutorial: "https://docs.python.org/3/tutorial/introduction.html"
    # - Article: Any web article URL

    url = input("Enter a URL to generate a course from: ").strip()

    if not url:
        print("No URL provided. Exiting.")
        return

    print("\n" + "=" * 70)
    print("Course Generation from URL")
    print("=" * 70)

    # Load configuration
    config = get_config()

    # Create LLMs
    analysis_llm = config.create_llm("summarization")
    course_llm = config.create_llm("course_generation")

    print(f"\n1. Loading content from URL...")
    print(f"   URL: {url}")

    try:
        # Load content using the magic loader
        # This will automatically:
        # - Detect content type (web, PDF, YouTube, etc.)
        # - Load the content
        # - Generate a summary using LLM
        content = load(analysis_llm, url)

        print(f"   ✓ Content loaded successfully")
        print(f"   Author: {content.source.author}")
        print(f"   Origin: {content.source.origin}")
        print(f"   Format: {content.source.format.value}")
        print(f"   Content length: {len(content.raw)} characters")

    except Exception as e:
        print(f"   ✗ Error loading content: {e}")
        return

    # Save the loaded content
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)

    content_file = output_dir / "loaded_content.json"
    content.to_json_file(content_file)
    print(f"   ✓ Content saved to: {content_file}")

    print("\n2. Generating course...")
    print("   This may take a minute as the LLM analyzes content and designs lessons...")

    try:
        # Generate course
        # This will:
        # - Analyze content to determine genre and extract topics
        # - Select appropriate strategy based on genre
        # - Use LLM to design optimal lesson structure
        # - Generate lessons with objectives and content sections
        # - Extract key takeaways
        course = generate_course(
            llm=course_llm,
            contents=[content],
        )

        print(f"\n   ✓ Course generated successfully!")

    except Exception as e:
        print(f"   ✗ Error generating course: {e}")
        import traceback
        traceback.print_exc()
        return

    # Display course details
    print("\n" + "=" * 70)
    print("COURSE DETAILS")
    print("=" * 70)

    print(f"\nTitle: {course.title}")
    print(f"Genre: {course.genre.value}")
    print(f"Difficulty: {course.difficulty_level.value}")
    print(f"Estimated Duration: {course.estimated_duration}")
    print(f"\nDescription:")
    print(f"  {course.description}")
    print(f"\nObjective:")
    print(f"  {course.objective}")

    # Display topics
    print(f"\nTopics Covered ({len(course.topics)}):")
    for i, topic in enumerate(course.topics, 1):
        print(f"  {i}. {topic.name}")
        if topic.description:
            print(f"     {topic.description}")

    # Display lessons
    print(f"\nLessons ({len(course.lessons)}):")
    print("-" * 70)
    for i, lesson in enumerate(course.lessons, 1):
        print(f"\nLesson {i}: {lesson.title}")
        print(f"Duration: {lesson.estimated_duration}")
        print(f"Description: {lesson.description}")

        print(f"\nObjectives:")
        for obj in lesson.objectives:
            print(f"  • {obj}")

        if lesson.prerequisites:
            print(f"\nPrerequisites:")
            for prereq in lesson.prerequisites:
                print(f"  • {prereq}")

        print(f"\nContent Sections: {len(lesson.content_sections)}")
        for section in lesson.content_sections:
            print(f"  • {section.title} ({section.type.value})")

    # Display takeaways
    print("\n" + "=" * 70)
    print("KEY TAKEAWAYS")
    print("=" * 70)
    for i, takeaway in enumerate(course.takeaways, 1):
        print(f"\n{i}. {takeaway.name}")
        print(f"   {takeaway.description}")
        print(f"   Criteria: {takeaway.criteria}")

    # Save course
    course_file = output_dir / "generated_course.json"
    course.to_json_file(course_file)

    print("\n" + "=" * 70)
    print(f"✓ Course saved to: {course_file}")
    print("=" * 70)

    # Summary statistics
    total_objectives = sum(len(lesson.objectives) for lesson in course.lessons)
    total_sections = sum(len(lesson.content_sections) for lesson in course.lessons)

    print(f"\nCourse Statistics:")
    print(f"  • Lessons: {len(course.lessons)}")
    print(f"  • Total Objectives: {total_objectives}")
    print(f"  • Total Content Sections: {total_sections}")
    print(f"  • Key Takeaways: {len(course.takeaways)}")
    print(f"  • Estimated Completion Time: {course.estimated_duration}")

    print("\n✅ Course generation complete!")


if __name__ == "__main__":
    main()
