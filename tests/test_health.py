from __future__ import annotations

from fastapi.testclient import TestClient


def test_health_returns_ok(client: TestClient) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["checks"] == {"api": "ok"}
    assert body["version"]
    assert body["service"]
    assert "X-Request-ID" in response.headers
    assert "X-Response-Time-ms" in response.headers


def test_health_preserves_incoming_request_id(client: TestClient) -> None:
    response = client.get("/health", headers={"X-Request-ID": "req-phase1"})
    assert response.status_code == 200
    assert response.headers["X-Request-ID"] == "req-phase1"


def test_openapi_includes_health(client: TestClient) -> None:
    response = client.get("/openapi.json")
    assert response.status_code == 200
    schema = response.json()
    assert "/health" in schema["paths"]
    assert schema["info"]["x-phase"] == "1"


def test_docs_are_available(client: TestClient) -> None:
    response = client.get("/docs")
    assert response.status_code == 200
