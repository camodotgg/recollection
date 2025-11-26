"""
Quiz activity models for assessments and knowledge checks.

Quizzes test learner understanding through various question types including
multiple choice, true/false, short answer, and multiple select questions.
"""
from enum import Enum
from typing import Sequence, Optional, Literal
from pydantic import BaseModel

from .base import LearningActivity, ActivityType


class QuestionType(str, Enum):
    """Type of quiz question."""
    MULTIPLE_CHOICE = "multiple_choice"
    TRUE_FALSE = "true_false"
    SHORT_ANSWER = "short_answer"
    MULTIPLE_SELECT = "multiple_select"


class QuizQuestion(BaseModel):
    """
    A single question within a quiz activity.

    Supports multiple question types with appropriate answer formats:
    - Multiple choice: single correct answer from options
    - True/False: boolean question
    - Short answer: text-based answer
    - Multiple select: multiple correct answers from options
    """
    id: str
    question: str
    question_type: QuestionType
    options: Optional[Sequence[str]] = None  # For multiple choice/select
    correct_answer: str | Sequence[str]  # Single or multiple correct answers
    explanation: str  # Explain the correct answer
    points: int = 1


class QuizActivity(LearningActivity):
    """
    Quiz activity for testing knowledge and understanding.

    A quiz consists of multiple questions of various types. Learners must
    achieve a minimum passing score to complete the quiz, and may be allowed
    to retry if they don't pass on the first attempt.

    The quiz tracks individual question responses and provides explanations
    for correct answers to facilitate learning.
    """
    activity_type: Literal[ActivityType.QUIZ] = ActivityType.QUIZ
    questions: Sequence[QuizQuestion]
    passing_score: int = 70  # Percentage needed to pass (0-100)
    allow_retries: bool = True
