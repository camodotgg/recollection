"""
Game activity models for gamified learning.

Games provide interactive, engaging ways to practice and reinforce knowledge
through activities like flashcards, matching, fill-in-the-blank, and sorting.
"""
from enum import Enum
from typing import Any, Dict, Literal
from pydantic import BaseModel

from .base import LearningActivity, ActivityType


class GameType(str, Enum):
    """Type of game activity."""
    FLASHCARDS = "flashcards"
    MATCHING = "matching"
    FILL_IN_BLANK = "fill_in_blank"
    SORTING = "sorting"


class GameActivity(LearningActivity):
    """
    Gamified learning activity for practice and reinforcement.

    Games make learning interactive and engaging through various formats:
    - Flashcards: Term/definition pairs for memorization
    - Matching: Connect related items
    - Fill-in-the-blank: Complete sentences or code
    - Sorting: Order items by category or sequence

    The game_data field is flexible and varies based on game_type to accommodate
    different game formats and requirements.
    """
    activity_type: Literal[ActivityType.GAME] = ActivityType.GAME
    game_type: GameType
    game_data: Dict[str, Any]  # Flexible game-specific data

    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "game_type": "flashcards",
                    "game_data": {
                        "cards": [
                            {"front": "Term", "back": "Definition"},
                            {"front": "Question", "back": "Answer"}
                        ]
                    }
                },
                {
                    "game_type": "matching",
                    "game_data": {
                        "pairs": [
                            {"left": "Python", "right": "Programming Language"},
                            {"left": "HTML", "right": "Markup Language"}
                        ]
                    }
                }
            ]
        }
