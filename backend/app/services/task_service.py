from sqlalchemy.orm import Session

import app.repositories.task_repository as task_repository
import app.repositories.workspace_repository as workspace_repository
import app.services.project_service as project_service
from app.errors import BadRequestError, ForbiddenError, NotFoundError
from app.models import Task, WorkspaceMember, WorkspaceMemberRole, TaskStatus, TaskPriority
from app.schemas.task import TaskCreate, TaskPage, TaskRead, TaskUpdate
from app.queue import enqueue_assignment_notification


def ensure_workspace_member(db: Session, workspace_id: int, user_id: int) -> None:
    member = workspace_repository.get_member(db, workspace_id, user_id)
    if member is None:
        raise BadRequestError("Assignee must be a member of this workspace")

def can_change_task(caller: WorkspaceMember, task: Task) -> bool:
    return (caller.role in [WorkspaceMemberRole.ADMIN, WorkspaceMemberRole.OWNER]) or task.reporter_id == caller.user_id


def list_tasks(
    db: Session, 
    workspace_id: int, 
    project_id: int,
    status: TaskStatus | None,
    priority: TaskPriority | None,
    assignee_id: int | None,
    sort_by: str,
    descending: bool,
    page: int,
    limit: int
) -> TaskPage:
    project_service.get_project(db, workspace_id, project_id)
    tasks, total = task_repository.list_tasks(
        db, project_id, status, priority, assignee_id, sort_by, descending, page, limit
    )

    items: list[TaskRead] = []
    for task in tasks:
        items.append(TaskRead.model_validate(task))
    return TaskPage(items=items, total=total, page=page, limit=limit)


def get_task(db: Session, workspace_id: int, project_id: int, task_id: int) -> Task:
    project_service.get_project(db, workspace_id, project_id)
    task = task_repository.get_task(db, project_id, task_id)
    if task is None:
        raise NotFoundError("Task not found")
    return task

def create_task(db: Session, workspace_id: int, project_id: int, caller: WorkspaceMember, data: TaskCreate) -> Task:
    project_service.get_project(db, workspace_id, project_id)
    if data.assignee_id is not None:
        ensure_workspace_member(db, workspace_id, data.assignee_id)
        
    task = Task(
    project_id=project_id,
    name=data.name,
    description=data.description,
    assignee_id=data.assignee_id,
    reporter_id=caller.user_id,
    priority=data.priority,
    story_points=data.story_points,
    due_date=data.due_date
    )

    created = task_repository.create_task(db, task)
    if created.assignee_id is not None and created.assignee_id != caller.user_id:
        enqueue_assignment_notification(task_id=created.id)
    return created

def update_task(db: Session, workspace_id: int, project_id: int, task_id: int, caller: WorkspaceMember, data: TaskUpdate) -> Task:
    task = get_task(db, workspace_id, project_id, task_id)
    if not (can_change_task(caller, task) or task.assignee_id == caller.user_id):
        raise ForbiddenError("You do not have access to do this")

    old_assignee_id = task.assignee_id

    if "assignee_id" in data.model_fields_set:
        if data.assignee_id is not None:
            ensure_workspace_member(db, workspace_id, data.assignee_id)
        task.assignee_id = data.assignee_id
    if "description" in data.model_fields_set:
        task.description = data.description
    if "due_date" in data.model_fields_set:
        task.due_date = data.due_date
    if data.name is not None:
        task.name = data.name
    if data.status is not None:
        task.status = data.status
    if data.priority is not None:
        task.priority = data.priority
    if data.story_points is not None:
        task.story_points = data.story_points

    updated = task_repository.update_task(db, task)
    if updated.assignee_id is not None and updated.assignee_id != old_assignee_id and updated.assignee_id != caller.user_id:
        enqueue_assignment_notification(task_id=updated.id)
    return updated
    
def delete_task(db: Session, workspace_id: int, project_id: int, task_id: int, caller: WorkspaceMember) -> None:
    task = get_task(db, workspace_id, project_id, task_id)
    if not can_change_task(caller, task):
        raise ForbiddenError("You do not have access to do this")
    task_repository.delete_task(db, task)

