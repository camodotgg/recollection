"""
Base strategy for genre-specific course generation.

This module defines the abstract base class for course generation strategies.
Different content genres (tutorials, documentaries, news, etc.) may require
different approaches to lesson structuring and completion criteria.
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, List
from datetime import timedelta

from pydantic import BaseModel

from src.content.models import Content, Topic, Genre
from src.course.models import CompletionCriteria, CompletionCriteriaType


class LessonPlan(BaseModel):
    """
    Planned structure for a lesson before full generation.

    Represents the LLM's decision about how to break content into lessons.
    """

    title: str
    description: str
    objectives: List[str]
    topic_coverage: List[str]  # Which topics from content are covered
    estimated_duration_minutes: int
    prerequisites: List[str] = []  # Titles of previous lessons


class CourseGenerationStrategy(ABC):
    """
    Base strategy for genre-specific course generation.

    Different content genres require different approaches:
    - Tutorials: Step-by-step, building complexity
    - Documentaries: Comprehension and retention focused
    - News: Context and current events understanding
    - Analysis: Critical thinking and argument evaluation

    Each strategy customizes:
    1. How lessons are structured from content
    2. What completion criteria are used
    3. How content sections are extracted and organized
    """

    def __init__(self, genre: Genre):
        """
        Initialize strategy for a specific genre.

        Args:
            genre: The genre this strategy handles
        """
        self.genre = genre

    @abstractmethod
    def get_lesson_structure_prompt(
        self, content_summary: str, topics: List[Topic]
    ) -> str:
        """
        Get the LLM prompt for determining lesson structure.

        This prompt guides the LLM in analyzing content and deciding
        how to break it into learnable lessons.

        Args:
            content_summary: Combined summary of all content
            topics: List of topics covered in the content

        Returns:
            Formatted prompt string for the LLM
        """
        pass

    @abstractmethod
    def get_takeaways_prompt(
        self, content_summary: str, topics: List[Topic], lesson_plans: List[LessonPlan]
    ) -> str:
        """
        Get the LLM prompt for extracting course takeaways.

        Args:
            content_summary: Combined summary of all content
            topics: List of topics covered
            lesson_plans: Planned lesson structure

        Returns:
            Formatted prompt string for the LLM
        """
        pass

    @abstractmethod
    def get_completion_criteria(
        self, total_lessons: int, estimated_duration: timedelta
    ) -> CompletionCriteria:
        """
        Get genre-specific completion criteria for the course.

        Different genres may have different requirements:
        - Tutorials might require practice activities
        - Documentaries might focus on comprehension
        - News might emphasize contextual understanding

        Args:
            total_lessons: Number of lessons in the course
            estimated_duration: Total estimated course duration

        Returns:
            CompletionCriteria object
        """
        pass

    def get_lesson_completion_criteria(
        self, lesson_plan: LessonPlan
    ) -> CompletionCriteria:
        """
        Get completion criteria for an individual lesson.

        Default implementation requires reviewing all content sections.
        Strategies can override for genre-specific requirements.

        Args:
            lesson_plan: The planned lesson

        Returns:
            CompletionCriteria object for the lesson
        """
        return CompletionCriteria(
            type=CompletionCriteriaType.CUSTOM,
            custom_rules="Review all content sections in this lesson",
        )

    def parse_lesson_structure_response(self, llm_response: str) -> List[LessonPlan]:
        """
        Parse the LLM's lesson structure response into LessonPlan objects.

        Expects JSON array format from LLM.

        Args:
            llm_response: Raw LLM response string

        Returns:
            List of LessonPlan objects

        Raises:
            ValueError: If response cannot be parsed
        """
        import json

        try:
            # Handle potential markdown code blocks
            response = llm_response.strip()
            if response.startswith("```"):
                # Extract JSON from code block
                lines = response.split("\n")
                response = "\n".join(lines[1:-1])  # Remove first and last lines

            data = json.loads(response)

            if not isinstance(data, list):
                raise ValueError("Expected JSON array of lesson plans")

            return [LessonPlan.model_validate(item) for item in data]

        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse lesson structure response: {e}")
        except Exception as e:
            raise ValueError(f"Failed to validate lesson plans: {e}")

    def parse_takeaways_response(self, llm_response: str) -> List[Dict[str, str]]:
        """
        Parse the LLM's takeaways response.

        Expects JSON array with name, description, criteria fields.

        Args:
            llm_response: Raw LLM response string

        Returns:
            List of takeaway dictionaries

        Raises:
            ValueError: If response cannot be parsed
        """
        import json

        try:
            # Handle potential markdown code blocks
            response = llm_response.strip()
            if response.startswith("```"):
                lines = response.split("\n")
                response = "\n".join(lines[1:-1])

            data = json.loads(response)

            if not isinstance(data, list):
                raise ValueError("Expected JSON array of takeaways")

            # Validate structure
            for item in data:
                if not all(key in item for key in ["name", "description", "criteria"]):
                    raise ValueError(
                        "Each takeaway must have name, description, and criteria"
                    )

            return data

        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse takeaways response: {e}")
