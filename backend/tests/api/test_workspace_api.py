from collections.abc import Callable

from fastapi.testclient import TestClient

from app.models import User


def test_creator_becomes_owner(
    client: TestClient,
    make_user: Callable[[str], User],
    auth: Callable[[User], dict[str, str]],
    create_workspace: Callable[..., int],
) -> None:
    owner = make_user("Owner")
    workspace_id = create_workspace(owner, "Acme")
    response = client.get("/workspaces", headers=auth(owner))
    assert response.status_code == 200
    assert response.json()[0]["id"] == workspace_id
    assert response.json()[0]["role"] == "OWNER"


def test_non_member_gets_404_for_an_existing_workspace(
    client: TestClient,
    make_user: Callable[[str], User],
    auth: Callable[[User], dict[str, str]],
    create_workspace: Callable[..., int],
) -> None:
    owner = make_user("Owner")
    stranger = make_user("Stranger")
    workspace_id = create_workspace(owner)
    response = client.get(f"/workspaces/{workspace_id}", headers=auth(stranger))
    assert response.status_code == 404


def test_missing_workspace_gives_404(
    client: TestClient, make_user: Callable[[str], User], auth: Callable[[User], dict[str, str]]
) -> None:
    user = make_user("Owner")
    response = client.get("/workspaces/9999", headers=auth(user))
    assert response.status_code == 404


def test_workspace_routes_need_a_token(client: TestClient) -> None:
    assert client.get("/workspaces").status_code == 401


def test_member_cannot_rename_but_owner_can(
    client: TestClient,
    make_user: Callable[[str], User],
    auth: Callable[[User], dict[str, str]],
    create_workspace: Callable[..., int],
    join_workspace: Callable[..., None],
) -> None:
    owner = make_user("Owner")
    member = make_user("Member")
    workspace_id = create_workspace(owner)
    join_workspace(owner, workspace_id, member)

    denied = client.patch(f"/workspaces/{workspace_id}", json={"name": "Hacked"}, headers=auth(member))
    allowed = client.patch(f"/workspaces/{workspace_id}", json={"name": "Renamed"}, headers=auth(owner))

    assert denied.status_code == 403
    assert allowed.status_code == 200
    assert allowed.json()["name"] == "Renamed"


def test_only_the_owner_can_delete_a_workspace(
    client: TestClient,
    make_user: Callable[[str], User],
    auth: Callable[[User], dict[str, str]],
    create_workspace: Callable[..., int],
    join_workspace: Callable[..., None],
) -> None:
    owner = make_user("Owner")
    admin = make_user("Admin")
    workspace_id = create_workspace(owner)
    join_workspace(owner, workspace_id, admin, "ADMIN")

    denied = client.delete(f"/workspaces/{workspace_id}", headers=auth(admin))
    deleted = client.delete(f"/workspaces/{workspace_id}", headers=auth(owner))
    after = client.get(f"/workspaces/{workspace_id}", headers=auth(owner))

    assert denied.status_code == 403
    assert deleted.status_code == 204
    assert after.status_code == 404


def test_adding_the_same_member_twice_returns_409(
    client: TestClient,
    make_user: Callable[[str], User],
    auth: Callable[[User], dict[str, str]],
    create_workspace: Callable[..., int],
    join_workspace: Callable[..., None],
) -> None:
    owner = make_user("Owner")
    member = make_user("Member")
    workspace_id = create_workspace(owner)
    join_workspace(owner, workspace_id, member)

    response = client.post(
        f"/workspaces/{workspace_id}/members",
        json={"email": member.email, "role": "MEMBER"},
        headers=auth(owner),
    )
    assert response.status_code == 409


def test_admin_cannot_add_another_admin(
    client: TestClient,
    make_user: Callable[[str], User],
    auth: Callable[[User], dict[str, str]],
    create_workspace: Callable[..., int],
    join_workspace: Callable[..., None],
) -> None:
    owner = make_user("Owner")
    admin = make_user("Admin")
    newcomer = make_user("Newcomer")
    workspace_id = create_workspace(owner)
    join_workspace(owner, workspace_id, admin, "ADMIN")

    response = client.post(
        f"/workspaces/{workspace_id}/members",
        json={"email": newcomer.email, "role": "ADMIN"},
        headers=auth(admin),
    )
    assert response.status_code == 403


def test_owner_cannot_be_removed(
    client: TestClient,
    make_user: Callable[[str], User],
    auth: Callable[[User], dict[str, str]],
    create_workspace: Callable[..., int],
    join_workspace: Callable[..., None],
) -> None:
    owner = make_user("Owner")
    admin = make_user("Admin")
    workspace_id = create_workspace(owner)
    join_workspace(owner, workspace_id, admin, "ADMIN")

    response = client.delete(f"/workspaces/{workspace_id}/members/{owner.id}", headers=auth(admin))
    assert response.status_code == 400
