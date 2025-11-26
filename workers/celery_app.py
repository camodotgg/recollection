"""Celery application configuration for background tasks."""

import os
from celery import Celery

# Get Redis URL from environment
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# Create Celery app
celery_app = Celery(
    "recollection",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=[
        "workers.tasks.content_tasks",
        "workers.tasks.course_tasks",
    ]
)

# Configure Celery
celery_app.conf.update(
    # Serialization
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",

    # Task tracking
    task_track_started=True,
    task_send_sent_event=True,

    # Task execution
    task_acks_late=True,
    worker_prefetch_multiplier=1,  # One task at a time per worker
    task_time_limit=3600,  # 1 hour max
    task_soft_time_limit=3300,  # 55 minutes soft limit

    # Queues
    task_default_queue="default",
    task_create_missing_queues=True,

    # Results
    result_expires=3600,  # Keep results for 1 hour
    result_backend_transport_options={
        "master_name": "mymaster"
    },

    # Timezone
    timezone="UTC",
    enable_utc=True,
)

# Task routes (optional - route different tasks to different queues)
celery_app.conf.task_routes = {
    "workers.tasks.content_tasks.load_content_task": {"queue": "content_processing"},
    "workers.tasks.course_tasks.generate_course_task": {"queue": "course_generation"},
}
