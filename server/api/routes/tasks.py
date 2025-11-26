"""Task status and polling routes."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

from server.db.database import get_db
from server.db.models import UserDB, TaskStatusDB
from server.api.dependencies import get_current_user

router = APIRouter(prefix="/tasks", tags=["tasks"])


class TaskStatusResponse(BaseModel):
    """Task status response schema."""
    task_id: str
    status: str
    progress_percent: int
    current_step: Optional[str]
    result: Optional[Dict[str, Any]]
    error_message: Optional[str]
    created_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True


@router.get("/{task_id}", response_model=TaskStatusResponse)
async def get_task_status(
    task_id: str,
    current_user: UserDB = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
) -> TaskStatusResponse:
    """
    Get the status of a background task.

    Args:
        task_id: The task ID
        current_user: Current authenticated user
        session: Database session

    Returns:
        Task status information

    Raises:
        HTTPException: If task not found or access denied
    """
    result = await session.execute(
        select(TaskStatusDB).where(
            TaskStatusDB.task_id == task_id,
            TaskStatusDB.user_id == current_user.id
        )
    )
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found or access denied"
        )

    return TaskStatusResponse(
        task_id=task.task_id,
        status=task.status,
        progress_percent=task.progress_percent,
        current_step=task.current_step,
        result=task.result_json,
        error_message=task.error_message,
        created_at=task.created_at,
        started_at=task.started_at,
        completed_at=task.completed_at
    )
