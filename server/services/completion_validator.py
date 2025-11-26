"""Service for validating completion criteria for lessons and courses."""

from typing import Dict, Any, Optional
from datetime import timedelta


class CompletionValidator:
    """
    Validates whether lesson or course completion criteria have been met.

    Supports multiple completion types:
    - ALL_ACTIVITIES: Complete all required activities
    - SCORE_THRESHOLD: Achieve a minimum percentage score
    - TIME_BASED: Spend a minimum amount of time
    - CUSTOM: Custom completion logic
    """

    @staticmethod
    def validate_lesson_completion(
        completion_criteria: Dict[str, Any],
        time_spent_seconds: int,
        activities_completed: Optional[int] = None,
        total_activities: Optional[int] = None,
        score: Optional[int] = None
    ) -> bool:
        """
        Check if a lesson's completion criteria have been met.

        Args:
            completion_criteria: The lesson's completion criteria from JSONB
            time_spent_seconds: Time spent on the lesson in seconds
            activities_completed: Number of activities completed (if applicable)
            total_activities: Total number of required activities (if applicable)
            score: Score achieved (0-100) (if applicable)

        Returns:
            True if criteria are met, False otherwise
        """
        if not completion_criteria:
            # No criteria defined - cannot auto-complete
            return False

        criteria_type = completion_criteria.get("type")

        if criteria_type == "time_based":
            # Check if minimum time has been spent
            minimum_time = completion_criteria.get("minimum_time")
            if minimum_time:
                # minimum_time is stored as seconds in the database
                required_seconds = minimum_time
                if isinstance(required_seconds, dict):
                    # Handle timedelta serialization {"seconds": X}
                    required_seconds = required_seconds.get("seconds", 0)
                return time_spent_seconds >= required_seconds
            return False

        elif criteria_type == "all_activities":
            # Check if all activities are completed
            if activities_completed is not None and total_activities is not None:
                return activities_completed >= total_activities
            return False

        elif criteria_type == "score_threshold":
            # Check if minimum score has been achieved
            minimum_score = completion_criteria.get("minimum_score")
            if minimum_score is not None and score is not None:
                return score >= minimum_score
            return False

        elif criteria_type == "custom":
            # Custom criteria - for now, return False (manual completion required)
            # Could be extended to evaluate custom_rules string
            return False

        # Unknown criteria type - cannot auto-complete
        return False

    @staticmethod
    def validate_course_completion(
        completion_criteria: Dict[str, Any],
        lessons_completed: int,
        total_lessons: int,
        overall_score: Optional[int] = None
    ) -> bool:
        """
        Check if a course's completion criteria have been met.

        Args:
            completion_criteria: The course's completion criteria from JSONB
            lessons_completed: Number of lessons completed
            total_lessons: Total number of lessons
            overall_score: Overall course score (0-100) (if applicable)

        Returns:
            True if criteria are met, False otherwise
        """
        if not completion_criteria:
            # No criteria - default to all lessons completed
            return lessons_completed == total_lessons

        criteria_type = completion_criteria.get("type")

        if criteria_type == "all_activities":
            # All lessons must be completed
            return lessons_completed == total_lessons

        elif criteria_type == "score_threshold":
            # Check if minimum score has been achieved across all lessons
            minimum_score = completion_criteria.get("minimum_score")
            if minimum_score is not None and overall_score is not None:
                return overall_score >= minimum_score and lessons_completed == total_lessons
            # Fallback to all lessons completed if no score available
            return lessons_completed == total_lessons

        elif criteria_type == "time_based":
            # For courses, time-based usually means all lessons with time requirements completed
            return lessons_completed == total_lessons

        elif criteria_type == "custom":
            # Custom criteria - for now, require all lessons completed
            return lessons_completed == total_lessons

        # Default: all lessons completed
        return lessons_completed == total_lessons

    @staticmethod
    def get_completion_progress_description(
        completion_criteria: Dict[str, Any],
        current_progress: Dict[str, Any]
    ) -> str:
        """
        Get a human-readable description of completion progress.

        Args:
            completion_criteria: The completion criteria
            current_progress: Current progress metrics (time_spent, score, etc.)

        Returns:
            Description string
        """
        if not completion_criteria:
            return "Complete the lesson"

        criteria_type = completion_criteria.get("type")

        if criteria_type == "time_based":
            minimum_time = completion_criteria.get("minimum_time")
            time_spent = current_progress.get("time_spent_seconds", 0)

            if isinstance(minimum_time, dict):
                required_seconds = minimum_time.get("seconds", 0)
            else:
                required_seconds = minimum_time or 0

            required_minutes = required_seconds // 60
            spent_minutes = time_spent // 60

            return f"Spend at least {required_minutes} minutes (current: {spent_minutes} min)"

        elif criteria_type == "all_activities":
            activities_completed = current_progress.get("activities_completed", 0)
            total_activities = current_progress.get("total_activities", 0)
            return f"Complete all {total_activities} activities (current: {activities_completed})"

        elif criteria_type == "score_threshold":
            minimum_score = completion_criteria.get("minimum_score", 0)
            current_score = current_progress.get("score", 0)
            return f"Achieve {minimum_score}% score (current: {current_score}%)"

        elif criteria_type == "custom":
            custom_rules = completion_criteria.get("custom_rules", "")
            return custom_rules or "Complete custom requirements"

        return "Complete the lesson"
