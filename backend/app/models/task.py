from datetime import datetime
from enum import Enum

from sqlalchemy import ForeignKey, Index, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from .user import User

class TaskStatus(str, Enum):
    OPEN = "OPEN"
    IN_PROGRESS = "IN_PROGRESS"
    TESTING = "TESTING"
    LIVE = "LIVE"
    VOID = "VOID"

class TaskPriority(str, Enum):
    LIVE_ISSUE = "LIVE_ISSUE"
    BLOCKER = "BLOCKER"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"

class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"))
    name: Mapped[str] = mapped_column(String(100))
    description: Mapped[str | None] = mapped_column(String(1000))
    assignee_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    reporter_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    assignee: Mapped[User | None] = relationship(foreign_keys="Task.assignee_id")
    reporter: Mapped[User] = relationship(foreign_keys="Task.reporter_id")

    status: Mapped[TaskStatus] = mapped_column(default=TaskStatus.OPEN)
    priority: Mapped[TaskPriority] = mapped_column(default=TaskPriority.HIGH)
    story_points: Mapped[int] = mapped_column(default=1)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())
    due_date: Mapped[datetime | None] = mapped_column()

    __table_args__ = (
        Index("idx_tasks_project_status_created", "project_id", "status", "created_at"),
    )
