"""
Free-form assessment activity models.

Free-form assessments allow learners to demonstrate understanding through
essays, projects, or open-ended work that requires manual or LLM-based review.
"""
from typing import Optional, Literal
from pydantic import BaseModel

from .base import LearningActivity, ActivityType


class FreeFormAssessment(LearningActivity):
    """
    Free-form assessment requiring subjective evaluation.

    Unlike quizzes with objective answers, free-form assessments allow learners
    to express understanding in their own words through essays, reflections,
    projects, or other open-ended formats.

    These assessments may include:
    - Essay questions
    - Project submissions
    - Reflective writing
    - Case study analysis
    - Creative work

    A rubric provides grading criteria, and assessment may be done manually
    or with LLM assistance.
    """
    activity_type: Literal[ActivityType.FREE_FORM_ASSESSMENT] = ActivityType.FREE_FORM_ASSESSMENT
    prompt: str  # What the learner should create/write
    guidelines: str  # Instructions and expectations
    rubric: Optional[str] = None  # Grading criteria
    word_limit: Optional[int] = None  # Maximum word count (if applicable)
