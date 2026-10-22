from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

import app.services.workspace_service as workspace_service
from app.schemas.workspace import WorkspaceCreate, WorkspaceRead, WorkspaceUpdate
from app.database import get_db
from app.models import User, Workspace
from app.dependencies import get_current_user


router = APIRouter(prefix="/workspaces", tags=["workspaces"])

@router.post("", response_model=WorkspaceRead, status_code=201)
def create_workspace_endpoint(data: WorkspaceCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> WorkspaceRead:
    return workspace_service.create_workspace(db, data, current_user.id)

@router.get("", response_model=list[WorkspaceRead])
def list_workspaces_endpoint(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> list[Workspace]:
    return workspace_service.list_workspaces(db, current_user.id)

@router.get("/{workspace_id}", response_model=WorkspaceRead)
def get_workspace_endpoint(workspace_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> Workspace:
    return workspace_service.get_workspace(db, workspace_id, current_user.id)

@router.patch("/{workspace_id}", response_model=WorkspaceRead)
def rename_workspace_endpoint(data: WorkspaceUpdate, workspace_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> Workspace:
    return workspace_service.rename_workspace(db, workspace_id, current_user.id, data.name)

@router.delete("/{workspace_id}", response_model=WorkspaceRead)
def delete_workspace_endpoint(workspace_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> None:
    workspace_service.delete_workspace(db, workspace_id, current_user.id)
