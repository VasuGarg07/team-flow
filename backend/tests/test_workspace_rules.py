import pytest
from sqlalchemy.orm import Session

import app.repositories.workspace_repository as workspace_repository
import app.services.workspace_service as workspace_service
from app.errors import BadRequestError, ForbiddenError, NotFoundError
from app.models import WorkspaceMember, WorkspaceMemberRole


def make_member(role: WorkspaceMemberRole) -> WorkspaceMember:
    return WorkspaceMember(user_id=5, workspace_id=1, role=role)


@pytest.fixture
def db() -> Session:
    return Session()


def stub_repository(monkeypatch: pytest.MonkeyPatch, target: WorkspaceMember | None) -> list[WorkspaceMember]:
    deleted: list[WorkspaceMember] = []
    monkeypatch.setattr(workspace_repository, "get_member", lambda db, workspace_id, user_id: target)
    monkeypatch.setattr(workspace_repository, "delete_member", lambda db, member: deleted.append(member))
    monkeypatch.setattr(workspace_repository, "update_member_role", lambda db, member, new_role: member)
    return deleted


def test_removing_the_owner_is_rejected(monkeypatch: pytest.MonkeyPatch, db: Session) -> None:
    deleted = stub_repository(monkeypatch, make_member(WorkspaceMemberRole.OWNER))
    with pytest.raises(BadRequestError):
        workspace_service.remove_member(db, 1, 5, WorkspaceMemberRole.OWNER)
    assert deleted == []


def test_removing_someone_who_is_not_a_member_is_rejected(monkeypatch: pytest.MonkeyPatch, db: Session) -> None:
    deleted = stub_repository(monkeypatch, None)
    with pytest.raises(NotFoundError):
        workspace_service.remove_member(db, 1, 5, WorkspaceMemberRole.OWNER)
    assert deleted == []


def test_an_admin_cannot_remove_another_admin(monkeypatch: pytest.MonkeyPatch, db: Session) -> None:
    deleted = stub_repository(monkeypatch, make_member(WorkspaceMemberRole.ADMIN))
    with pytest.raises(ForbiddenError):
        workspace_service.remove_member(db, 1, 5, WorkspaceMemberRole.ADMIN)
    assert deleted == []


@pytest.mark.parametrize(
    "caller_role, target_role",
    [
        (WorkspaceMemberRole.OWNER, WorkspaceMemberRole.MEMBER),
        (WorkspaceMemberRole.OWNER, WorkspaceMemberRole.ADMIN),
        (WorkspaceMemberRole.ADMIN, WorkspaceMemberRole.MEMBER),
    ],
    ids=["owner_removes_member", "owner_removes_admin", "admin_removes_member"],
)
def test_allowed_removals_delete_the_member_once(
    monkeypatch: pytest.MonkeyPatch, db: Session, caller_role: WorkspaceMemberRole, target_role: WorkspaceMemberRole
) -> None:
    target = make_member(target_role)
    deleted = stub_repository(monkeypatch, target)
    workspace_service.remove_member(db, 1, 5, caller_role)
    assert deleted == [target]


def test_changing_a_role_to_owner_is_rejected(monkeypatch: pytest.MonkeyPatch, db: Session) -> None:
    stub_repository(monkeypatch, make_member(WorkspaceMemberRole.MEMBER))
    with pytest.raises(BadRequestError):
        workspace_service.change_member_role(db, 1, 5, WorkspaceMemberRole.OWNER)


def test_changing_the_owners_role_is_rejected(monkeypatch: pytest.MonkeyPatch, db: Session) -> None:
    stub_repository(monkeypatch, make_member(WorkspaceMemberRole.OWNER))
    with pytest.raises(BadRequestError):
        workspace_service.change_member_role(db, 1, 5, WorkspaceMemberRole.ADMIN)


def test_changing_a_member_to_admin_returns_the_member(monkeypatch: pytest.MonkeyPatch, db: Session) -> None:
    target = make_member(WorkspaceMemberRole.MEMBER)
    stub_repository(monkeypatch, target)
    assert workspace_service.change_member_role(db, 1, 5, WorkspaceMemberRole.ADMIN) is target