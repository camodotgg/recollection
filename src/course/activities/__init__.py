"""
Learning activities module.

This module provides all activity types that can be included in lessons:
- QuizActivity: Knowledge assessment with questions
- ChallengeActivity: Practical exercises and problems
- GameActivity: Gamified learning (flashcards, matching, etc.)
- FreeFormAssessment: Open-ended work requiring review
- DailyChallenge: Periodic challenges for engagement
"""
from .base import LearningActivity, ActivityType
from .quiz import QuizActivity, QuizQuestion, QuestionType
from .challenge import ChallengeActivity
from .game import GameActivity, GameType
from .assessment import FreeFormAssessment
from .daily import DailyChallenge, ChallengeType

__all__ = [
    # Base
    "LearningActivity",
    "ActivityType",
    # Quiz
    "QuizActivity",
    "QuizQuestion",
    "QuestionType",
    # Challenge
    "ChallengeActivity",
    # Game
    "GameActivity",
    "GameType",
    # Assessment
    "FreeFormAssessment",
    # Daily
    "DailyChallenge",
    "ChallengeType",
]
