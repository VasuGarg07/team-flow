import pytest

from app.models import Task, WorkspaceMember, WorkspaceMemberRole
from app.services.task_service import can_change_task


def make_member(user_id: int, role: WorkspaceMemberRole) -> WorkspaceMember:
    return WorkspaceMember(user_id=user_id, workspace_id=1, role=role)


@pytest.fixture
def task() -> Task:
    return Task(project_id=1, name="Fix login", reporter_id=1, assignee_id=2)


def test_owner_can_change_any_task(task: Task) -> None:
    owner = make_member(10, WorkspaceMemberRole.OWNER)
    assert can_change_task(owner, task) is True


def test_admin_can_change_any_task(task: Task) -> None:
    admin = make_member(11, WorkspaceMemberRole.ADMIN)
    assert can_change_task(admin, task) is True


def test_member_can_change_a_task_they_reported(task: Task) -> None:
    reporter = make_member(1, WorkspaceMemberRole.MEMBER)
    assert can_change_task(reporter, task) is True


def test_member_cannot_change_a_task_someone_else_reported(task: Task) -> None:
    stranger = make_member(3, WorkspaceMemberRole.MEMBER)
    assert can_change_task(stranger, task) is False


def test_member_who_is_only_the_assignee_fails_this_check_because_update_task_adds_its_own_rule(task: Task) -> None:
    assignee = make_member(2, WorkspaceMemberRole.MEMBER)
    assert can_change_task(assignee, task) is False