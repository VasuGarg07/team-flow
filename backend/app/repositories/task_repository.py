from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Task


def create_task(db: Session, task: Task) -> Task:
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


def list_tasks(db: Session, project_id: int) -> list[Task]:
    statement = select(Task).where(Task.project_id == project_id)
    return list(db.scalars(statement).all())


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