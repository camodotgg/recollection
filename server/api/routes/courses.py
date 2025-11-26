"""Course management routes."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import List, Optional
import uuid

from server.db.database import get_db
from server.db.models import UserDB, CourseDB, TaskStatusDB, TaskStatus
from server.api.dependencies import get_current_user
from workers.tasks.course_tasks import generate_course_task

router = APIRouter(prefix="/courses", tags=["courses"])


class GenerateCourseRequest(BaseModel):
    """Request to generate a course."""
    content_ids: List[str]


class GenerateCourseResponse(BaseModel):
    """Response for course generation request."""
    task_id: str
    status: str
    message: str


class CourseResponse(BaseModel):
    """Course response schema."""
    id: str
    title: str
    description: str
    objective: str
    genre: str
    difficulty_level: str
    estimated_duration_seconds: int
    created_at: str

    class Config:
        from_attributes = True


class CourseDetailResponse(BaseModel):
    """Detailed course response schema."""
    id: str
    title: str
    description: str
    objective: str
    genre: str
    difficulty_level: str
    lessons: List[dict]
    takeaways: List[dict]
    topics: List[dict]
    completion_criteria: dict
    source_content: List[dict]
    estimated_duration_seconds: int
    created_at: str

    class Config:
        from_attributes = True


@router.post("/generate", response_model=GenerateCourseResponse, status_code=status.HTTP_202_ACCEPTED)
async def generate_course(
    request: GenerateCourseRequest,
    current_user: UserDB = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
) -> GenerateCourseResponse:
    """
    Generate a course from content (async background task).

    Args:
        request: Content IDs to generate course from
        current_user: Current authenticated user
        session: Database session

    Returns:
        GenerateCourseResponse with task_id for tracking
    """
    if not request.content_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one content_id is required"
        )

    # Generate task ID
    task_id = str(uuid.uuid4())

    # Create task status record
    task_status = TaskStatusDB(
        task_id=task_id,
        user_id=current_user.id,
        status=TaskStatus.PENDING,
        progress_percent=0,
        current_step="Queued for processing..."
    )
    session.add(task_status)
    await session.commit()

    # Enqueue Celery task
    generate_course_task.apply_async(
        args=[task_id, current_user.id, request.content_ids],
        task_id=task_id
    )

    return GenerateCourseResponse(
        task_id=task_id,
        status="pending",
        message="Course generation started. Use task_id to check progress."
    )


@router.get("", response_model=List[CourseResponse])
async def list_courses(
    current_user: UserDB = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 20
) -> List[CourseResponse]:
    """
    List all courses for the current user.

    Args:
        current_user: Current authenticated user
        session: Database session
        skip: Number of records to skip
        limit: Maximum number of records to return

    Returns:
        List of courses
    """
    result = await session.execute(
        select(CourseDB)
        .where(CourseDB.user_id == current_user.id)
        .order_by(CourseDB.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    courses = result.scalars().all()

    return [
        CourseResponse(
            id=course.id,
            title=course.title,
            description=course.description,
            objective=course.objective,
            genre=course.genre,
            difficulty_level=course.difficulty_level,
            estimated_duration_seconds=course.estimated_duration_seconds,
            created_at=course.created_at.isoformat()
        )
        for course in courses
    ]


@router.get("/{course_id}", response_model=CourseDetailResponse)
async def get_course(
    course_id: str,
    current_user: UserDB = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
) -> CourseDetailResponse:
    """
    Get a specific course with full details.

    Args:
        course_id: Course ID
        current_user: Current authenticated user
        session: Database session

    Returns:
        Detailed course information

    Raises:
        HTTPException: If course not found or access denied
    """
    result = await session.execute(
        select(CourseDB).where(
            CourseDB.id == course_id,
            CourseDB.user_id == current_user.id
        )
    )
    course = result.scalar_one_or_none()

    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )

    return CourseDetailResponse(
        id=course.id,
        title=course.title,
        description=course.description,
        objective=course.objective,
        genre=course.genre,
        difficulty_level=course.difficulty_level,
        lessons=course.lessons_json,
        takeaways=course.takeaways_json,
        topics=course.topics_json,
        completion_criteria=course.completion_criteria_json,
        source_content=course.source_content_json,
        estimated_duration_seconds=course.estimated_duration_seconds,
        created_at=course.created_at.isoformat()
    )


@router.delete("/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_course(
    course_id: str,
    current_user: UserDB = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
):
    """
    Delete a course.

    Args:
        course_id: Course ID
        current_user: Current authenticated user
        session: Database session

    Raises:
        HTTPException: If course not found or access denied
    """
    result = await session.execute(
        select(CourseDB).where(
            CourseDB.id == course_id,
            CourseDB.user_id == current_user.id
        )
    )
    course = result.scalar_one_or_none()

    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )

    await session.delete(course)
    await session.commit()
