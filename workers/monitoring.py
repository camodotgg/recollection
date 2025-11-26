"""Task monitoring and status tracking utilities."""

import asyncio
from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
import os
import redis
import json

from server.db.models import TaskStatusDB, TaskStatus

# Database configuration - use sync psycopg2 for Celery tasks
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://user:password@localhost:5433/recollection")
# Convert asyncpg URL to psycopg2 URL for sync operations
SYNC_DATABASE_URL = DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://")
sync_engine = create_engine(SYNC_DATABASE_URL, echo=False, pool_pre_ping=True)
SyncSessionLocal = sessionmaker(sync_engine, expire_on_commit=False)

# Redis configuration for pub/sub
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")


async def update_task_status(
    task_id: str,
    status: Optional[str] = None,
    progress: Optional[int] = None,
    step: Optional[str] = None,
    result: Optional[Dict[str, Any]] = None,
    error: Optional[str] = None
):
    """
    Update task status in the database.

    Args:
        task_id: The task ID
        status: New status (PENDING, STARTED, PROGRESS, SUCCESS, FAILURE)
        progress: Progress percentage (0-100)
        step: Current step description
        result: Result data (for SUCCESS status)
        error: Error message (for FAILURE status)
    """
    async with AsyncSessionLocal() as session:
        # Get existing task
        result_db = await session.execute(
            select(TaskStatusDB).where(TaskStatusDB.task_id == task_id)
        )
        task = result_db.scalar_one_or_none()

        if not task:
            return

        # Update fields
        if status:
            task.status = status
            if status == TaskStatus.STARTED:
                task.started_at = datetime.utcnow()
            elif status in [TaskStatus.SUCCESS, TaskStatus.FAILURE]:
                task.completed_at = datetime.utcnow()

        if progress is not None:
            task.progress_percent = progress

        if step is not None:
            task.current_step = step

        if result is not None:
            task.result_json = result

        if error is not None:
            task.error_message = error

        await session.commit()


async def publish_task_progress(task_id: str, event: str, data: Optional[Dict[str, Any]] = None):
    """
    Publish task progress event to Redis pub/sub for WebSocket clients.

    Args:
        task_id: The task ID
        event: Event type (progress, completed, failed)
        data: Additional event data
    """
    try:
        redis_client = await aioredis.from_url(REDIS_URL)
        channel = f"task:{task_id}"
        message = {
            "event": event,
            "task_id": task_id,
            **(data or {})
        }
        await redis_client.publish(channel, json.dumps(message))
        await redis_client.close()
    except Exception as e:
        print(f"Error publishing task progress: {e}")


def update_task_status_sync(
    task_id: str,
    status: Optional[str] = None,
    progress: Optional[int] = None,
    step: Optional[str] = None,
    result: Optional[Dict[str, Any]] = None,
    error: Optional[str] = None
):
    """
    Synchronous version for Celery tasks.
    Use this in Celery tasks (non-async context).
    """
    with SyncSessionLocal() as session:
        # Get existing task
        task = session.execute(
            select(TaskStatusDB).where(TaskStatusDB.task_id == task_id)
        ).scalar_one_or_none()

        if not task:
            return

        # Update fields
        if status:
            task.status = status
            if status == TaskStatus.STARTED:
                task.started_at = datetime.utcnow()
            elif status in [TaskStatus.SUCCESS, TaskStatus.FAILURE]:
                task.completed_at = datetime.utcnow()

        if progress is not None:
            task.progress_percent = progress

        if step is not None:
            task.current_step = step

        if result is not None:
            task.result_json = result

        if error is not None:
            task.error_message = error

        session.commit()


def publish_task_progress_sync(task_id: str, event: str, data: Optional[Dict[str, Any]] = None):
    """
    Synchronous version for Celery tasks.
    Use this in Celery tasks (non-async context).
    """
    try:
        redis_client = redis.from_url(REDIS_URL)
        channel = f"task:{task_id}"
        message = {
            "event": event,
            "task_id": task_id,
            **(data or {})
        }
        result = redis_client.publish(channel, json.dumps(message))
        print(f"Published to Redis channel {channel}: {message} (subscribers: {result})")
        redis_client.close()
    except Exception as e:
        print(f"Error publishing task progress: {e}")
        import traceback
        traceback.print_exc()
