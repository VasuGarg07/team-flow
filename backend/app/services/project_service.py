from pydantic import TypeAdapter
from sqlalchemy.orm import Session

import app.repositories.project_repository as project_repository
from app.schemas.project import ProjectCreate, ProjectUpdate, ProjectRead
from app.models import Project
from app.errors import NotFoundError
from app.cache import read_cache, write_cache

adapter = TypeAdapter(list[ProjectRead])

def create_project(db: Session, workspace_id: int, data: ProjectCreate) -> Project:
    project = Project(name=data.name, description=data.description)
    project.workspace_id = workspace_id
    return project_repository.create_project(db, project)

def list_projects(db: Session, workspace_id: int) -> list[ProjectRead]:
    # Check in cache first
    key = f"workspace:{workspace_id}:projects"
    text = read_cache(key)

    if text is not None:
        data = adapter.validate_json(text)
        return data

    projects = project_repository.list_projects(db, workspace_id)
    project_reads = [ProjectRead.model_validate(project) for project in projects]
    projects_text = adapter.dump_json(project_reads).decode()
    write_cache(key, projects_text)

    return projects

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