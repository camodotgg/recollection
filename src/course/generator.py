"""
Course generator for creating structured courses from analyzed content.

This module provides the main course generation functionality, using LLMs to determine
optimal lesson structure and generate learning materials from Content objects.
"""
import uuid
from typing import Sequence, Optional, List
from datetime import datetime, timedelta

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import SystemMessage, HumanMessage

from src.content.models import Content, Genre, AnalyzedContent
from src.content.analysis.analyze import analyze
from src.course.models import (
    Course,
    Lesson,
    ContentSection,
    ContentReference,
    Takeaway,
    CompletionCriteria,
    DifficultyLevel,
    ContentSectionType,
)
from src.course.merger import merge_contents, MergedContent
from src.course.strategies import get_strategy_for_genre, LessonPlan


def generate_course(
    llm: BaseChatModel,
    contents: Sequence[Content],
    analyzed_contents: Optional[Sequence[AnalyzedContent]] = None,
    **kwargs,
) -> Course:
    """
    Generate a course from one or more Content objects.

    This function:
    1. Analyzes content if not already analyzed
    2. Merges multiple content sources
    3. Uses LLM to determine optimal lesson structure
    4. Generates lessons with content sections
    5. Extracts course takeaways
    6. Sets completion criteria

    Args:
        llm: Language model for course generation
        contents: Sequence of Content objects to generate course from
        analyzed_contents: Optional pre-analyzed content (if None, will analyze)
        **kwargs: Additional options for course generation

    Returns:
        Course object with structured lessons and learning materials

    Raises:
        ValueError: If contents sequence is empty

    Example:
        >>> from src.config import get_config
        >>> config = get_config()
        >>> course_llm = config.create_llm("course_generation")
        >>> content = Content.from_json_file("tutorial.json")
        >>> course = generate_course(course_llm, [content])
        >>> print(f"Course: {course.title} with {len(course.lessons)} lessons")
    """
    if not contents:
        raise ValueError("Cannot generate course from empty sequence of contents")

    # Step 1: Analyze content if not provided
    if analyzed_contents is None:
        analyzed_contents = [analyze(llm, content) for content in contents]

    # Validate that we have matching analyzed content
    if len(analyzed_contents) != len(contents):
        raise ValueError(
            f"Number of analyzed contents ({len(analyzed_contents)}) must match "
            f"number of contents ({len(contents)})"
        )

    # Step 2: Merge multiple contents
    merged = merge_contents(contents, analyzed_contents)

    # Step 3: Get appropriate strategy for the genre
    strategy = get_strategy_for_genre(merged.primary_genre)

    # Step 4: Determine course metadata
    course_metadata = _determine_course_metadata(merged, analyzed_contents)

    # Step 5: Generate lesson structure using LLM
    lesson_plans = _generate_lesson_structure(llm, strategy, merged)

    # Step 6: Generate lesson content
    lessons = _generate_lessons(merged, lesson_plans, strategy)

    # Step 7: Generate course takeaways using LLM
    takeaways = _generate_takeaways(llm, strategy, merged, lesson_plans)

    # Step 8: Set completion criteria
    total_duration = sum(
        (lesson.estimated_duration for lesson in lessons), timedelta()
    )
    completion_criteria = strategy.get_completion_criteria(
        total_lessons=len(lessons),
        estimated_duration=total_duration,
    )

    # Step 9: Create Course object
    course_id = kwargs.get("course_id", str(uuid.uuid4()))
    now = datetime.now()

    return Course(
        id=course_id,
        title=course_metadata["title"],
        description=course_metadata["description"],
        objective=course_metadata["objective"],
        source_content=merged.source_references,
        genre=merged.primary_genre,
        topics=merged.topics,
        difficulty_level=course_metadata["difficulty_level"],
        estimated_duration=total_duration,
        lessons=lessons,
        takeaways=takeaways,
        completion_criteria=completion_criteria,
        created_at=now,
        updated_at=now,
    )


def _determine_course_metadata(
    merged: MergedContent,
    analyzed_contents: Sequence[AnalyzedContent],
) -> dict:
    """
    Determine course metadata from merged content.

    Args:
        merged: Merged content
        analyzed_contents: Analyzed content objects

    Returns:
        Dictionary with title, description, objective, difficulty_level
    """
    # Use first content's title as base, or generate generic title
    if merged.contents:
        base_title = merged.contents[0].source.title or "Untitled Content"
    else:
        base_title = "Course"

    # Generate title based on number of sources
    if len(merged.contents) == 1:
        title = f"Course: {base_title}"
    else:
        title = f"Course: {base_title} and {len(merged.contents) - 1} more"

    # Generate description from topics
    topic_names = [t.name for t in merged.topics[:5]]  # Top 5 topics
    topics_str = ", ".join(topic_names)

    description = (
        f"A comprehensive course covering {topics_str} "
        f"based on {len(merged.contents)} content source(s)."
    )

    # Generate objective
    objective = f"Master the concepts and skills related to {topics_str}"

    # Determine difficulty level (simplified - could be enhanced)
    # For now, default to INTERMEDIATE
    difficulty_level = DifficultyLevel.INTERMEDIATE

    return {
        "title": title,
        "description": description,
        "objective": objective,
        "difficulty_level": difficulty_level,
    }


