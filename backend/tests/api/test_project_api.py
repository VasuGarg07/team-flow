from collections.abc import Callable

from fastapi.testclient import TestClient

from app.models import User


def test_member_can_read_projects_but_not_create_one(
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
    create_project(owner, workspace_id, "Website")

    listing = client.get(f"/workspaces/{workspace_id}/projects", headers=auth(member))
    creating = client.post(f"/workspaces/{workspace_id}/projects", json={"name": "Mine"}, headers=auth(member))

    assert listing.status_code == 200
    assert [project["name"] for project in listing.json()] == ["Website"]
    assert creating.status_code == 403


def test_project_from_another_workspace_returns_404(
    client: TestClient,
    make_user: Callable[[str], User],
    auth: Callable[[User], dict[str, str]],
    create_workspace: Callable[..., int],
    create_project: Callable[..., int],
) -> None:
    owner = make_user("Owner")
    workspace_a = create_workspace(owner, "A")
    workspace_b = create_workspace(owner, "B")
    project_in_a = create_project(owner, workspace_a)

    right_path = client.get(f"/workspaces/{workspace_a}/projects/{project_in_a}", headers=auth(owner))
    wrong_path = client.get(f"/workspaces/{workspace_b}/projects/{project_in_a}", headers=auth(owner))

    assert right_path.status_code == 200
    assert wrong_path.status_code == 404


def test_cannot_update_or_delete_a_project_through_another_workspace(
    client: TestClient,
    make_user: Callable[[str], User],
    auth: Callable[[User], dict[str, str]],
    create_workspace: Callable[..., int],
    create_project: Callable[..., int],
) -> None:
    owner = make_user("Owner")
    workspace_a = create_workspace(owner, "A")
    workspace_b = create_workspace(owner, "B")
    project_in_a = create_project(owner, workspace_a)

    update = client.patch(f"/workspaces/{workspace_b}/projects/{project_in_a}", json={"name": "X"}, headers=auth(owner))
    delete = client.delete(f"/workspaces/{workspace_b}/projects/{project_in_a}", headers=auth(owner))
    still_there = client.get(f"/workspaces/{workspace_a}/projects/{project_in_a}", headers=auth(owner))

    assert update.status_code == 404
    assert delete.status_code == 404
    assert still_there.status_code == 200
    assert still_there.json()["name"] == "Website"


def test_stranger_cannot_read_projects(
    client: TestClient,
    make_user: Callable[[str], User],
    auth: Callable[[User], dict[str, str]],
    create_workspace: Callable[..., int],
) -> None:
    owner = make_user("Owner")
    stranger = make_user("Stranger")
    workspace_id = create_workspace(owner)
    response = client.get(f"/workspaces/{workspace_id}/projects", headers=auth(stranger))
    assert response.status_code == 404


def test_new_project_shows_up_even_after_the_list_was_cached(
    client: TestClient,
    make_user: Callable[[str], User],
    auth: Callable[[User], dict[str, str]],
    create_workspace: Callable[..., int],
    create_project: Callable[..., int],
) -> None:
    owner = make_user("Owner")
    workspace_id = create_workspace(owner)
    create_project(owner, workspace_id, "First")

    first_listing = client.get(f"/workspaces/{workspace_id}/projects", headers=auth(owner))
    create_project(owner, workspace_id, "Second")
    second_listing = client.get(f"/workspaces/{workspace_id}/projects", headers=auth(owner))

    assert len(first_listing.json()) == 1
    assert len(second_listing.json()) == 2


def test_deleted_project_disappears_from_a_cached_list(
    client: TestClient,
    make_user: Callable[[str], User],
    auth: Callable[[User], dict[str, str]],
    create_workspace: Callable[..., int],
    create_project: Callable[..., int],
) -> None:
    owner = make_user("Owner")
    workspace_id = create_workspace(owner)
    project_id = create_project(owner, workspace_id)

    client.get(f"/workspaces/{workspace_id}/projects", headers=auth(owner))
    client.delete(f"/workspaces/{workspace_id}/projects/{project_id}", headers=auth(owner))
    listing = client.get(f"/workspaces/{workspace_id}/projects", headers=auth(owner))

    assert listing.json() == []
