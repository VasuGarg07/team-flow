from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models import TaskPriority, TaskStatus


class TaskCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=1000)
    assignee_id: int | None = None
    priority: TaskPriority = TaskPriority.MEDIUM
    story_points: int = Field(default=1, ge=1, le=100)
    due_date: datetime | None = None


class TaskUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=1000)
    assignee_id: int | None = None
    status: TaskStatus | None = None
    priority: TaskPriority | None = None
    story_points: int | None = Field(default=None, ge=1, le=100)
    due_date: datetime | None = None


class TaskRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    project_id: int
    name: str
    description: str | None
    assignee_id: int | None
    reporter_id: int
    status: TaskStatus
    priority: TaskPriority
    story_points: int
    due_date: datetime | None
    created_at: datetime
    updated_at: datetime


class TaskPage(BaseModel):
    items: list[TaskRead]
    total: int
    page: int
    limit: int