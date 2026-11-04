from collections.abc import Callable

from fastapi.testclient import TestClient

from app.models import User
from tests.fakes import InMemoryRedis


def tasks_url(workspace_id: int, project_id: int) -> str:
    return f"/workspaces/{workspace_id}/projects/{project_id}/tasks"


def test_reporter_comes_from_the_token_not_the_body(
    client: TestClient,
    make_user: Callable[[str], User],
    auth: Callable[[User], dict[str, str]],
    create_workspace: Callable[..., int],
    join_workspace: Callable[..., None],
    create_project: Callable[..., int],
) -> None:
    owner = make_user("Owner")
    member = make_user("Member")
    workspace_id = create_workspace(owner)
    join_workspace(owner, workspace_id, member)
    project_id = create_project(owner, workspace_id)

    response = client.post(
        tasks_url(workspace_id, project_id),
        json={"name": "Fix bug", "reporter_id": owner.id},
        headers=auth(member),
    )

    assert response.status_code == 201
    assert response.json()["reporter_id"] == member.id
    assert response.json()["status"] == "OPEN"


def test_assignee_must_be_a_workspace_member(
    client: TestClient,
    make_user: Callable[[str], User],
    auth: Callable[[User], dict[str, str]],
    create_workspace: Callable[..., int],
    create_project: Callable[..., int],
) -> None:
    owner = make_user("Owner")
    outsider = make_user("Outsider")
    workspace_id = create_workspace(owner)
    project_id = create_project(owner, workspace_id)

    response = client.post(
        tasks_url(workspace_id, project_id),
        json={"name": "Fix bug", "assignee_id": outsider.id},
        headers=auth(owner),
    )
    assert response.status_code == 400


def test_task_in_another_workspace_returns_404(
    client: TestClient,
    make_user: Callable[[str], User],
    auth: Callable[[User], dict[str, str]],
    create_workspace: Callable[..., int],
    create_project: Callable[..., int],
    create_task: Callable[..., int],
) -> None:
    owner = make_user("Owner")
    workspace_a = create_workspace(owner, "A")
    workspace_b = create_workspace(owner, "B")
    project_a = create_project(owner, workspace_a)
    project_b = create_project(owner, workspace_b)
    task_in_a = create_task(owner, workspace_a, project_a)

    response = client.get(f"{tasks_url(workspace_b, project_b)}/{task_in_a}", headers=auth(owner))
    assert response.status_code == 404


def test_plain_member_cannot_update_someone_elses_task(
    client: TestClient,
    make_user: Callable[[str], User],
    auth: Callable[[User], dict[str, str]],
    create_workspace: Callable[..., int],
    join_workspace: Callable[..., None],
    create_project: Callable[..., int],
    create_task: Callable[..., int],
) -> None:
    owner = make_user("Owner")
    member = make_user("Member")
    workspace_id = create_workspace(owner)
    join_workspace(owner, workspace_id, member)
    project_id = create_project(owner, workspace_id)
    task_id = create_task(owner, workspace_id, project_id)
    url = f"{tasks_url(workspace_id, project_id)}/{task_id}"

    denied = client.patch(url, json={"status": "LIVE"}, headers=auth(member))
    allowed = client.patch(url, json={"status": "LIVE"}, headers=auth(owner))

    assert denied.status_code == 403
    assert allowed.status_code == 200
    assert allowed.json()["status"] == "LIVE"


def test_assignee_can_update_their_task(
    client: TestClient,
    make_user: Callable[[str], User],
    auth: Callable[[User], dict[str, str]],
    create_workspace: Callable[..., int],
    join_workspace: Callable[..., None],
    create_project: Callable[..., int],
    create_task: Callable[..., int],
) -> None:
    owner = make_user("Owner")
    member = make_user("Member")
    workspace_id = create_workspace(owner)
    join_workspace(owner, workspace_id, member)
    project_id = create_project(owner, workspace_id)
    task_id = create_task(owner, workspace_id, project_id, assignee_id=member.id)

    response = client.patch(
        f"{tasks_url(workspace_id, project_id)}/{task_id}",
        json={"status": "IN_PROGRESS"},
        headers=auth(member),
    )
    assert response.status_code == 200


