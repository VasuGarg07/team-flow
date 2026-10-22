from sqlalchemy.orm import Session

import app.repositories.workspace_repository as workspace_repository
from app.schemas.workspace import WorkspaceCreate, WorkspaceRead, WorkspaceUpdate
from app.models import Workspace, WorkspaceMember, WorkspaceMemberRole
from app.errors import NotFoundError, ForbiddenError

def create_workspace(db: Session, data: WorkspaceCreate, user_id: int) -> Workspace:
    workspace = Workspace(name=data.name)
    workspace_member = WorkspaceMember(user_id=user_id, role=WorkspaceMemberRole.OWNER)
    return workspace_repository.create_workspace_with_owner(db, workspace, workspace_member)

def list_workspaces(db: Session, user_id: int) -> list[Workspace]:
    return workspace_repository.list_workspaces_for_user(db, user_id)

def get_workspace(db: Session, workspace_id: int, user_id: int) -> Workspace:
    member = workspace_repository.get_member(db, workspace_id, user_id)
    if member is None:
        raise NotFoundError("Workspace not found")

    workspace = workspace_repository.get_workspace_by_id(db, workspace_id)
    if workspace is None:
        raise NotFoundError("Workspace not found")

    return workspace

def rename_workspace(db: Session, workspace_id: int, user_id: int, new_name: str) -> Workspace:
    member = workspace_repository.get_member(db, workspace_id, user_id)
    if member is None:
        raise NotFoundError("Workspace not found")

    if member.role != WorkspaceMemberRole.OWNER:
        raise ForbiddenError("Only workspace owner can rename workspace")

    workspace = workspace_repository.get_workspace_by_id(db, workspace_id)
    if workspace is None:
        raise NotFoundError("Workspace not found")

    return workspace_repository.update_workspace_name(db, workspace, new_name.strip())

def delete_workspace(db: Session, workspace_id: int, user_id: int) -> None:
    member = workspace_repository.get_member(db, workspace_id, user_id)
    if member is None:
        raise NotFoundError("Workspace not found")

    if member.role != WorkspaceMemberRole.OWNER:
        raise ForbiddenError("Only workspace owner can delete workspace")

    workspace = workspace_repository.get_workspace_by_id(db, workspace_id)
    if workspace is None:
        raise NotFoundError("Workspace not found")

    workspace_repository.delete_workspace(db, workspace)