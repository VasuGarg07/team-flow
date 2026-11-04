import pytest
from pydantic import ValidationError

from app.models import TaskPriority
from app.schemas.auth import LoginRequest
from app.schemas.task import TaskCreate, TaskUpdate
from app.schemas.user import UserCreate


def user_data(**changes: object) -> dict[str, object]:
    data: dict[str, object] = {
        "first_name": "Aarav",
        "last_name": "Mehta",
        "email": "aarav@teamflow.example",
        "password": "password123",
    }
    data.update(changes)
    return data


def test_valid_user_is_accepted() -> None:
    user = UserCreate.model_validate(user_data())
    assert user.first_name == "Aarav"


@pytest.mark.parametrize("length", [8, 128])
def test_password_length_at_the_limits_is_accepted(length: int) -> None:
    UserCreate.model_validate(user_data(password="a" * length))


@pytest.mark.parametrize("length", [7, 129])
def test_password_length_outside_the_limits_is_rejected(length: int) -> None:
    with pytest.raises(ValidationError):
        UserCreate.model_validate(user_data(password="a" * length))


@pytest.mark.parametrize(
    "email",
    ["not-an-email", "a@teamflow.test", ""],
    ids=["no_at_sign", "reserved_test_domain", "empty"],
)
def test_bad_email_is_rejected(email: str) -> None:
    with pytest.raises(ValidationError):
        UserCreate.model_validate(user_data(email=email))


def test_login_with_empty_password_is_rejected() -> None:
    with pytest.raises(ValidationError):
        LoginRequest(email="aarav@teamflow.example", password="")


def test_task_create_uses_defaults() -> None:
    task = TaskCreate(name="Fix login")
    assert task.priority == TaskPriority.MEDIUM
    assert task.story_points == 1
    assert task.assignee_id is None


@pytest.mark.parametrize("name", ["", "x" * 101], ids=["empty", "too_long"])
def test_task_create_rejects_bad_names(name: str) -> None:
    with pytest.raises(ValidationError):
        TaskCreate(name=name)


@pytest.mark.parametrize("points", [0, 101])
def test_task_create_rejects_story_points_outside_1_to_100(points: int) -> None:
    with pytest.raises(ValidationError):
        TaskCreate(name="Fix login", story_points=points)


def test_task_create_rejects_unknown_priority() -> None:
    with pytest.raises(ValidationError):
        TaskCreate.model_validate({"name": "Fix login", "priority": "URGENT"})


def test_task_update_remembers_which_fields_were_sent() -> None:
    update = TaskUpdate.model_validate({"assignee_id": None})
    assert update.model_fields_set == {"assignee_id"}


def test_task_update_with_nothing_sent_has_no_fields_set() -> None:
    assert TaskUpdate().model_fields_set == set()