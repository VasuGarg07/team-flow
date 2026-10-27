from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

import app.services.project_service as project_service
from app.schemas.project import ProjectRead, ProjectCreate, ProjectUpdate
from app.database import get_db
from app.dependencies import require_workspace_role
from app.models import Project, WorkspaceMember, WorkspaceMemberRole

router = APIRouter(prefix="/workspaces/{workspace_id}/projects", tags=["projects"])

@router.post("", response_model=ProjectRead, status_code=201)
def create_project_endpoint(
    data: ProjectCreate,
    workspace_id: int,
    db: Session = Depends(get_db), 
    member: WorkspaceMember = Depends(require_workspace_role(WorkspaceMemberRole.OWNER, WorkspaceMemberRole.ADMIN))
) -> Project:
    return project_service.create_project(db, workspace_id, data)

@router.get("", response_model=list[ProjectRead])
def list_projects_endpoint(
    workspace_id: int,
    db: Session = Depends(get_db), 
    member: WorkspaceMember = Depends(require_workspace_role(WorkspaceMemberRole.OWNER, WorkspaceMemberRole.ADMIN, WorkspaceMemberRole.MEMBER))
) -> list[ProjectRead]:
    return project_service.list_projects(db, workspace_id)

@router.get("/{project_id}", response_model=ProjectRead)
def get_project_endpoint(
    workspace_id: int,
    project_id: int,
    db: Session = Depends(get_db), 
    member: WorkspaceMember = Depends(require_workspace_role(WorkspaceMemberRole.OWNER, WorkspaceMemberRole.ADMIN, WorkspaceMemberRole.MEMBER))
) -> Project:
    return project_service.get_project(db, workspace_id, project_id)

@router.patch("/{project_id}", response_model=ProjectRead)
def update_project_endpoint(
    workspace_id: int,
    project_id: int,
    data: ProjectUpdate,
    db: Session = Depends(get_db), 
    member: WorkspaceMember = Depends(require_workspace_role(WorkspaceMemberRole.OWNER, WorkspaceMemberRole.ADMIN))
) -> Project:
    return project_service.update_project(db, workspace_id, project_id, data)

@router.delete("/{project_id}", status_code=204)
def delete_project_endpoint(
    workspace_id: int,
    project_id: int,
    db: Session = Depends(get_db), 
    member: WorkspaceMember = Depends(require_workspace_role(WorkspaceMemberRole.OWNER, WorkspaceMemberRole.ADMIN))
) -> None:
    return project_service.delete_project(db, workspace_id, project_id)
