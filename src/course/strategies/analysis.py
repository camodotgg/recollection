"""
Analysis/opinion content strategy for course generation.

Analysis content focuses on critical thinking, arguments, and evaluation.
Emphasizes understanding different viewpoints and developing analytical skills.
"""
from typing import List
from datetime import timedelta

from src.content.models import Topic, Genre
from src.course.models import CompletionCriteria, CompletionCriteriaType
from .base import CourseGenerationStrategy, LessonPlan


class AnalysisStrategy(CourseGenerationStrategy):
    """
    Strategy for generating courses from analysis and opinion content.

    Analysis courses emphasize:
    - Critical thinking and evaluation
    - Understanding arguments and evidence
    - Identifying biases and assumptions
    - Forming informed opinions
    """

    def __init__(self):
        super().__init__(Genre.ANALYSIS)

    def get_lesson_structure_prompt(
        self, content_summary: str, topics: List[Topic]
    ) -> str:
        """Get LLM prompt for analysis lesson structure."""
        topics_str = ", ".join([t.name for t in topics])

        return f"""Analyze the following analysis/opinion content and determine the optimal lesson structure for learning.

Content Summary:
{content_summary}

Topics Covered: {topics_str}

Create a structured learning path that follows critical thinking best practices:
1. Start by establishing the topic and main arguments
2. Progress to examining evidence and reasoning
3. Explore counterarguments and alternative perspectives
4. End with synthesis and evaluation
5. Each lesson should focus on a specific analytical dimension
6. Balance lesson length (aim for 20-35 minute lessons)
7. Include critical thinking objectives

Return a JSON array of lessons with:
- title: Clear, analytical lesson title
- description: What analytical aspect this lesson covers
- objectives: Critical thinking objectives (what learner will ANALYZE/EVALUATE)
- topic_coverage: Which topics from the content are covered
- estimated_duration_minutes: How long the lesson should take (20-40 minutes)
- prerequisites: Titles of previous lessons needed for understanding

Focus on helping learners think critically, evaluate arguments, and form informed opinions.

Example format:
```json
[
  {{
    "title": "The Central Argument",
    "description": "Understand the main thesis, claims, and reasoning presented",
    "objectives": [
      "Identify the central argument and supporting claims",
      "Recognize the type of reasoning used",
      "Understand the author's perspective and goals"
    ],
    "topic_coverage": ["Main Argument", "Author's Position"],
    "estimated_duration_minutes": 25,
    "prerequisites": []
  }},
  {{
    "title": "Examining the Evidence",
    "description": "Critically evaluate the evidence and data presented to support the argument",
    "objectives": [
      "Assess the quality and relevance of evidence",
      "Identify logical connections and gaps",
      "Recognize potential biases in data selection"
    ],
    "topic_coverage": ["Evidence", "Data Analysis"],
    "estimated_duration_minutes": 30,
    "prerequisites": ["The Central Argument"]
  }},
  {{
    "title": "Alternative Perspectives",
    "description": "Explore counterarguments and different viewpoints on the topic",
    "objectives": [
      "Identify major counterarguments",
      "Understand opposing viewpoints",
      "Compare strengths and weaknesses of different positions"
    ],
    "topic_coverage": ["Counterarguments", "Alternative Views"],
    "estimated_duration_minutes": 30,
    "prerequisites": ["The Central Argument", "Examining the Evidence"]
  }},
  {{
    "title": "Critical Evaluation and Synthesis",
    "description": "Synthesize insights and form a balanced, informed perspective",
    "objectives": [
      "Evaluate the overall strength of the argument",
      "Synthesize multiple perspectives",
      "Develop an informed personal position"
    ],
    "topic_coverage": ["Synthesis", "Evaluation"],
    "estimated_duration_minutes": 25,
    "prerequisites": ["The Central Argument", "Examining the Evidence", "Alternative Perspectives"]
  }}
]
```

Return ONLY the JSON array, no other text."""

    def get_takeaways_prompt(
        self, content_summary: str, topics: List[Topic], lesson_plans: List[LessonPlan]
    ) -> str:
        """Get LLM prompt for analysis takeaways."""
        topics_str = ", ".join([t.name for t in topics])
        lessons_str = "\n".join([f"- {lp.title}" for lp in lesson_plans])

        return f"""Based on this analysis/opinion course content, identify 3-5 key takeaways.

Content: {content_summary[:500]}...

Topics: {topics_str}

Lessons:
{lessons_str}

For each takeaway, focus on ANALYTICAL SKILLS and INSIGHTS the learner will gain:
- name: Concise name (3-5 words) capturing the skill or insight
- description: What analytical ability or understanding the learner will develop
- criteria: How to verify this skill (e.g., "Can evaluate X and identify Y")

Focus on critical thinking skills and balanced understanding.

Example format:
```json
[
  {{
    "name": "Argument Evaluation",
    "description": "Critically assess arguments by examining evidence, logic, and assumptions",
    "criteria": "Can identify strengths and weaknesses in complex arguments and explain reasoning"
  }},
  {{
    "name": "Perspective Analysis",
    "description": "Recognize and understand multiple viewpoints on complex issues",
    "criteria": "Can articulate various perspectives fairly and identify underlying values and assumptions"
  }},
  {{
    "name": "Informed Opinion",
    "description": "Develop well-reasoned positions based on evidence and balanced consideration",
    "criteria": "Can state and defend a position while acknowledging counterarguments and limitations"
  }}
]
```

Return ONLY the JSON array, no other text."""

    def get_completion_criteria(
        self, total_lessons: int, estimated_duration: timedelta
    ) -> CompletionCriteria:
        """
        Analysis completion focuses on critical thinking demonstration.

        Learners should demonstrate ability to evaluate arguments and think critically.
        """
        return CompletionCriteria(
            type=CompletionCriteriaType.CUSTOM,
            custom_rules=(
                f"Complete all {total_lessons} lessons and demonstrate critical thinking "
                "skills through analysis activities. Assessment activities will test ability "
                "to evaluate arguments, consider multiple perspectives, and form informed opinions."
            ),
            genre_specific_requirements={
                "critical_thinking": True,
                "argument_evaluation": True,
                "perspective_consideration": True,
            },
        )

    def get_lesson_completion_criteria(
        self, lesson_plan: LessonPlan
    ) -> CompletionCriteria:
        """Analysis lessons require critical engagement with the content."""
        return CompletionCriteria(
            type=CompletionCriteriaType.CUSTOM,
            custom_rules=(
                f"Review all content sections and critically analyze: {lesson_plan.title}"
            ),
            genre_specific_requirements={
                "critical_engagement": True,
            },
        )