def test_plain_member_cannot_delete_someone_elses_task(
    client: TestClient,
    make_user: Callable[[str], User],
    auth: Callable[[User], dict[str, str]],
    create_workspace: Callable[..., int],
    join_workspace: Callable[..., None],
    create_project: Callable[..., int],
    create_task: Callable[..., int],
) -> None:
    owner = make_user("Owner")
    member = make_user("Member")
    workspace_id = create_workspace(owner)
    join_workspace(owner, workspace_id, member)
    project_id = create_project(owner, workspace_id)
    task_id = create_task(owner, workspace_id, project_id)

    response = client.delete(f"{tasks_url(workspace_id, project_id)}/{task_id}", headers=auth(member))
    assert response.status_code == 403


def test_assigning_to_someone_else_queues_one_job(
    queued_jobs: list[int],
    make_user: Callable[[str], User],
    create_workspace: Callable[..., int],
    join_workspace: Callable[..., None],
    create_project: Callable[..., int],
    create_task: Callable[..., int],
) -> None:
    owner = make_user("Owner")
    member = make_user("Member")
    workspace_id = create_workspace(owner)
    join_workspace(owner, workspace_id, member)
    project_id = create_project(owner, workspace_id)

    task_id = create_task(owner, workspace_id, project_id, assignee_id=member.id)

    assert queued_jobs == [task_id]


def test_assigning_to_yourself_queues_no_job(
    queued_jobs: list[int],
    make_user: Callable[[str], User],
    create_workspace: Callable[..., int],
    create_project: Callable[..., int],
    create_task: Callable[..., int],
) -> None:
    owner = make_user("Owner")
    workspace_id = create_workspace(owner)
    project_id = create_project(owner, workspace_id)

    create_task(owner, workspace_id, project_id, assignee_id=owner.id)

    assert queued_jobs == []


def test_creating_a_task_publishes_a_live_event(
    fake_redis: InMemoryRedis,
    client: TestClient,
    make_user: Callable[[str], User],
    auth: Callable[[User], dict[str, str]],
    create_workspace: Callable[..., int],
    create_project: Callable[..., int],
) -> None:
    owner = make_user("Owner")
    workspace_id = create_workspace(owner)
    project_id = create_project(owner, workspace_id)

    response = client.post(tasks_url(workspace_id, project_id), json={"name": "Fix bug"}, headers=auth(owner))

    events = fake_redis.events_for(f"events:workspace:{workspace_id}")
    assert response.status_code == 201
    assert len(events) == 1
    assert "task.created" in events[0]
    assert str(response.json()["id"]) in events[0]


def test_task_list_has_pagination_and_status_filter(
    client: TestClient,
    make_user: Callable[[str], User],
    auth: Callable[[User], dict[str, str]],
    create_workspace: Callable[..., int],
    create_project: Callable[..., int],
    create_task: Callable[..., int],
) -> None:
    owner = make_user("Owner")
    workspace_id = create_workspace(owner)
    project_id = create_project(owner, workspace_id)
    create_task(owner, workspace_id, project_id, "One")
    create_task(owner, workspace_id, project_id, "Two")
    finished_id = create_task(owner, workspace_id, project_id, "Three")
    base_url = tasks_url(workspace_id, project_id)
    client.patch(f"{base_url}/{finished_id}", json={"status": "LIVE"}, headers=auth(owner))

    first_page = client.get(f"{base_url}?limit=2", headers=auth(owner))
    only_open = client.get(f"{base_url}?status=OPEN", headers=auth(owner))

    assert first_page.status_code == 200
    assert len(first_page.json()["items"]) == 2
    assert first_page.json()["total"] == 3
    assert first_page.json()["page"] == 1
    assert first_page.json()["limit"] == 2
    assert only_open.json()["total"] == 2


def test_task_routes_need_a_token(client: TestClient) -> None:
    assert client.get("/workspaces/1/projects/1/tasks").status_code == 401
