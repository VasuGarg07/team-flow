from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Task, TaskStatus, TaskPriority

SORTABLE_COLUMNS = {
    "created_at": Task.created_at, 
    "due_date": Task.due_date,
    "priority": Task.priority, 
    "status": Task.status, 
    "story_points": Task.story_points, 
    "name": Task.name
}

def create_task(db: Session, task: Task) -> Task:
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


def list_tasks(
    db: Session, 
    project_id: int,
    status: TaskStatus | None,
    priority: TaskPriority | None,
    assignee_id: int | None,
    sort_by: str,
    descending: bool,
    page: int,
    limit: int
) -> tuple[list[Task], int]:
    statement = select(Task).where(Task.project_id == project_id)
    if status is not None:
        statement = statement.where(Task.status == status)
    if priority is not None:
        statement = statement.where(Task.priority == priority)
    if assignee_id is not None:
        statement = statement.where(Task.assignee_id == assignee_id)

    total = db.scalar(select(func.count()).select_from(statement.subquery()))
    sort_column = SORTABLE_COLUMNS[sort_by]
    if descending:
        statement = statement.order_by(sort_column.desc().nulls_last(), Task.id)
    else:
        statement = statement.order_by(sort_column.asc().nulls_last(), Task.id)

    statement = statement.offset((page - 1) * limit).limit(limit)
    tasks = list(db.scalars(statement).all())
    return tasks, total or 0


def get_task(db: Session, project_id: int, task_id: int) -> Task | None:
    statement = select(Task).where(Task.project_id == project_id, Task.id == task_id)
    return db.scalar(statement)


def update_task(db: Session, task: Task) -> Task:
    db.commit()
    db.refresh(task)
    return task


def delete_task(db: Session, task: Task) -> None:
    db.delete(task)
    db.commit()