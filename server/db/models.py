"""SQLAlchemy ORM models for the database."""

from sqlalchemy import Column, String, Boolean, DateTime, Text, Integer, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func
from datetime import datetime
import uuid
import enum

from .database import Base


class UserDB(Base):
    """User model for authentication and ownership."""

    __tablename__ = "users"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4()))
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    contents = relationship("ContentDB", back_populates="user", cascade="all, delete-orphan")
    courses = relationship("CourseDB", back_populates="user", cascade="all, delete-orphan")
    tasks = relationship("TaskStatusDB", back_populates="user", cascade="all, delete-orphan")


class SourceFormat(str, enum.Enum):
    """Content source format types."""
    PDF = "pdf"
    WEB = "web"
    YOUTUBE = "youtube"
    TEXT = "text"


class ContentDB(Base):
    """Content model for storing loaded content."""

    __tablename__ = "contents"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    # Source information
    source_link: Mapped[str | None] = mapped_column(Text, nullable=True)
    source_author: Mapped[str | None] = mapped_column(String, nullable=True)
    source_origin: Mapped[str | None] = mapped_column(String, nullable=True)
    source_format: Mapped[str | None] = mapped_column(SQLEnum(SourceFormat), nullable=True)

    # Content data (stored as JSONB for Pydantic models)
    summary_json: Mapped[dict] = mapped_column(JSONB, nullable=False)
    raw_text: Mapped[str] = mapped_column(Text, nullable=False)
    metadata_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    analyzed_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)  # AnalyzedContent (genre, topics)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    user = relationship("UserDB", back_populates="contents")


class DifficultyLevel(str, enum.Enum):
    """Course difficulty levels."""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class CourseDB(Base):
    """Course model for storing generated courses."""

    __tablename__ = "courses"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    # Course metadata
    title: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    objective: Mapped[str] = mapped_column(Text, nullable=False)
    genre: Mapped[str] = mapped_column(String, nullable=False)
    difficulty_level: Mapped[str] = mapped_column(SQLEnum(DifficultyLevel), nullable=False)

    # Course structure (stored as JSONB for Pydantic models)
    lessons_json: Mapped[list] = mapped_column(JSONB, nullable=False)  # Lesson[] Pydantic models
    takeaways_json: Mapped[list] = mapped_column(JSONB, nullable=False)  # Takeaway[] Pydantic models
    topics_json: Mapped[list] = mapped_column(JSONB, nullable=False)  # Topic[] Pydantic models
    completion_criteria_json: Mapped[dict] = mapped_column(JSONB, nullable=False)  # CompletionCriteria Pydantic model
    source_content_json: Mapped[list] = mapped_column(JSONB, nullable=False)  # ContentReference[] Pydantic models

    # Duration
    estimated_duration_seconds: Mapped[int] = mapped_column(Integer, nullable=False)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    user = relationship("UserDB", back_populates="courses")


class TaskStatus(str, enum.Enum):
    """Task status types."""
    PENDING = "PENDING"
    STARTED = "STARTED"
    PROGRESS = "PROGRESS"
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"


class TaskStatusDB(Base):
    """Task status model for tracking background jobs."""

    __tablename__ = "task_status"

    task_id: Mapped[str] = mapped_column(String(255), primary_key=True)
    user_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    # Status information
    status: Mapped[str] = mapped_column(SQLEnum(TaskStatus), nullable=False, default=TaskStatus.PENDING)
    progress_percent: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    current_step: Mapped[str | None] = mapped_column(String, nullable=True)

    # Result and error
    result_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    user = relationship("UserDB", back_populates="tasks")


class CourseProgressDB(Base):
    """Course progress tracking for users."""

    __tablename__ = "course_progress"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    course_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("courses.id", ondelete="CASCADE"), nullable=False, index=True)

    # Progress tracking
    is_started: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    completion_percent: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Timestamps
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_accessed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Metadata
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    user = relationship("UserDB")
    course = relationship("CourseDB")
    lesson_progress = relationship("LessonProgressDB", back_populates="course_progress", cascade="all, delete-orphan")


class LessonProgressDB(Base):
    """Lesson progress tracking within a course."""

    __tablename__ = "lesson_progress"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4()))
    course_progress_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("course_progress.id", ondelete="CASCADE"), nullable=False, index=True)

    # Lesson identification (stored as index since lessons are in JSONB)
    lesson_index: Mapped[int] = mapped_column(Integer, nullable=False)
    lesson_title: Mapped[str] = mapped_column(String, nullable=False)

    # Completion tracking
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    completed_manually: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)  # True if user clicked "mark complete"
    completed_automatically: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)  # True if criteria were met

    # Time tracking
    time_spent_seconds: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Activity tracking
    activities_completed: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_activities: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Timestamps
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # User notes
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    course_progress = relationship("CourseProgressDB", back_populates="lesson_progress")
