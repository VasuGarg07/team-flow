from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

import app.services.workspace_service as workspace_service
from app.schemas.workspace import WorkspaceCreate, WorkspaceDetail, WorkspaceRead, WorkspaceUpdate, WorkspaceMemberRead, WorkspaceMemberRoleUpdate, WorkspaceMemberAdd
from app.database import get_db
from app.models import User, Workspace, WorkspaceMember, WorkspaceMemberRole
from app.dependencies import get_current_user, require_workspace_role


router = APIRouter(prefix="/workspaces", tags=["workspaces"])

@router.post("", response_model=WorkspaceRead, status_code=201)
def create_workspace_endpoint(
    data: WorkspaceCreate, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
) -> Workspace:
    return workspace_service.create_workspace(db, data, current_user.id)

@router.get("", response_model=list[WorkspaceDetail])
def list_workspaces_endpoint(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> list[WorkspaceDetail]:
    return workspace_service.list_workspaces(db, current_user.id)


@router.get("/{workspace_id}", response_model=WorkspaceDetail)
def get_workspace_endpoint(
    workspace_id: int,
    db: Session = Depends(get_db),
    member: WorkspaceMember = Depends(require_workspace_role(WorkspaceMemberRole.OWNER, WorkspaceMemberRole.ADMIN, WorkspaceMemberRole.MEMBER))
) -> WorkspaceDetail:
    return workspace_service.get_workspace_detail(db, workspace_id, member.role)

@router.patch("/{workspace_id}", response_model=WorkspaceRead)
def rename_workspace_endpoint(
    data: WorkspaceUpdate, 
    workspace_id: int, 
    db: Session = Depends(get_db), 
    member: WorkspaceMember = Depends(require_workspace_role(WorkspaceMemberRole.OWNER, WorkspaceMemberRole.ADMIN))
) -> Workspace:
    return workspace_service.rename_workspace(db, workspace_id, data.name)

@router.delete("/{workspace_id}", status_code=204)
def delete_workspace_endpoint(
    workspace_id: int, 
    db: Session = Depends(get_db), 
    member: WorkspaceMember = Depends(require_workspace_role(WorkspaceMemberRole.OWNER))
) -> None:
    workspace_service.delete_workspace(db, workspace_id)

@router.get("/{workspace_id}/members", response_model=list[WorkspaceMemberRead])
def list_members_endpoint(
    workspace_id: int, 
    db: Session = Depends(get_db), 
    member: WorkspaceMember = Depends(require_workspace_role(WorkspaceMemberRole.OWNER, WorkspaceMemberRole.ADMIN, WorkspaceMemberRole.MEMBER))
) -> list[WorkspaceMember]:
    return workspace_service.list_members(db, workspace_id)

@router.post("/{workspace_id}/members", response_model=WorkspaceMemberRead, status_code=201)
def add_member_endpoint(
    workspace_id: int,
    data: WorkspaceMemberAdd,
    db: Session = Depends(get_db),
    member: WorkspaceMember = Depends(
        require_workspace_role(WorkspaceMemberRole.OWNER, WorkspaceMemberRole.ADMIN)
    ),
) -> WorkspaceMember:
    return workspace_service.add_member(db, workspace_id, member.role, data)


@router.patch("/{workspace_id}/members/{target_user_id}", response_model=WorkspaceMemberRead)
def change_member_role_endpoint(
    workspace_id: int,
    target_user_id: int,
    data: WorkspaceMemberRoleUpdate,
    db: Session = Depends(get_db),
    member: WorkspaceMember = Depends(require_workspace_role(WorkspaceMemberRole.OWNER)),
) -> WorkspaceMember:
    return workspace_service.change_member_role(db, workspace_id, target_user_id, data.role)


@router.delete("/{workspace_id}/members/{target_user_id}", status_code=204)
def remove_member_endpoint(
    workspace_id: int,
    target_user_id: int,
    db: Session = Depends(get_db),
    member: WorkspaceMember = Depends(
        require_workspace_role(WorkspaceMemberRole.OWNER, WorkspaceMemberRole.ADMIN)
    ),
) -> None:
    workspace_service.remove_member(db, workspace_id, target_user_id, member.role)
