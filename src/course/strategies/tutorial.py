"""
Tutorial content strategy for course generation.

Tutorials focus on step-by-step learning with building complexity.
Emphasizes hands-on practice and progressive skill development.
"""
from typing import List
from datetime import timedelta

from src.content.models import Topic, Genre
from src.course.models import CompletionCriteria, CompletionCriteriaType
from .base import CourseGenerationStrategy, LessonPlan


class TutorialStrategy(CourseGenerationStrategy):
    """
    Strategy for generating courses from tutorial content.

    Tutorial courses emphasize:
    - Step-by-step progression
    - Building complexity
    - Practical examples and exercises
    - Clear prerequisites and dependencies
    """

    def __init__(self):
        super().__init__(Genre.TUTORIAL)

    def get_lesson_structure_prompt(
        self, content_summary: str, topics: List[Topic]
    ) -> str:
        """Get LLM prompt for tutorial lesson structure."""
        topics_str = ", ".join([t.name for t in topics])

        return f"""Analyze the following tutorial content and determine the optimal lesson structure for learning.

Content Summary:
{content_summary}

Topics Covered: {topics_str}

Create a structured learning path that follows tutorial best practices:
1. Start with foundational concepts and prerequisites
2. Build complexity progressively through lessons
3. Each lesson should focus on a specific skill or concept
4. Ensure clear dependencies between lessons
5. Balance lesson length (aim for 15-30 minute lessons)
6. Include practical, hands-on objectives

Return a JSON array of lessons with:
- title: Clear, action-oriented lesson title (e.g., "Building Your First Component")
- description: What the lesson covers and why it matters
- objectives: Specific learning objectives (what learner will be able to DO after this lesson)
- topic_coverage: Which topics from the content are covered
- estimated_duration_minutes: How long the lesson should take (15-45 minutes)
- prerequisites: Titles of previous lessons needed (empty array for first lesson)

Be thoughtful about breaking content into digestible, buildable units where each lesson
prepares the learner for the next.

Example format:
```json
[
  {{
    "title": "Setting Up Your Development Environment",
    "description": "Learn how to install and configure the necessary tools for development",
    "objectives": [
      "Install required software",
      "Configure development environment",
      "Verify setup with a hello world example"
    ],
    "topic_coverage": ["Installation", "Configuration"],
    "estimated_duration_minutes": 20,
    "prerequisites": []
  }},
  {{
    "title": "Understanding Basic Concepts",
    "description": "Master the fundamental concepts that underpin the technology",
    "objectives": [
      "Explain core terminology",
      "Identify key components",
      "Apply basic patterns"
    ],
    "topic_coverage": ["Fundamentals", "Core Concepts"],
    "estimated_duration_minutes": 25,
    "prerequisites": ["Setting Up Your Development Environment"]
  }}
]
```

Return ONLY the JSON array, no other text."""

    def get_takeaways_prompt(
        self, content_summary: str, topics: List[Topic], lesson_plans: List[LessonPlan]
    ) -> str:
        """Get LLM prompt for tutorial takeaways."""
        topics_str = ", ".join([t.name for t in topics])
        lessons_str = "\n".join([f"- {lp.title}" for lp in lesson_plans])

        return f"""Based on this tutorial course content, identify 3-5 key takeaways.

Content: {content_summary[:500]}...

Topics: {topics_str}

Lessons:
{lessons_str}

For each takeaway, focus on PRACTICAL SKILLS the learner will gain:
- name: Concise name (3-5 words) describing the skill
- description: What the learner will be able to do
- criteria: How to verify this skill was learned (e.g., "Can build X without guidance")

Focus on concrete, measurable outcomes that demonstrate practical mastery.

Example format:
```json
[
  {{
    "name": "Build REST APIs",
    "description": "Create functional REST APIs with proper routing, error handling, and data validation",
    "criteria": "Successfully build a CRUD API from scratch without reference materials"
  }},
  {{
    "name": "Test Applications",
    "description": "Write comprehensive unit and integration tests for code",
    "criteria": "Achieve 80%+ test coverage on a new feature"
  }}
]
```

Return ONLY the JSON array, no other text."""

    def get_completion_criteria(
        self, total_lessons: int, estimated_duration: timedelta
    ) -> CompletionCriteria:
        """
        Tutorial completion requires demonstrating practical skills.

        Learners should complete activities to show they can apply concepts.
        """
        return CompletionCriteria(
            type=CompletionCriteriaType.CUSTOM,
            custom_rules=(
                f"Complete all {total_lessons} lessons and demonstrate practical skills "
                "through activities. Activities will be generated based on performance "
                "during daily challenges."
            ),
            genre_specific_requirements={
                "requires_practice": True,
                "activity_focused": True,
                "skill_demonstration": True,
            },
        )

    def get_lesson_completion_criteria(
        self, lesson_plan: LessonPlan
    ) -> CompletionCriteria:
        """Tutorial lessons require reviewing content and completing activities."""
        return CompletionCriteria(
            type=CompletionCriteriaType.CUSTOM,
            custom_rules=(
                f"Review all content sections and complete practice activities for: {lesson_plan.title}"
            ),
            genre_specific_requirements={
                "requires_practice": True,
            },
        )
