"""Content management routes."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel, HttpUrl
from typing import List, Optional
import uuid

from server.db.database import get_db
from server.db.models import UserDB, ContentDB, TaskStatusDB, TaskStatus
from server.api.dependencies import get_current_user
from workers.tasks.content_tasks import load_content_task

router = APIRouter(prefix="/content", tags=["content"])


class LoadContentRequest(BaseModel):
    """Request to load content from a URL."""
    url: HttpUrl


class LoadContentResponse(BaseModel):
    """Response for content loading request."""
    task_id: str
    status: str
    message: str


class ContentResponse(BaseModel):
    """Content response schema."""
    id: str
    source_link: Optional[str]
    source_author: Optional[str]
    source_origin: Optional[str]
    source_format: Optional[str]
    summary: dict
    created_at: str

    class Config:
        from_attributes = True


@router.post("/load", response_model=LoadContentResponse, status_code=status.HTTP_202_ACCEPTED)
async def load_content(
    request: LoadContentRequest,
    current_user: UserDB = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
) -> LoadContentResponse:
    """
    Load content from a URL (async background task).

    Args:
        request: URL to load content from
        current_user: Current authenticated user
        session: Database session

    Returns:
        LoadContentResponse with task_id for tracking
    """
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
    load_content_task.apply_async(
        args=[task_id, current_user.id, str(request.url)],
        task_id=task_id
    )

    return LoadContentResponse(
        task_id=task_id,
        status="pending",
        message="Content loading started. Use task_id to check progress."
    )


@router.get("", response_model=List[ContentResponse])
async def list_content(
    current_user: UserDB = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 20
) -> List[ContentResponse]:
    """
    List all content for the current user.

    Args:
        current_user: Current authenticated user
        session: Database session
        skip: Number of records to skip
        limit: Maximum number of records to return

    Returns:
        List of content items
    """
    result = await session.execute(
        select(ContentDB)
        .where(ContentDB.user_id == current_user.id)
        .order_by(ContentDB.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    contents = result.scalars().all()

    return [
        ContentResponse(
            id=content.id,
            source_link=content.source_link,
            source_author=content.source_author,
            source_origin=content.source_origin,
            source_format=content.source_format,
            summary=content.summary_json,
            created_at=content.created_at.isoformat()
        )
        for content in contents
    ]


@router.get("/{content_id}", response_model=ContentResponse)
async def get_content(
    content_id: str,
    current_user: UserDB = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
) -> ContentResponse:
    """
    Get a specific content item.

    Args:
        content_id: Content ID
        current_user: Current authenticated user
        session: Database session

    Returns:
        Content item

    Raises:
        HTTPException: If content not found or access denied
    """
    result = await session.execute(
        select(ContentDB).where(
            ContentDB.id == content_id,
            ContentDB.user_id == current_user.id
        )
    )
    content = result.scalar_one_or_none()

    if not content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Content not found"
        )

    return ContentResponse(
        id=content.id,
        source_link=content.source_link,
        source_author=content.source_author,
        source_origin=content.source_origin,
        source_format=content.source_format,
        summary=content.summary_json,
        created_at=content.created_at.isoformat()
    )


@router.delete("/{content_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_content(
    content_id: str,
    current_user: UserDB = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
):
    """
    Delete a content item.

    Args:
        content_id: Content ID
        current_user: Current authenticated user
        session: Database session

    Raises:
        HTTPException: If content not found or access denied
    """
    result = await session.execute(
        select(ContentDB).where(
            ContentDB.id == content_id,
            ContentDB.user_id == current_user.id
        )
    )
    content = result.scalar_one_or_none()

    if not content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Content not found"
        )

    await session.delete(content)
    await session.commit()
