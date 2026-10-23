from sqlalchemy.orm import Session

import app.repositories.workspace_repository as workspace_repository
from app.repositories.user_repository import get_user_by_email
from app.schemas.workspace import WorkspaceCreate, WorkspaceDetail, WorkspaceMemberAdd
from app.models import Workspace, WorkspaceMember, WorkspaceMemberRole
from app.errors import NotFoundError, BadRequestError, ForbiddenError, ConflictError

def create_workspace(db: Session, data: WorkspaceCreate, user_id: int) -> Workspace:
    workspace = Workspace(name=data.name)
    workspace_member = WorkspaceMember(user_id=user_id, role=WorkspaceMemberRole.OWNER)
    return workspace_repository.create_workspace_with_owner(db, workspace, workspace_member)

def list_workspaces(db: Session, user_id: int) -> list[WorkspaceDetail]:
    rows = workspace_repository.list_workspaces_for_user(db, user_id)
    result: list[WorkspaceDetail] = []
    for workspace, role in rows:
        result.append(WorkspaceDetail(
            id=workspace.id, 
            name=workspace.name, 
            created_at=workspace.created_at, 
            role=role
        ))
    return result

def get_workspace(db: Session, workspace_id: int) -> Workspace:
    workspace = workspace_repository.get_workspace_by_id(db, workspace_id)
    if workspace is None:
        raise NotFoundError("Workspace not found")
    return workspace

def get_workspace_detail(db: Session, workspace_id: int, role: WorkspaceMemberRole) -> WorkspaceDetail:
    workspace = get_workspace(db, workspace_id)
    return WorkspaceDetail(id=workspace.id, name=workspace.name, created_at=workspace.created_at, role=role)

def rename_workspace(db: Session, workspace_id: int, new_name: str) -> Workspace:
    workspace = get_workspace(db, workspace_id)
    return workspace_repository.update_workspace_name(db, workspace, new_name.strip())

def delete_workspace(db: Session, workspace_id: int) -> None:
    workspace = get_workspace(db, workspace_id)
    workspace_repository.delete_workspace(db, workspace)

def list_members(db: Session, workspace_id: int) -> list[WorkspaceMember]:
    return workspace_repository.list_members(db, workspace_id)

def add_member(db: Session, workspace_id: int, caller_role: WorkspaceMemberRole, data: WorkspaceMemberAdd) -> WorkspaceMember:
    if data.role == WorkspaceMemberRole.OWNER:
        raise BadRequestError("A workspace can only have one owner")
    if data.role == WorkspaceMemberRole.ADMIN and caller_role != WorkspaceMemberRole.OWNER:
        raise ForbiddenError("Only the owner can add an admin")

    user = get_user_by_email(db, data.email.strip().lower())
    if user is None:
        raise NotFoundError("User not found")

    if workspace_repository.get_member(db, workspace_id, user.id) is not None:
        raise ConflictError("User is already a member")

    member = WorkspaceMember(user_id=user.id, workspace_id=workspace_id, role=data.role)
    return workspace_repository.add_member(db, member)


def remove_member(db: Session, workspace_id: int, target_user_id: int, caller_role: WorkspaceMemberRole) -> None:
    target = workspace_repository.get_member(db, workspace_id, target_user_id)
    if target is None:
        raise NotFoundError("Member not found")
    if target.role == WorkspaceMemberRole.OWNER:
        raise BadRequestError("The owner cannot be removed")
    if caller_role == WorkspaceMemberRole.ADMIN and target.role != WorkspaceMemberRole.MEMBER:
        raise ForbiddenError("An admin can only remove members")

    workspace_repository.delete_member(db, target)

def change_member_role(db: Session, workspace_id: int, target_user_id: int, new_role: WorkspaceMemberRole) -> WorkspaceMember:
    if new_role == WorkspaceMemberRole.OWNER:
        raise BadRequestError("A workspace can only have one owner")

    target = workspace_repository.get_member(db, workspace_id, target_user_id)
    if target is None:
        raise NotFoundError("Member not found")
    if target.role == WorkspaceMemberRole.OWNER:
        raise BadRequestError("The owner's role cannot be changed")

    return workspace_repository.update_member_role(db, target, new_role)