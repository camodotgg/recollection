"""
News/commentary content strategy for course generation.

News content focuses on current events understanding, context, and analysis.
Emphasizes staying informed and understanding implications.
"""
from typing import List
from datetime import timedelta

from src.content.models import Topic, Genre
from src.course.models import CompletionCriteria, CompletionCriteriaType
from .base import CourseGenerationStrategy, LessonPlan


class NewsStrategy(CourseGenerationStrategy):
    """
    Strategy for generating courses from news and commentary content.

    News courses emphasize:
    - Current events understanding
    - Background context and history
    - Multiple perspectives and analysis
    - Implications and future outlook
    """

    def __init__(self):
        super().__init__(Genre.NEWS)

    def get_lesson_structure_prompt(
        self, content_summary: str, topics: List[Topic]
    ) -> str:
        """Get LLM prompt for news lesson structure."""
        topics_str = ", ".join([t.name for t in topics])

        return f"""Analyze the following news/commentary content and determine the optimal lesson structure for learning.

Content Summary:
{content_summary}

Topics Covered: {topics_str}

Create a structured learning path that follows news comprehension best practices:
1. Start with background context and "what happened"
2. Progress to analysis and "why it matters"
3. Explore different perspectives and implications
4. Each lesson should focus on a specific aspect or angle
5. Balance lesson length (aim for 15-30 minute lessons)
6. Include current-events focused objectives

Return a JSON array of lessons with:
- title: Clear, informative lesson title
- description: What aspect of the news/event this covers
- objectives: Understanding-focused objectives (what learner will KNOW/UNDERSTAND)
- topic_coverage: Which topics from the content are covered
- estimated_duration_minutes: How long the lesson should take (15-35 minutes)
- prerequisites: Titles of previous lessons needed for context

Focus on helping learners understand not just what happened, but why it matters and
what it means for different stakeholders.

Example format:
```json
[
  {{
    "title": "The Event: What Happened and When",
    "description": "Understand the key facts, timeline, and main developments of the event",
    "objectives": [
      "Recall the key facts and timeline",
      "Identify the main stakeholders involved",
      "Understand the immediate impact"
    ],
    "topic_coverage": ["Event Timeline", "Key Players"],
    "estimated_duration_minutes": 20,
    "prerequisites": []
  }},
  {{
    "title": "Historical Context and Background",
    "description": "Explore the historical events and trends that led to this situation",
    "objectives": [
      "Connect current events to historical precedents",
      "Understand underlying causes",
      "Recognize long-term trends"
    ],
    "topic_coverage": ["Historical Background", "Root Causes"],
    "estimated_duration_minutes": 25,
    "prerequisites": ["The Event: What Happened and When"]
  }},
  {{
    "title": "Analysis: Why It Matters",
    "description": "Examine the significance and implications of these developments",
    "objectives": [
      "Analyze the broader implications",
      "Understand different perspectives",
      "Evaluate potential outcomes"
    ],
    "topic_coverage": ["Analysis", "Implications"],
    "estimated_duration_minutes": 30,
    "prerequisites": ["The Event: What Happened and When", "Historical Context and Background"]
  }}
]
```

Return ONLY the JSON array, no other text."""

    def get_takeaways_prompt(
        self, content_summary: str, topics: List[Topic], lesson_plans: List[LessonPlan]
    ) -> str:
        """Get LLM prompt for news takeaways."""
        topics_str = ", ".join([t.name for t in topics])
        lessons_str = "\n".join([f"- {lp.title}" for lp in lesson_plans])

        return f"""Based on this news/commentary course content, identify 3-5 key takeaways.

Content: {content_summary[:500]}...

Topics: {topics_str}

Lessons:
{lessons_str}

For each takeaway, focus on UNDERSTANDING and AWARENESS the learner will gain:
- name: Concise name (3-5 words) capturing the insight
- description: What the learner will understand about the situation
- criteria: How to verify this understanding (e.g., "Can explain X and its implications")

Focus on current events understanding, context, and informed perspectives.

Example format:
```json
[
  {{
    "name": "Event Context",
    "description": "Understand what happened, why it happened, and the key players involved",
    "criteria": "Can accurately summarize the event and explain the underlying causes"
  }},
  {{
    "name": "Multiple Perspectives",
    "description": "Recognize and understand different stakeholder viewpoints and their reasoning",
    "criteria": "Can articulate at least three different perspectives on the issue"
  }},
  {{
    "name": "Broader Implications",
    "description": "Understand how this event affects various groups and potential future developments",
    "criteria": "Can explain short-term and long-term implications for different stakeholders"
  }}
]
```

Return ONLY the JSON array, no other text."""

    def get_completion_criteria(
        self, total_lessons: int, estimated_duration: timedelta
    ) -> CompletionCriteria:
        """
        News completion focuses on informed understanding.

        Learners should understand the events, context, and implications.
        """
        return CompletionCriteria(
            type=CompletionCriteriaType.CUSTOM,
            custom_rules=(
                f"Complete all {total_lessons} lessons and demonstrate understanding "
                "of the events, context, multiple perspectives, and implications. "
                "Assessment activities will test comprehension and analysis."
            ),
            genre_specific_requirements={
                "context_understanding": True,
                "perspective_awareness": True,
                "current_events_focused": True,
            },
        )

    def get_lesson_completion_criteria(
        self, lesson_plan: LessonPlan
    ) -> CompletionCriteria:
        """News lessons require reviewing content and understanding the context."""
        return CompletionCriteria(
            type=CompletionCriteriaType.CUSTOM,
            custom_rules=(
                f"Review all content sections and understand the context of: {lesson_plan.title}"
            ),
            genre_specific_requirements={
                "context_check": True,
            },
        )
