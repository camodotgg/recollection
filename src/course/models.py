"""
Course and Lesson data models for the learning system.

This module defines the core data structures for courses, lessons, and completion criteria.
Courses are generated from Content objects and contain structured lessons with learning
activities and completion requirements.
"""
from enum import Enum
from typing import Any, Dict, Sequence, Optional, Union
from datetime import datetime, timedelta, date
from pathlib import Path

from pydantic import BaseModel

from src.content.models import Genre, Topic


# ============================================================================
# Enums
# ============================================================================

class DifficultyLevel(str, Enum):
    """Difficulty level for courses and activities."""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class ContentSectionType(str, Enum):
    """Type of content section within a lesson."""
    TEXT = "text"
    VIDEO_REFERENCE = "video_reference"
    CODE_EXAMPLE = "code_example"
    DIAGRAM = "diagram"
    QUOTE = "quote"
    KEY_POINT = "key_point"


class CompletionCriteriaType(str, Enum):
    """Type of completion criteria for lessons and courses."""
    ALL_ACTIVITIES = "all_activities"  # Complete all required activities
    SCORE_THRESHOLD = "score_threshold"  # Achieve minimum score
    TIME_BASED = "time_based"  # Spend minimum time
    CUSTOM = "custom"  # Custom criteria


# ============================================================================
# Base Models
# ============================================================================

class ContentReference(BaseModel):
    """
    Links back to source content that inspired this course.

    Maintains traceability between generated courses and their source materials,
    allowing learners to reference the original content.
    """
    content_id: str
    link: str
    relevance: str


class Takeaway(BaseModel):
    """
    A key learning outcome or takeaway from a course or lesson.
    """
    name: str
    description: str
    criteria: str


class CompletionCriteria(BaseModel):
    """
    Defines how a lesson or course is considered complete.

    Supports multiple completion types:
    - ALL_ACTIVITIES: Complete all required activities
    - SCORE_THRESHOLD: Achieve a minimum percentage score
    - TIME_BASED: Spend a minimum amount of time
    - CUSTOM: Custom completion logic

    Different content genres may have different completion requirements.
    """
    type: CompletionCriteriaType

    # For SCORE_THRESHOLD
    minimum_score: Optional[int] = None  # Percentage (0-100)

    # For TIME_BASED
    minimum_time: Optional[timedelta] = None

    # For CUSTOM
    custom_rules: Optional[str] = None

    # Genre-specific requirements
    genre_specific_requirements: Optional[Dict[str, Any]] = None


# ============================================================================
# Lesson Models
# ============================================================================

class ContentSection(BaseModel):
    """
    A section of instructional content within a lesson.

    Each section represents a discrete piece of learning material, such as
    explanatory text, code examples, or references to source material.
    """
    id: str
    title: str
    body: str  # Markdown or rich text
    order: int
    type: ContentSectionType
    source_reference: Optional[ContentReference] = None


class Lesson(BaseModel):
    """
    Individual learning unit within a course.

    A lesson represents a focused learning session with specific objectives,
    instructional content sections, learning activities, and completion criteria.
    Lessons are ordered within a course and may have prerequisites.
    """
    id: str
    title: str
    description: str
    order: int

    # Learning objectives
    objectives: Sequence[str]
    prerequisites: Sequence[str] = []  # IDs of previous lessons

    # Content
    content_sections: Sequence[ContentSection]

    # Activities
    # Union type allows any activity type (Quiz, Challenge, Game, Assessment)
    # Import is deferred to avoid circular dependency
    activities: Sequence[Any] = []  # TYPE: Union[QuizActivity, ChallengeActivity, GameActivity, FreeFormAssessment]

    # Completion
    completion_criteria: CompletionCriteria
    estimated_duration: timedelta


# ============================================================================
# Course Model
# ============================================================================

class Course(BaseModel):
    """
    A learning program generated from one or more Content objects.

    Courses provide structured learning paths with ordered lessons, learning
    activities, and clear completion criteria. They are generated based on the
    genre and topics of source content (tutorials, documentaries, news, etc.).

    The course maintains references to its source content for transparency and
    allows learners to access the original material.
    """
    id: str
    title: str
    description: str
    objective: str

    # Link to source content
    source_content: Sequence[ContentReference]

    # Course metadata
    genre: Genre
    topics: Sequence[Topic]
    difficulty_level: DifficultyLevel
    estimated_duration: timedelta

    # Structure
    lessons: Sequence[Lesson]
    takeaways: Sequence[Takeaway]

    # Completion
    completion_criteria: CompletionCriteria

    # Timestamps
    created_at: datetime
    updated_at: datetime

    def to_json_file(self, file_path: Path | str) -> None:
        """
        Save Course object to a JSON file.

        Args:
            file_path: Path where to save the JSON file
        """
        file_path = Path(file_path)
        file_path.parent.mkdir(parents=True, exist_ok=True)

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(self.model_dump_json(indent=2))

    @classmethod
    def from_json_file(cls, file_path: Path | str) -> "Course":
        """
        Load Course object from a JSON file.

        Args:
            file_path: Path to the JSON file

        Returns:
            Course object loaded from file

        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If JSON is invalid
        """
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        with open(file_path, "r", encoding="utf-8") as f:
            return cls.model_validate_json(f.read())

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert Course object to a dictionary.

        Returns:
            Dictionary representation of the Course object
        """
        return self.model_dump()

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Course":
        """
        Create Course object from a dictionary.

        Args:
            data: Dictionary containing course data

        Returns:
            Course object
        """
        return cls.model_validate(data)
