"""
Documentary content strategy for course generation.

Documentaries focus on comprehension, key facts, and narrative understanding.
Emphasizes retention of information and understanding of the full story.
"""
from typing import List
from datetime import timedelta

from src.content.models import Topic, Genre
from src.course.models import CompletionCriteria, CompletionCriteriaType
from .base import CourseGenerationStrategy, LessonPlan


class DocumentaryStrategy(CourseGenerationStrategy):
    """
    Strategy for generating courses from documentary content.

    Documentary courses emphasize:
    - Comprehension and understanding
    - Key facts and insights
    - Narrative flow and connections
    - Critical perspectives
    """

    def __init__(self):
        super().__init__(Genre.DOCUMENTARY)

    def get_lesson_structure_prompt(
        self, content_summary: str, topics: List[Topic]
    ) -> str:
        """Get LLM prompt for documentary lesson structure."""
        topics_str = ", ".join([t.name for t in topics])

        return f"""Analyze the following documentary content and determine the optimal lesson structure for learning.

Content Summary:
{content_summary}

Topics Covered: {topics_str}

Create a structured learning path that follows documentary comprehension best practices:
1. Organize lessons around key themes or narrative arcs
2. Each lesson should focus on a central idea or time period
3. Ensure lessons build understanding of the overall story
4. Balance lesson length (aim for 20-40 minute lessons)
5. Include comprehension-focused objectives

Return a JSON array of lessons with:
- title: Clear, engaging lesson title that captures the theme
- description: What this part of the story covers and its significance
- objectives: Understanding-focused objectives (what learner will UNDERSTAND/KNOW)
- topic_coverage: Which topics from the content are covered
- estimated_duration_minutes: How long the lesson should take (20-45 minutes)
- prerequisites: Titles of previous lessons needed for context

Focus on helping learners understand and retain the key information and narratives.

Example format:
```json
[
  {{
    "title": "The Origins of the Movement",
    "description": "Explore the historical context and early events that sparked the movement",
    "objectives": [
      "Understand the historical context",
      "Identify key figures and their motivations",
      "Recognize the catalyzing events"
    ],
    "topic_coverage": ["Historical Background", "Key Figures"],
    "estimated_duration_minutes": 30,
    "prerequisites": []
  }},
  {{
    "title": "Turning Points and Conflicts",
    "description": "Examine the critical moments that shaped the movement's trajectory",
    "objectives": [
      "Analyze major turning points",
      "Understand the conflicts and opposition",
      "Connect events to broader consequences"
    ],
    "topic_coverage": ["Major Events", "Opposition"],
    "estimated_duration_minutes": 35,
    "prerequisites": ["The Origins of the Movement"]
  }}
]
```

Return ONLY the JSON array, no other text."""

    def get_takeaways_prompt(
        self, content_summary: str, topics: List[Topic], lesson_plans: List[LessonPlan]
    ) -> str:
        """Get LLM prompt for documentary takeaways."""
        topics_str = ", ".join([t.name for t in topics])
        lessons_str = "\n".join([f"- {lp.title}" for lp in lesson_plans])

        return f"""Based on this documentary course content, identify 3-5 key takeaways.

Content: {content_summary[:500]}...

Topics: {topics_str}

Lessons:
{lessons_str}

For each takeaway, focus on UNDERSTANDING and INSIGHTS the learner will gain:
- name: Concise name (3-5 words) capturing the insight
- description: What the learner will understand about the topic
- criteria: How to verify this understanding (e.g., "Can explain X and its significance")

Focus on deep comprehension and meaningful insights.

Example format:
```json
[
  {{
    "name": "Historical Impact",
    "description": "Understand how the events shaped modern society and continue to influence current issues",
    "criteria": "Can explain the historical impact and draw connections to contemporary events"
  }},
  {{
    "name": "Multiple Perspectives",
    "description": "Recognize and analyze different viewpoints and their underlying motivations",
    "criteria": "Can articulate various perspectives and explain why different groups held different views"
  }}
]
```

Return ONLY the JSON array, no other text."""

    def get_completion_criteria(
        self, total_lessons: int, estimated_duration: timedelta
    ) -> CompletionCriteria:
        """
        Documentary completion focuses on comprehension and retention.

        Learners should demonstrate understanding of key concepts and narratives.
        """
        return CompletionCriteria(
            type=CompletionCriteriaType.CUSTOM,
            custom_rules=(
                f"Complete all {total_lessons} lessons and demonstrate comprehension "
                "of key facts, themes, and narratives. Assessment activities will test "
                "understanding and retention."
            ),
            genre_specific_requirements={
                "comprehension_focused": True,
                "retention_important": True,
                "narrative_understanding": True,
            },
        )

    def get_lesson_completion_criteria(
        self, lesson_plan: LessonPlan
    ) -> CompletionCriteria:
        """Documentary lessons require reviewing content and demonstrating comprehension."""
        return CompletionCriteria(
            type=CompletionCriteriaType.CUSTOM,
            custom_rules=(
                f"Review all content sections and demonstrate understanding of: {lesson_plan.title}"
            ),
            genre_specific_requirements={
                "comprehension_check": True,
            },
        )
