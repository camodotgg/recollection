"""
Base classes and enums for learning activities.

This module defines the base LearningActivity class and common enums used across
all activity types (quizzes, challenges, games, assessments).
"""
from enum import Enum
from datetime import timedelta
from pydantic import BaseModel


class ActivityType(str, Enum):
    """Type of learning activity."""
    QUIZ = "quiz"
    CHALLENGE = "challenge"
    GAME = "game"
    FREE_FORM_ASSESSMENT = "free_form_assessment"
    DAILY_CHALLENGE = "daily_challenge"


class LearningActivity(BaseModel):
    """
    Base class for all learning activities.

    Activities are interactive elements within lessons that help learners practice
    and demonstrate their understanding. This base class defines common fields
    shared by all activity types.

    Specific activity types (Quiz, Challenge, Game, etc.) extend this base class
    with their own specialized fields and behavior.
    """
    id: str
    title: str
    description: str
    activity_type: ActivityType
    order: int  # Order within lesson
    estimated_duration: timedelta

    # Completion requirement
    is_required: bool = True  # Must complete to finish lesson?
