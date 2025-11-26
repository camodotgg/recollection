"""API routes for course and lesson progress tracking."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from pydantic import BaseModel
from datetime import datetime

from server.db.database import get_db
from server.db.models import CourseProgressDB, LessonProgressDB, CourseDB, UserDB
from server.api.routes.auth import get_current_user
from server.services.completion_validator import CompletionValidator

router = APIRouter(prefix="/progress", tags=["progress"])


# Pydantic models
class LessonProgressResponse(BaseModel):
    """Lesson progress response schema."""
    id: str
    lesson_index: int
    lesson_title: str
    is_completed: bool
    completed_manually: bool
    completed_automatically: bool
    time_spent_seconds: int
    activities_completed: int
    total_activities: int
    started_at: datetime | None
    completed_at: datetime | None
    notes: str | None

    class Config:
        from_attributes = True


class CourseProgressResponse(BaseModel):
    """Course progress response schema."""
    id: str
    course_id: str
    is_started: bool
    is_completed: bool
    completion_percent: int
    started_at: datetime
    completed_at: datetime | None
    last_accessed_at: datetime
    notes: str | None
    lesson_progress: List[LessonProgressResponse]

    class Config:
        from_attributes = True


class StartCourseRequest(BaseModel):
    """Request to start a course."""
    course_id: str


class MarkLessonCompleteRequest(BaseModel):
    """Request to mark a lesson as complete."""
    lesson_index: int
    manually: bool = True
    notes: str | None = None


class UpdateLessonTimeRequest(BaseModel):
    """Request to update lesson time spent."""
    lesson_index: int
    time_spent_seconds: int


class UpdateActivityProgressRequest(BaseModel):
    """Request to update activity progress."""
    lesson_index: int
    activities_completed: int


@router.post("/courses/start", response_model=CourseProgressResponse)
async def start_course(
    request: StartCourseRequest,
    current_user: UserDB = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
):
    """
    Start a course or get existing progress.

    Args:
        request: Course ID to start
        current_user: Current authenticated user
        session: Database session

    Returns:
        CourseProgressResponse with initial progress

    Raises:
        HTTPException: If course not found or access denied
    """
    # Check if course exists and belongs to user
    course_result = await session.execute(
        select(CourseDB).where(
            CourseDB.id == request.course_id,
            CourseDB.user_id == current_user.id
        )
    )
    course = course_result.scalar_one_or_none()

    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    # Check if progress already exists
    progress_result = await session.execute(
        select(CourseProgressDB).where(
            CourseProgressDB.user_id == current_user.id,
            CourseProgressDB.course_id == request.course_id
        )
    )
    progress = progress_result.scalar_one_or_none()

    if progress:
        # Update last accessed
        progress.last_accessed_at = datetime.utcnow()
        await session.commit()
        await session.refresh(progress)

        # Load lesson progress
        lesson_progress_result = await session.execute(
            select(LessonProgressDB).where(
                LessonProgressDB.course_progress_id == progress.id
            ).order_by(LessonProgressDB.lesson_index)
        )
        progress.lesson_progress = lesson_progress_result.scalars().all()

        return progress

    # Create new progress
    progress = CourseProgressDB(
        user_id=current_user.id,
        course_id=request.course_id,
        is_started=True,
        completion_percent=0
    )
    session.add(progress)
    await session.commit()
    await session.refresh(progress)

    # Initialize lesson progress for each lesson
    lessons = course.lessons_json
    for index, lesson in enumerate(lessons):
        # Count activities in the lesson
        activities = lesson.get("activities", [])
        total_activities = len(activities) if activities else 0

        lesson_progress = LessonProgressDB(
            course_progress_id=progress.id,
            lesson_index=index,
            lesson_title=lesson.get("title", f"Lesson {index + 1}"),
            total_activities=total_activities
        )
        session.add(lesson_progress)

    await session.commit()

    # Load all lesson progress
    lesson_progress_result = await session.execute(
        select(LessonProgressDB).where(
            LessonProgressDB.course_progress_id == progress.id
        ).order_by(LessonProgressDB.lesson_index)
    )
    progress.lesson_progress = lesson_progress_result.scalars().all()

    return progress


@router.get("/courses/{course_id}", response_model=CourseProgressResponse)
async def get_course_progress(
    course_id: str,
    current_user: UserDB = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
):
    """
    Get course progress for current user.

    Args:
        course_id: Course ID
        current_user: Current authenticated user
        session: Database session

    Returns:
        CourseProgressResponse

    Raises:
        HTTPException: If progress not found
    """
    progress_result = await session.execute(
        select(CourseProgressDB).where(
            CourseProgressDB.user_id == current_user.id,
            CourseProgressDB.course_id == course_id
        )
    )
    progress = progress_result.scalar_one_or_none()

    if not progress:
        raise HTTPException(status_code=404, detail="Course progress not found. Please start the course first.")

    # Load lesson progress
    lesson_progress_result = await session.execute(
        select(LessonProgressDB).where(
            LessonProgressDB.course_progress_id == progress.id
        ).order_by(LessonProgressDB.lesson_index)
    )
    progress.lesson_progress = lesson_progress_result.scalars().all()

    return progress


@router.post("/courses/{course_id}/lessons/complete", response_model=CourseProgressResponse)
async def mark_lesson_complete(
    course_id: str,
    request: MarkLessonCompleteRequest,
    current_user: UserDB = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
):
    """
    Mark a lesson as complete (manually or automatically).

    Args:
        course_id: Course ID
        request: Lesson index and completion info
        current_user: Current authenticated user
        session: Database session

    Returns:
        Updated CourseProgressResponse

    Raises:
        HTTPException: If progress or lesson not found
    """
    # Get course progress
    progress_result = await session.execute(
        select(CourseProgressDB).where(
            CourseProgressDB.user_id == current_user.id,
            CourseProgressDB.course_id == course_id
        )
    )
    progress = progress_result.scalar_one_or_none()

    if not progress:
        raise HTTPException(status_code=404, detail="Course progress not found. Please start the course first.")

    # Get lesson progress
    lesson_result = await session.execute(
        select(LessonProgressDB).where(
            LessonProgressDB.course_progress_id == progress.id,
            LessonProgressDB.lesson_index == request.lesson_index
        )
    )
    lesson_progress = lesson_result.scalar_one_or_none()

    if not lesson_progress:
        raise HTTPException(status_code=404, detail="Lesson not found")

    # Mark as complete
    if not lesson_progress.is_completed:
        lesson_progress.is_completed = True
        lesson_progress.completed_at = datetime.utcnow()

        if request.manually:
            lesson_progress.completed_manually = True
        else:
            lesson_progress.completed_automatically = True

    if request.notes:
        lesson_progress.notes = request.notes

    # Update last accessed
    progress.last_accessed_at = datetime.utcnow()

    # Recalculate course completion percentage
    all_lessons_result = await session.execute(
        select(LessonProgressDB).where(
            LessonProgressDB.course_progress_id == progress.id
        )
    )
    all_lessons = all_lessons_result.scalars().all()
    total_lessons = len(all_lessons)
    completed_lessons = sum(1 for lesson in all_lessons if lesson.is_completed)

    progress.completion_percent = int((completed_lessons / total_lessons) * 100) if total_lessons > 0 else 0

    # Check if all lessons are complete
    if completed_lessons == total_lessons and not progress.is_completed:
        progress.is_completed = True
        progress.completed_at = datetime.utcnow()

    await session.commit()

    # Reload all lesson progress
    lesson_progress_result = await session.execute(
        select(LessonProgressDB).where(
            LessonProgressDB.course_progress_id == progress.id
        ).order_by(LessonProgressDB.lesson_index)
    )
    progress.lesson_progress = lesson_progress_result.scalars().all()

    return progress


@router.post("/courses/{course_id}/lessons/time", response_model=CourseProgressResponse)
async def update_lesson_time(
    course_id: str,
    request: UpdateLessonTimeRequest,
    current_user: UserDB = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
):
    """
    Update time spent on a lesson and check for automatic completion.

    This endpoint should be called periodically while a user is viewing a lesson
    to track time spent. If time-based completion criteria are met, the lesson
    will be automatically marked as complete.

    Args:
        course_id: Course ID
        request: Lesson index and time spent
        current_user: Current authenticated user
        session: Database session

    Returns:
        Updated CourseProgressResponse
    """
    # Get course progress
    progress_result = await session.execute(
        select(CourseProgressDB).where(
            CourseProgressDB.user_id == current_user.id,
            CourseProgressDB.course_id == course_id
        )
    )
    progress = progress_result.scalar_one_or_none()

    if not progress:
        raise HTTPException(status_code=404, detail="Course progress not found. Please start the course first.")

    # Get lesson progress
    lesson_result = await session.execute(
        select(LessonProgressDB).where(
            LessonProgressDB.course_progress_id == progress.id,
            LessonProgressDB.lesson_index == request.lesson_index
        )
    )
    lesson_progress = lesson_result.scalar_one_or_none()

    if not lesson_progress:
        raise HTTPException(status_code=404, detail="Lesson not found")

    # Update time spent
    lesson_progress.time_spent_seconds = request.time_spent_seconds

    # Mark started if not already
    if not lesson_progress.started_at:
        lesson_progress.started_at = datetime.utcnow()

    # Get course to access lesson completion criteria
    course_result = await session.execute(
        select(CourseDB).where(CourseDB.id == course_id)
    )
    course = course_result.scalar_one_or_none()

    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    # Get lesson completion criteria from course lessons JSONB
    lessons_json = course.lessons_json
    if request.lesson_index < len(lessons_json):
        lesson_data = lessons_json[request.lesson_index]
        lesson_completion_criteria = lesson_data.get("completion_criteria", {})

        # Check if automatic completion criteria are met (only if not already completed)
        if not lesson_progress.is_completed:
            validator = CompletionValidator()
            if validator.validate_lesson_completion(
                completion_criteria=lesson_completion_criteria,
                time_spent_seconds=lesson_progress.time_spent_seconds
            ):
                # Automatically mark as complete
                lesson_progress.is_completed = True
                lesson_progress.completed_automatically = True
                lesson_progress.completed_at = datetime.utcnow()

    # Update last accessed
    progress.last_accessed_at = datetime.utcnow()

    # Recalculate course completion percentage if lesson was auto-completed
    if lesson_progress.is_completed:
        all_lessons_result = await session.execute(
            select(LessonProgressDB).where(
                LessonProgressDB.course_progress_id == progress.id
            )
        )
        all_lessons = all_lessons_result.scalars().all()
        total_lessons = len(all_lessons)
        completed_lessons = sum(1 for lesson in all_lessons if lesson.is_completed)

        progress.completion_percent = int((completed_lessons / total_lessons) * 100) if total_lessons > 0 else 0

        # Check if all lessons are complete
        if completed_lessons == total_lessons and not progress.is_completed:
            progress.is_completed = True
            progress.completed_at = datetime.utcnow()

    await session.commit()

    # Reload all lesson progress
    lesson_progress_result = await session.execute(
        select(LessonProgressDB).where(
            LessonProgressDB.course_progress_id == progress.id
        ).order_by(LessonProgressDB.lesson_index)
    )
    progress.lesson_progress = lesson_progress_result.scalars().all()

    return progress


@router.post("/courses/{course_id}/lessons/activity", response_model=CourseProgressResponse)
async def update_activity_progress(
    course_id: str,
    request: UpdateActivityProgressRequest,
    current_user: UserDB = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
):
    """
    Update activity completion progress and check for automatic completion.

    This endpoint should be called when a user completes an activity (quiz, challenge, etc.)
    within a lesson. If all activities are completed, the lesson will be automatically
    marked as complete.

    Args:
        course_id: Course ID
        request: Lesson index and activities completed count
        current_user: Current authenticated user
        session: Database session

    Returns:
        Updated CourseProgressResponse
    """
    # Get course progress
    progress_result = await session.execute(
        select(CourseProgressDB).where(
            CourseProgressDB.user_id == current_user.id,
            CourseProgressDB.course_id == course_id
        )
    )
    progress = progress_result.scalar_one_or_none()

    if not progress:
        raise HTTPException(status_code=404, detail="Course progress not found. Please start the course first.")

    # Get lesson progress
    lesson_result = await session.execute(
        select(LessonProgressDB).where(
            LessonProgressDB.course_progress_id == progress.id,
            LessonProgressDB.lesson_index == request.lesson_index
        )
    )
    lesson_progress = lesson_result.scalar_one_or_none()

    if not lesson_progress:
        raise HTTPException(status_code=404, detail="Lesson not found")

    # Update activities completed
    lesson_progress.activities_completed = request.activities_completed

    # Mark started if not already
    if not lesson_progress.started_at:
        lesson_progress.started_at = datetime.utcnow()

    # Get course to access lesson completion criteria
    course_result = await session.execute(
        select(CourseDB).where(CourseDB.id == course_id)
    )
    course = course_result.scalar_one_or_none()

    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    # Get lesson completion criteria from course lessons JSONB
    lessons_json = course.lessons_json
    if request.lesson_index < len(lessons_json):
        lesson_data = lessons_json[request.lesson_index]
        lesson_completion_criteria = lesson_data.get("completion_criteria", {})

        # Check if automatic completion criteria are met (only if not already completed)
        if not lesson_progress.is_completed:
            validator = CompletionValidator()
            if validator.validate_lesson_completion(
                completion_criteria=lesson_completion_criteria,
                time_spent_seconds=lesson_progress.time_spent_seconds,
                activities_completed=lesson_progress.activities_completed,
                total_activities=lesson_progress.total_activities
            ):
                # Automatically mark as complete
                lesson_progress.is_completed = True
                lesson_progress.completed_automatically = True
                lesson_progress.completed_at = datetime.utcnow()

    # Update last accessed
    progress.last_accessed_at = datetime.utcnow()

    # Recalculate course completion percentage if lesson was auto-completed
    if lesson_progress.is_completed:
        all_lessons_result = await session.execute(
            select(LessonProgressDB).where(
                LessonProgressDB.course_progress_id == progress.id
            )
        )
        all_lessons = all_lessons_result.scalars().all()
        total_lessons = len(all_lessons)
        completed_lessons = sum(1 for lesson in all_lessons if lesson.is_completed)

        progress.completion_percent = int((completed_lessons / total_lessons) * 100) if total_lessons > 0 else 0

        # Check if all lessons are complete
        if completed_lessons == total_lessons and not progress.is_completed:
            progress.is_completed = True
            progress.completed_at = datetime.utcnow()

    await session.commit()

    # Reload all lesson progress
    lesson_progress_result = await session.execute(
        select(LessonProgressDB).where(
            LessonProgressDB.course_progress_id == progress.id
        ).order_by(LessonProgressDB.lesson_index)
    )
    progress.lesson_progress = lesson_progress_result.scalars().all()

    return progress


@router.delete("/courses/{course_id}/lessons/{lesson_index}/complete")
async def unmark_lesson_complete(
    course_id: str,
    lesson_index: int,
    current_user: UserDB = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
):
    """
    Unmark a lesson as complete (allow users to reset progress).

    Args:
        course_id: Course ID
        lesson_index: Lesson index
        current_user: Current authenticated user
        session: Database session

    Returns:
        Success message

    Raises:
        HTTPException: If progress or lesson not found
    """
    # Get course progress
    progress_result = await session.execute(
        select(CourseProgressDB).where(
            CourseProgressDB.user_id == current_user.id,
            CourseProgressDB.course_id == course_id
        )
    )
    progress = progress_result.scalar_one_or_none()

    if not progress:
        raise HTTPException(status_code=404, detail="Course progress not found")

    # Get lesson progress
    lesson_result = await session.execute(
        select(LessonProgressDB).where(
            LessonProgressDB.course_progress_id == progress.id,
            LessonProgressDB.lesson_index == lesson_index
        )
    )
    lesson_progress = lesson_result.scalar_one_or_none()

    if not lesson_progress:
        raise HTTPException(status_code=404, detail="Lesson not found")

    # Unmark as complete
    lesson_progress.is_completed = False
    lesson_progress.completed_manually = False
    lesson_progress.completed_automatically = False
    lesson_progress.completed_at = None

    # Recalculate course completion percentage
    all_lessons_result = await session.execute(
        select(LessonProgressDB).where(
            LessonProgressDB.course_progress_id == progress.id
        )
    )
    all_lessons = all_lessons_result.scalars().all()
    total_lessons = len(all_lessons)
    completed_lessons = sum(1 for lesson in all_lessons if lesson.is_completed)

    progress.completion_percent = int((completed_lessons / total_lessons) * 100) if total_lessons > 0 else 0
    progress.is_completed = False
    progress.completed_at = None

    await session.commit()

    return {"message": "Lesson unmarked as complete"}
