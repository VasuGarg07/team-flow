from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Workspace, WorkspaceMember


def create_workspace_with_owner(db: Session, workspace: Workspace, member: WorkspaceMember) -> Workspace:
    db.add(workspace)
    db.flush()
    member.workspace_id = workspace.id

    db.add(member)
    db.commit()
    db.refresh(workspace)
    return workspace

def list_workspaces_for_user(db: Session, user_id: int) -> list[Workspace]:
    statement = (
        select(Workspace)
        .join(WorkspaceMember, WorkspaceMember.workspace_id == Workspace.id)
        .where(WorkspaceMember.user_id == user_id)
    )
    return list(db.scalars(statement).all())

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