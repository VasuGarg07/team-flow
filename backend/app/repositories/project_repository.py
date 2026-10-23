from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Project

def create_project(db: Session, project: Project) -> Project:
    db.add(project)
    db.commit()
    db.refresh(project)
    return project

def list_projects(db: Session, workspace_id: int) -> list[Project]:
    statement = select(Project).where(Project.workspace_id == workspace_id)
    return list(db.scalars(statement).all())

def get_project(db: Session, workspace_id: int, project_id: int) -> Project | None:
    statement = select(Project).where(Project.workspace_id == workspace_id, Project.id == project_id)
    return db.scalar(statement)

def update_project(db: Session, project: Project) -> Project:
    db.commit()
    db.refresh(project)
    return project

def delete_project(db: Session, project: Project) -> None:
    db.delete(project)
    db.commit()