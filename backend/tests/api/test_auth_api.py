from collections.abc import Callable

from fastapi.testclient import TestClient

from app.models import User

PASSWORD = "password123"

REGISTER_BODY = {
    "first_name": "Aarav",
    "last_name": "Mehta",
    "email": "aarav@teamflow.example",
    "password": PASSWORD,
}


def test_register_creates_a_user_without_exposing_the_password(client: TestClient) -> None:
    response = client.post("/auth/register", json=REGISTER_BODY)
    assert response.status_code == 201
    body = response.json()
    assert body["email"] == "aarav@teamflow.example"
    assert "password" not in body
    assert "password_hash" not in body


def test_register_lowercases_the_email(client: TestClient) -> None:
    response = client.post("/auth/register", json={**REGISTER_BODY, "email": "Aarav@TeamFlow.example"})
    assert response.json()["email"] == "aarav@teamflow.example"


def test_register_with_an_existing_email_returns_409(client: TestClient) -> None:
    client.post("/auth/register", json=REGISTER_BODY)
    response = client.post("/auth/register", json=REGISTER_BODY)
    assert response.status_code == 409
    assert response.json()["error"]["code"] == "CONFLICT"


def test_register_with_a_short_password_returns_422_with_details(client: TestClient) -> None:
    response = client.post("/auth/register", json={**REGISTER_BODY, "password": "short"})
    assert response.status_code == 422
    error = response.json()["error"]
    assert error["code"] == "VALIDATION_ERROR"
    assert error["details"][0]["field"] == "body.password"


def test_login_returns_an_access_token_and_a_secure_refresh_cookie(
    client: TestClient, make_user: Callable[[str], User]
) -> None:
    user = make_user("Priya")
    response = client.post("/auth/login", json={"email": user.email, "password": PASSWORD})
    assert response.status_code == 200
    assert response.json()["token_type"] == "bearer"
    assert response.json()["access_token"]
    cookie = response.headers["set-cookie"].lower()
    assert "refresh_token=" in cookie
    assert "httponly" in cookie
    assert "samesite=strict" in cookie
    assert "path=/auth" in cookie


def test_login_with_a_wrong_password_returns_401(client: TestClient, make_user: Callable[[str], User]) -> None:
    user = make_user("Priya")
    response = client.post("/auth/login", json={"email": user.email, "password": "wrong-password"})
    assert response.status_code == 401
    assert response.json()["error"]["message"] == "Invalid email or password"


def test_login_with_an_unknown_email_returns_401_not_500(client: TestClient) -> None:
    response = client.post("/auth/login", json={"email": "nobody@teamflow.example", "password": PASSWORD})
    assert response.status_code == 401
    assert response.json()["error"]["message"] == "Invalid email or password"


def test_me_returns_the_signed_in_user(
    client: TestClient, make_user: Callable[[str], User], auth: Callable[[User], dict[str, str]]
) -> None:
    user = make_user("Priya")
    response = client.get("/auth/me", headers=auth(user))
    assert response.status_code == 200
    assert response.json()["email"] == user.email


def test_me_without_a_token_returns_401(client: TestClient) -> None:
    response = client.get("/auth/me")
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "UNAUTHENTICATED"


def test_me_with_a_garbage_token_returns_401(client: TestClient) -> None:
    response = client.get("/auth/me", headers={"Authorization": "Bearer not-a-token"})
    assert response.status_code == 401


def test_refresh_uses_the_cookie_from_login(client: TestClient, make_user: Callable[[str], User]) -> None:
    user = make_user("Priya")
    client.post("/auth/login", json={"email": user.email, "password": PASSWORD})
    response = client.post("/auth/refresh")
    assert response.status_code == 200
    assert response.json()["access_token"]


def test_refresh_without_a_cookie_returns_401(client: TestClient) -> None:
    response = client.post("/auth/refresh")
    assert response.status_code == 401


def test_logout_clears_the_cookie(client: TestClient) -> None:
    response = client.delete("/auth/logout")
    assert response.status_code == 204
    assert "refresh_token=" in response.headers["set-cookie"].lower()


def test_sixth_login_in_a_minute_is_rate_limited(client: TestClient) -> None:
    body = {"email": "nobody@teamflow.example", "password": PASSWORD}
    for _ in range(5):
        assert client.post("/auth/login", json=body).status_code == 401
    response = client.post("/auth/login", json=body)
    assert response.status_code == 429
    assert response.json()["error"]["code"] == "TOO_MANY_REQUESTS"
    assert "retry-after" in response.headers