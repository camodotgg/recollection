"""
Course module for learning system.

This module provides data models and activities for structured learning courses
generated from content. Courses contain lessons with various learning activities
and completion criteria.
"""
from .models import (
    # Core models
    Course,
    Lesson,
    ContentSection,
    ContentReference,
    Takeaway,
    CompletionCriteria,
    # Enums
    DifficultyLevel,
    ContentSectionType,
    CompletionCriteriaType,
)

from .activities import (
    # Base
    LearningActivity,
    ActivityType,
    # Quiz
    QuizActivity,
    QuizQuestion,
    QuestionType,
    # Challenge
    ChallengeActivity,
    # Game
    GameActivity,
    GameType,
    # Assessment
    FreeFormAssessment,
    # Daily
    DailyChallenge,
    ChallengeType,
)

from .generator import generate_course
from .merger import merge_contents, MergedContent
from .strategies import (
    CourseGenerationStrategy,
    LessonPlan,
    get_strategy_for_genre,
)

__all__ = [
    # Core models
    "Course",
    "Lesson",
    "ContentSection",
    "ContentReference",
    "Takeaway",
    "CompletionCriteria",
    # Enums
    "DifficultyLevel",
    "ContentSectionType",
    "CompletionCriteriaType",
    # Activities - Base
    "LearningActivity",
    "ActivityType",
    # Activities - Quiz
    "QuizActivity",
    "QuizQuestion",
    "QuestionType",
    # Activities - Challenge
    "ChallengeActivity",
    # Activities - Game
    "GameActivity",
    "GameType",
    # Activities - Assessment
    "FreeFormAssessment",
    # Activities - Daily
    "DailyChallenge",
    "ChallengeType",
    # Course generation
    "generate_course",
    "merge_contents",
    "MergedContent",
    "CourseGenerationStrategy",
    "LessonPlan",
    "get_strategy_for_genre",
]
