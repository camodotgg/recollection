"""
Course generation strategies for different content genres.

This module provides genre-specific strategies for generating courses from content.
Each strategy customizes lesson structure, completion criteria, and learning objectives
based on the content type (tutorials, documentaries, news, analysis).
"""
from .base import CourseGenerationStrategy, LessonPlan
from .tutorial import TutorialStrategy
from .documentary import DocumentaryStrategy
from .news import NewsStrategy
from .analysis import AnalysisStrategy

from src.content.models import Genre


__all__ = [
    "CourseGenerationStrategy",
    "LessonPlan",
    "TutorialStrategy",
    "DocumentaryStrategy",
    "NewsStrategy",
    "AnalysisStrategy",
    "get_strategy_for_genre",
]


def get_strategy_for_genre(genre: Genre) -> CourseGenerationStrategy:
    """
    Get the appropriate course generation strategy for a genre.

    Args:
        genre: The content genre

    Returns:
        CourseGenerationStrategy instance for the genre

    Example:
        >>> strategy = get_strategy_for_genre(Genre.TUTORIAL)
        >>> isinstance(strategy, TutorialStrategy)
        True
    """
    strategy_map = {
        Genre.TUTORIAL: TutorialStrategy,
        Genre.DOCUMENTARY: DocumentaryStrategy,
        Genre.NEWS: NewsStrategy,
        Genre.COMMENTARY: NewsStrategy,  # Commentary uses news strategy
        Genre.ANALYSIS: AnalysisStrategy,
        Genre.OPINION: AnalysisStrategy,  # Opinion uses analysis strategy
        Genre.REVIEW: AnalysisStrategy,  # Review uses analysis strategy
    }

    strategy_class = strategy_map.get(genre)

    if strategy_class is None:
        # Default to tutorial strategy for unknown genres
        return TutorialStrategy()

    return strategy_class()
