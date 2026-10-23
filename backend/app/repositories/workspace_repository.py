from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models import Workspace, WorkspaceMember, WorkspaceMemberRole


def create_workspace_with_owner(db: Session, workspace: Workspace, member: WorkspaceMember) -> Workspace:
    db.add(workspace)
    db.flush()
    member.workspace_id = workspace.id

    db.add(member)
    db.commit()
    db.refresh(workspace)
    return workspace

def list_workspaces_for_user(db: Session, user_id: int) -> list[tuple[Workspace, WorkspaceMemberRole]]:
    statement = (
        select(Workspace, WorkspaceMember.role)
        .join(WorkspaceMember, WorkspaceMember.workspace_id == Workspace.id)
        .where(WorkspaceMember.user_id == user_id)
    )
    rows = db.execute(statement).all()

    result: list[tuple[Workspace, WorkspaceMemberRole]] = []
    for workspace, role in rows:
        result.append((workspace, role))
    return result


def get_member(db: Session, workspace_id: int, user_id: int) -> WorkspaceMember | None:
    statement = (
        select(WorkspaceMember)
        .where(WorkspaceMember.workspace_id == workspace_id, WorkspaceMember.user_id == user_id)
    )
    return db.scalar(statement)

def get_workspace_by_id(db: Session, workspace_id: int) -> Workspace | None:
    return db.get(Workspace, workspace_id)

def update_workspace_name(db: Session, workspace: Workspace, new_name: str) -> Workspace:
    workspace.name = new_name
    db.commit()
    db.refresh(workspace)
    return workspace

def delete_workspace(db: Session, workspace: Workspace) -> None:
    db.delete(workspace)
    db.commit()

def list_members(db: Session, workspace_id: int) -> list[WorkspaceMember]:
    statement = (
        select(WorkspaceMember)
        .where(WorkspaceMember.workspace_id == workspace_id)
    ).options(
        joinedload(WorkspaceMember.user)
    )

    return list(db.scalars(statement).all())

def add_member(db: Session, member: WorkspaceMember) -> WorkspaceMember:
    db.add(member)
    db.commit()
    db.refresh(member)
    return member

def update_member_role(db: Session, member: WorkspaceMember, new_role: WorkspaceMemberRole) -> WorkspaceMember:
    member.role = new_role
    db.commit()
    db.refresh(member)
    return member

def delete_member(db: Session, member: WorkspaceMember) -> None:
    db.delete(member)
    db.commit()