from sqlalchemy.orm import Session

import app.repositories.project_repository as project_repository
from app.schemas.project import ProjectCreate, ProjectUpdate
from app.models import Project
from app.errors import NotFoundError

def create_project(db: Session, workspace_id: int, data: ProjectCreate) -> Project:
    project = Project(name=data.name, description=data.description)
    project.workspace_id = workspace_id
    return project_repository.create_project(db, project)

def list_projects(db: Session, workspace_id: int) -> list[Project]:
    return project_repository.list_projects(db, workspace_id)

def get_project(db: Session, workspace_id: int, project_id: int) -> Project:
    project = project_repository.get_project(db, workspace_id, project_id)
    if project is None:
        raise NotFoundError("Project not found")
    return project

def update_project(db: Session, workspace_id: int, project_id: int, data: ProjectUpdate) -> Project:
    project = get_project(db, workspace_id, project_id)

    if data.name is not None:
        project.name = data.name
    if "description" in data.model_fields_set:
        project.description = data.description

    return project_repository.update_project(db, project)

def delete_project(db: Session, workspace_id: int, project_id: int) -> None:
    project = get_project(db, workspace_id, project_id)
    project_repository.delete_project(db, project)