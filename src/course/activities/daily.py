"""
Daily challenge models for periodic practice and engagement.

Daily challenges are special activities that appear on a schedule to keep
learners engaged and reinforce key concepts over time.
"""
from enum import Enum
from typing import Sequence, Optional
from datetime import date
from pydantic import BaseModel

from src.course.models import DifficultyLevel


class ChallengeType(str, Enum):
    """Type of daily challenge."""
    PRACTICE = "practice"  # Review previous material
    EXPLORATION = "exploration"  # Explore new related topics
    APPLICATION = "application"  # Apply knowledge to new scenarios


class DailyChallenge(BaseModel):
    """
    Special challenge that appears daily or periodically.

    Daily challenges provide ongoing engagement and spaced repetition to
    reinforce learning. They can review previous material, introduce new
    related concepts, or encourage application of knowledge in new contexts.

    Challenges are scheduled with availability and expiration dates, and
    may award points for gamification.
    """
    id: str
    title: str
    description: str
    challenge_type: ChallengeType
    difficulty: DifficultyLevel

    # Related content
    related_course_id: Optional[str] = None
    related_topics: Sequence[str] = []

    # Challenge content
    prompt: str
    hints: Sequence[str] = []
    solution: Optional[str] = None

    # Scheduling
    available_date: date
    expires_date: Optional[date] = None

    # Gamification
    points: int = 10
