import logging

import pytest
from fastapi.testclient import TestClient


def test_every_response_has_a_request_id(client: TestClient) -> None:
    response = client.get("/health")
    assert response.headers["x-request-id"]


def test_a_client_sent_request_id_is_reused(client: TestClient) -> None:
    response = client.get("/health", headers={"X-Request-ID": "trace-1"})
    assert response.headers["x-request-id"] == "trace-1"


def test_a_too_long_request_id_is_replaced(client: TestClient) -> None:
    response = client.get("/health", headers={"X-Request-ID": "x" * 200})
    assert response.headers["x-request-id"] != "x" * 200


def test_failed_login_is_logged_without_the_password(client: TestClient, caplog: pytest.LogCaptureFixture) -> None:
    with caplog.at_level(logging.INFO, logger="app.requests"):
        client.post("/auth/login", json={"email": "nobody@teamflow.example", "password": "super-secret-pass"})

    request_records = [record for record in caplog.records if record.name == "app.requests"]
    assert len(request_records) == 1
    record = request_records[0]
    assert record.levelname == "WARNING"
    assert record.method == "POST"
    assert record.path == "/auth/login"
    assert record.status_code == 401
    assert "super-secret-pass" not in caplog.text