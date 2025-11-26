"""Celery tasks for course generation."""

from celery import shared_task
from workers.celery_app import celery_app
from workers.monitoring import update_task_status_sync, publish_task_progress_sync
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
import os

# Import existing business logic
from src.course.generator import generate_course
from src.config import get_config
from src.content.models import Content, Summary, Source, Format
from server.db.models import ContentDB, CourseDB

# Database configuration - use sync psycopg2 for Celery tasks
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://user:password@localhost:5433/recollection")
# Convert asyncpg URL to psycopg2 URL for sync operations
SYNC_DATABASE_URL = DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://")
sync_engine = create_engine(SYNC_DATABASE_URL, echo=False, pool_pre_ping=True)
SyncSessionLocal = sessionmaker(sync_engine, expire_on_commit=False)


@shared_task(bind=True, name="workers.tasks.course_tasks.generate_course_task")
def generate_course_task(self, task_id: str, user_id: str, content_ids: list[str]):
    """
    Generate a course from one or more content items.

    Args:
        task_id: The task ID for tracking
        user_id: The user ID who initiated the task
        content_ids: List of content IDs to generate course from

    Returns:
        dict: Result with course_id
    """
    try:
        # Update status: STARTED
        update_task_status_sync(
            task_id,
            status="STARTED",
            progress=0,
            step="Initializing course generator..."
        )
        publish_task_progress_sync(task_id, "progress", {"percent": 0, "step": "Initializing..."})

        # Get LLM configuration
        config = get_config()
        llm = config.create_llm("course_generation")

        # Update progress
        update_task_status_sync(
            task_id,
            progress=10,
            step="Loading content from database..."
        )
        publish_task_progress_sync(task_id, "progress", {"percent": 10, "step": "Loading content..."})

        # Load content from database and convert to Pydantic models
        with SyncSessionLocal() as session:
            contents = []
            for content_id in content_ids:
                result = session.execute(
                    select(ContentDB).where(
                        ContentDB.id == content_id,
                        ContentDB.user_id == user_id
                    )
                )
                db_content = result.scalar_one_or_none()

                if not db_content:
                    raise ValueError(f"Content {content_id} not found or access denied")

                # Convert DB model to Pydantic model
                # Note: Using content created_at as source created_at since we don't store it separately
                source = Source(
                    link=db_content.source_link,
                    author=db_content.source_author,
                    origin=db_content.source_origin,
                    created_at=db_content.created_at,
                    format=Format(db_content.source_format) if db_content.source_format else None
                )

                summary = Summary.model_validate(db_content.summary_json)

                content = Content(
                    source=source,
                    summary=summary,
                    raw=db_content.raw_text,
                    metadata=db_content.metadata_json
                )
                contents.append(content)

        # Update progress
        update_task_status_sync(
            task_id,
            progress=30,
            step=f"Generating course from {len(contents)} content(s)..."
        )
        publish_task_progress_sync(
            task_id,
            "progress",
            {"percent": 30, "step": "Generating course..."}
        )

        # Call existing business logic
        course = generate_course(llm=llm, contents=contents)

        # Update progress
        update_task_status_sync(
            task_id,
            progress=80,
            step="Course generated successfully. Saving to database..."
        )
        publish_task_progress_sync(
            task_id,
            "progress",
            {"percent": 80, "step": "Saving to database..."}
        )

        # Save to database
        with SyncSessionLocal() as session:
            db_course = CourseDB(
                user_id=user_id,
                title=course.title,
                description=course.description,
                objective=course.objective,
                genre=course.genre.value if course.genre else "unknown",
                difficulty_level=course.difficulty_level.value if course.difficulty_level else "beginner",
                lessons_json=[lesson.model_dump(mode='json') for lesson in course.lessons],
                takeaways_json=[takeaway.model_dump(mode='json') for takeaway in course.takeaways],
                topics_json=[topic.model_dump(mode='json') for topic in course.topics],
                completion_criteria_json=course.completion_criteria.model_dump(mode='json'),
                source_content_json=[ref.model_dump(mode='json') for ref in course.source_content],
                estimated_duration_seconds=int(course.estimated_duration.total_seconds()),
            )
            session.add(db_course)
            session.commit()
            session.refresh(db_course)
            course_id = db_course.id

        # Update status: SUCCESS
        update_task_status_sync(
            task_id,
            status="SUCCESS",
            progress=100,
            step="Course generated successfully!",
            result={"course_id": course_id}
        )
        publish_task_progress_sync(
            task_id,
            "completed",
            {"course_id": course_id}
        )

        return {"course_id": course_id, "status": "success"}

    except Exception as e:
        error_msg = str(e)
        print(f"Error in generate_course_task: {error_msg}")

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
