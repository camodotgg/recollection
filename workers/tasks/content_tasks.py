"""Celery tasks for content loading."""

from celery import shared_task
from workers.celery_app import celery_app
from workers.monitoring import update_task_status_sync, publish_task_progress_sync
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
import os

# Import existing business logic
from src.content.loader.magic import load
from src.config import get_config
from server.db.models import ContentDB

# Database configuration - Use synchronous database for Celery tasks
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://user:password@localhost:5433/recollection")
SYNC_DATABASE_URL = DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://")
sync_engine = create_engine(SYNC_DATABASE_URL, echo=False, pool_pre_ping=True)
SyncSessionLocal = sessionmaker(sync_engine, expire_on_commit=False)


@shared_task(bind=True, name="workers.tasks.content_tasks.load_content_task")
def load_content_task(self, task_id: str, user_id: str, url: str):
    """
    Load content from a URL using the existing magic loader.

    Args:
        task_id: The task ID for tracking
        user_id: The user ID who initiated the task
        url: The URL to load content from

    Returns:
        dict: Result with content_id
    """
    try:
        # Update status: STARTED
        update_task_status_sync(
            task_id,
            status="STARTED",
            progress=0,
            step="Initializing content loader..."
        )
        publish_task_progress_sync(task_id, "progress", {"percent": 0, "step": "Initializing..."})

        # Get LLM configuration
        config = get_config()
        llm = config.create_llm("summarization")

        # Update progress
        update_task_status_sync(
            task_id,
            progress=10,
            step=f"Loading content from {url}..."
        )
        publish_task_progress_sync(task_id, "progress", {"percent": 10, "step": "Loading content..."})

        # Call existing business logic
        content = load(llm, url)

        # Update progress
        update_task_status_sync(
            task_id,
            progress=75,
            step="Content loaded successfully. Saving to database..."
        )
        publish_task_progress_sync(task_id, "progress", {"percent": 75, "step": "Saving to database..."})

        # Save to database using synchronous session
        with SyncSessionLocal() as session:
            db_content = ContentDB(
                user_id=user_id,
                source_link=content.source.link if content.source else url,
                source_author=content.source.author if content.source else None,
                source_origin=content.source.origin if content.source else None,
                source_format=content.source.format.value if content.source and content.source.format else None,
                summary_json=content.summary.model_dump(mode='json') if content.summary else {},
                raw_text=content.raw,
                metadata_json=content.metadata if content.metadata else {},
                analyzed_json=None,  # Will be populated later if needed
            )
            session.add(db_content)
            session.commit()
            session.refresh(db_content)
            content_id = db_content.id

        # Update status: SUCCESS
        update_task_status_sync(
            task_id,
            status="SUCCESS",
            progress=100,
            step="Content loaded successfully!",
            result={"content_id": content_id}
        )
        publish_task_progress_sync(
            task_id,
            "completed",
            {"content_id": content_id}
        )

        return {"content_id": content_id, "status": "success"}

    except Exception as e:
        error_msg = str(e)
        print(f"Error in load_content_task: {error_msg}")

        # Update status: FAILURE
        update_task_status_sync(
            task_id,
            status="FAILURE",
            error=error_msg
        )
        publish_task_progress_sync(
            task_id,
            "failed",
            {"error": error_msg}
        )

        # Re-raise so Celery marks it as failed
        raise