def _generate_lesson_structure(
    llm: BaseChatModel,
    strategy,
    merged: MergedContent,
) -> List[LessonPlan]:
    """
    Use LLM to generate lesson structure.

    Args:
        llm: Language model
        strategy: Course generation strategy
        merged: Merged content

    Returns:
        List of LessonPlan objects
    """
    # Get strategy-specific prompt
    prompt = strategy.get_lesson_structure_prompt(
        content_summary=merged.combined_summary,
        topics=list(merged.topics),
    )

    # Call LLM
    messages = [
        SystemMessage(content="You are an expert course designer and educator."),
        HumanMessage(content=prompt),
    ]

    response = llm.invoke(messages)
    response_text = response.content

    # Parse response into LessonPlan objects
    lesson_plans = strategy.parse_lesson_structure_response(response_text)

    return lesson_plans


def _generate_lessons(
    merged: MergedContent,
    lesson_plans: List[LessonPlan],
    strategy,
) -> List[Lesson]:
    """
    Generate full Lesson objects from lesson plans.

    Args:
        merged: Merged content
        lesson_plans: Planned lesson structure
        strategy: Course generation strategy

    Returns:
        List of Lesson objects
    """
    lessons = []

    for i, plan in enumerate(lesson_plans):
        # Create content sections for this lesson
        content_sections = _create_content_sections(merged, plan, i)

        # Get lesson completion criteria
        completion_criteria = strategy.get_lesson_completion_criteria(plan)

        # Create lesson
        lesson = Lesson(
            id=str(uuid.uuid4()),
            title=plan.title,
            description=plan.description,
            order=i,
            objectives=plan.objectives,
            prerequisites=plan.prerequisites,
            content_sections=content_sections,
            activities=[],  # Activities generated later during daily challenges
            completion_criteria=completion_criteria,
            estimated_duration=timedelta(minutes=plan.estimated_duration_minutes),
        )

        lessons.append(lesson)

    return lessons


def _create_content_sections(
    merged: MergedContent,
    lesson_plan: LessonPlan,
    lesson_index: int,
) -> List[ContentSection]:
    """
    Create content sections for a lesson.

    Extracts relevant portions of the merged content for this lesson.

    Args:
        merged: Merged content
        lesson_plan: Planned lesson
        lesson_index: Index of this lesson in course

    Returns:
        List of ContentSection objects
    """
    sections = []

    # Create a main content section with the lesson's portion of content
    # In a more sophisticated implementation, this would extract specific
    # relevant portions based on topic_coverage
    section = ContentSection(
        id=str(uuid.uuid4()),
        title=f"{lesson_plan.title} - Content",
        body=_extract_relevant_content(merged, lesson_plan),
        order=0,
        type=ContentSectionType.TEXT,
        source_reference=merged.source_references[0] if merged.source_references else None,
    )

    sections.append(section)

    # Add objectives as a key points section
    objectives_body = "\n".join([f"- {obj}" for obj in lesson_plan.objectives])
    objectives_section = ContentSection(
        id=str(uuid.uuid4()),
        title="Learning Objectives",
        body=objectives_body,
        order=1,
        type=ContentSectionType.KEY_POINT,
    )

    sections.append(objectives_section)

    return sections


def _extract_relevant_content(
    merged: MergedContent,
    lesson_plan: LessonPlan,
) -> str:
    """
    Extract relevant content for a lesson based on topic coverage.

    This is a simplified implementation that returns a portion of the summary.
    A more sophisticated version would use semantic search or LLM to extract
    the most relevant sections.

    Args:
        merged: Merged content
        lesson_plan: Planned lesson

    Returns:
        Extracted content text
    """
    # For now, return a portion of the combined summary
    # In production, this should intelligently extract relevant sections
    # based on lesson_plan.topic_coverage

    # Simple heuristic: include description and mention topics
    topics_str = ", ".join(lesson_plan.topic_coverage)

    content = f"""## {lesson_plan.title}

{lesson_plan.description}

### Topics Covered
{topics_str}

### Content
This lesson covers material from the source content related to: {topics_str}.

{merged.combined_summary[:1000]}...

*Note: Full content sections will be populated with relevant excerpts from source materials.*
"""

    return content


def _generate_takeaways(
    llm: BaseChatModel,
    strategy,
    merged: MergedContent,
    lesson_plans: List[LessonPlan],
) -> List[Takeaway]:
    """
    Use LLM to generate course takeaways.

    Args:
        llm: Language model
        strategy: Course generation strategy
        merged: Merged content
        lesson_plans: Planned lessons

    Returns:
        List of Takeaway objects
    """
    # Get strategy-specific prompt
    prompt = strategy.get_takeaways_prompt(
        content_summary=merged.combined_summary,
        topics=list(merged.topics),
        lesson_plans=lesson_plans,
    )

    # Call LLM
    messages = [
        SystemMessage(content="You are an expert educator identifying key learning outcomes."),
        HumanMessage(content=prompt),
    ]

    response = llm.invoke(messages)
    response_text = response.content

    # Parse response
    takeaway_dicts = strategy.parse_takeaways_response(response_text)

    # Convert to Takeaway objects
    takeaways = [Takeaway(**data) for data in takeaway_dicts]

    return takeaways
