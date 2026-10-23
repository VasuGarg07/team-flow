from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

import app.services.task_service as task_service
from app.database import get_db
from app.dependencies import require_workspace_role
from app.models import Task, WorkspaceMember, WorkspaceMemberRole
from app.schemas.task import TaskCreate, TaskRead, TaskUpdate

router = APIRouter(prefix="/workspaces/{workspace_id}/projects/{project_id}/tasks", tags=["tasks"])

require_any_member = require_workspace_role(
    WorkspaceMemberRole.OWNER, WorkspaceMemberRole.ADMIN, WorkspaceMemberRole.MEMBER
)


@router.post("", response_model=TaskRead, status_code=201)
def create_task_endpoint(
    workspace_id: int,
    project_id: int,
    data: TaskCreate,
    db: Session = Depends(get_db),
    member: WorkspaceMember = Depends(require_any_member),
) -> Task:
    return task_service.create_task(db, workspace_id, project_id, member, data)


@router.get("", response_model=list[TaskRead])
def list_tasks_endpoint(
    workspace_id: int,
    project_id: int,
    db: Session = Depends(get_db),
    member: WorkspaceMember = Depends(require_any_member),
) -> list[Task]:
    return task_service.list_tasks(db, workspace_id, project_id)


@router.get("/{task_id}", response_model=TaskRead)
def get_task_endpoint(
    workspace_id: int,
    project_id: int,
    task_id: int,
    db: Session = Depends(get_db),
    member: WorkspaceMember = Depends(require_any_member),
) -> Task:
    return task_service.get_task(db, workspace_id, project_id, task_id)


@router.patch("/{task_id}", response_model=TaskRead)
def update_task_endpoint(
    workspace_id: int,
    project_id: int,
    task_id: int,
    data: TaskUpdate,
    db: Session = Depends(get_db),
    member: WorkspaceMember = Depends(require_any_member),
) -> Task:
    return task_service.update_task(db, workspace_id, project_id, task_id, member, data)


@router.delete("/{task_id}", status_code=204)
def delete_task_endpoint(
    workspace_id: int,
    project_id: int,
    task_id: int,
    db: Session = Depends(get_db),
    member: WorkspaceMember = Depends(require_any_member),
) -> None:
    task_service.delete_task(db, workspace_id, project_id, task_id, member)