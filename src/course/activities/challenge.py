"""
Challenge and exercise activity models.

Challenges are practical, hands-on tasks that require learners to apply their
knowledge to solve problems or complete exercises.
"""
from enum import Enum
from typing import Sequence, Optional, Literal
from pydantic import BaseModel

from .base import LearningActivity, ActivityType


class ChallengeActivity(LearningActivity):
    """
    Challenge/exercise activity for practical application of knowledge.

    Challenges present learners with a problem or task to solve, with progressive
    hints available to guide them. A reference solution may be provided after
    completion for learners to compare their approach.

    Challenges emphasize practical skills and problem-solving rather than
    memorization of facts.
    """
    activity_type: Literal[ActivityType.CHALLENGE] = ActivityType.CHALLENGE
    prompt: str  # What the learner needs to do
    hints: Sequence[str] = []  # Progressive hints (shown one at a time)
    solution: Optional[str] = None  # Reference solution (optional)
    verification_criteria: str = ""  # How to verify the challenge is complete
