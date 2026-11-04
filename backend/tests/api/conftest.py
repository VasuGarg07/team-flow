from collections.abc import Callable, Generator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from app.config import app_settings
from app.database import Base, get_db
from app.main import app as fastapi_app
from app.models import User
from app.security import create_access_token, hash_password
from tests.fakes import InMemoryRedis

PASSWORD = "password123"
PASSWORD_HASH = hash_password(PASSWORD)


@pytest.fixture(scope="session")
def test_engine() -> Generator[Engine, None, None]:
    url = app_settings.TEST_DATABASE_URL
    assert url is not None, "Set TEST_DATABASE_URL in .env"
    assert url != app_settings.DATABASE_URL, "Refusing to use the dev database"
    assert url.rsplit("/", 1)[-1].endswith("_test"), "Refusing to run on a database that is not a test database"
    engine = create_engine(url)
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    yield engine
    engine.dispose()


@pytest.fixture(autouse=True)
def clean_database(test_engine: Engine) -> Generator[None, None, None]:
    yield
    table_names = ", ".join(f'"{table.name}"' for table in Base.metadata.sorted_tables)
    with test_engine.begin() as connection:
        connection.execute(text(f"TRUNCATE {table_names} RESTART IDENTITY CASCADE"))


@pytest.fixture(autouse=True)
def fake_redis(monkeypatch: pytest.MonkeyPatch) -> InMemoryRedis:
    fake = InMemoryRedis()
    monkeypatch.setattr("app.cache.redis_client", fake)
    monkeypatch.setattr("app.realtime.redis_client", fake)
    return fake


@pytest.fixture(autouse=True)
def queued_jobs(monkeypatch: pytest.MonkeyPatch) -> list[int]:
    queued: list[int] = []
    monkeypatch.setattr("app.services.task_service.enqueue_assignment_notification", lambda task_id: queued.append(task_id))
    return queued


@pytest.fixture(autouse=True)
def upload_folder(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> Path:
    monkeypatch.setattr(app_settings, "UPLOAD_DIR", str(tmp_path))
    return tmp_path


@pytest.fixture
def client(test_engine: Engine) -> Generator[TestClient, None, None]:
    test_session_factory = sessionmaker(bind=test_engine)

    def override_get_db() -> Generator[Session, None, None]:
        with test_session_factory() as session:
            yield session

    fastapi_app.dependency_overrides[get_db] = override_get_db
    yield TestClient(fastapi_app)
    fastapi_app.dependency_overrides.clear()


@pytest.fixture
def db_session(test_engine: Engine) -> Generator[Session, None, None]:
    with sessionmaker(bind=test_engine)() as session:
        yield session


@pytest.fixture
def make_user(db_session: Session) -> Callable[[str], User]:
    def create(first_name: str) -> User:
        user = User(
            first_name=first_name,
            last_name="Tester",
            email=f"{first_name.lower()}@teamflow.example",
            password_hash=PASSWORD_HASH,
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        return user

    return create


@pytest.fixture
def auth() -> Callable[[User], dict[str, str]]:
    def headers_for(user: User) -> dict[str, str]:
        return {"Authorization": f"Bearer {create_access_token(user.id)}"}

    return headers_for


@pytest.fixture
def create_workspace(client: TestClient, auth: Callable[[User], dict[str, str]]) -> Callable[..., int]:
    def create(owner: User, name: str = "Acme") -> int:
        response = client.post("/workspaces", json={"name": name}, headers=auth(owner))
        assert response.status_code == 201
        return int(response.json()["id"])

    return create


@pytest.fixture
def join_workspace(client: TestClient, auth: Callable[[User], dict[str, str]]) -> Callable[..., None]:
    def join(owner: User, workspace_id: int, user: User, role: str = "MEMBER") -> None:
        response = client.post(
            f"/workspaces/{workspace_id}/members",
            json={"email": user.email, "role": role},
            headers=auth(owner),
        )
        assert response.status_code == 201

    return join


@pytest.fixture
def create_project(client: TestClient, auth: Callable[[User], dict[str, str]]) -> Callable[..., int]:
    def create(owner: User, workspace_id: int, name: str = "Website") -> int:
        response = client.post(
            f"/workspaces/{workspace_id}/projects",
            json={"name": name},
            headers=auth(owner),
        )
        assert response.status_code == 201
        return int(response.json()["id"])

    return create


@pytest.fixture
def create_task(client: TestClient, auth: Callable[[User], dict[str, str]]) -> Callable[..., int]:
    def create(user: User, workspace_id: int, project_id: int, name: str = "Fix bug", assignee_id: int | None = None) -> int:
        response = client.post(
            f"/workspaces/{workspace_id}/projects/{project_id}/tasks",
            json={"name": name, "assignee_id": assignee_id},
            headers=auth(user),
        )
        assert response.status_code == 201
        return int(response.json()["id"])

    return create
