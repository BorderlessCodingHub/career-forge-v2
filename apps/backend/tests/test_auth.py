"""Auth mint + Bearer middleware tests (CAR-23)."""

from __future__ import annotations

import jwt
from fastapi.testclient import TestClient
from sqlalchemy import select

from career_forge.auth.jwt_tokens import ANON_PROVIDER
from career_forge.config import settings
from career_forge.db.models.user import User
from career_forge.db.session import SessionLocal


def test_health_public_without_bearer(raw_client: TestClient) -> None:
    res = raw_client.get("/health")
    assert res.status_code == 200


def test_protected_route_rejects_missing_bearer(raw_client: TestClient) -> None:
    res = raw_client.get("/roadmap/")
    assert res.status_code == 401
    assert "Bearer" in res.json()["detail"]


def test_protected_route_rejects_invalid_bearer(raw_client: TestClient) -> None:
    res = raw_client.get(
        "/roadmap/",
        headers={"Authorization": "Bearer not-a-jwt"},
    )
    assert res.status_code == 401


def test_anon_mint_creates_user_and_token(raw_client: TestClient) -> None:
    res = raw_client.post("/auth/anon/mint", json={"external_id": "user-car23aa"})
    assert res.status_code == 200
    body = res.json()
    assert body["token_type"] == "bearer"
    assert body["provider"] == ANON_PROVIDER
    assert body["external_id"] == "user-car23aa"
    assert body["access_token"]

    payload = jwt.decode(
        body["access_token"],
        settings.jwt_secret,
        algorithms=["HS256"],
    )
    assert payload["sub"] == "user-car23aa"
    assert payload["provider"] == ANON_PROVIDER

    with SessionLocal() as session:
        user = session.scalar(select(User).where(User.external_id == "user-car23aa"))
        assert user is not None


def test_mint_without_external_id_generates_one(raw_client: TestClient) -> None:
    res = raw_client.post("/auth/anon/mint", json={})
    assert res.status_code == 200
    external_id = res.json()["external_id"]
    assert external_id.startswith("user-")


def test_bearer_allows_protected_roadmap(
    client: TestClient,
    auth_external_id: str,
) -> None:
    res = client.get("/roadmap/", params={"user_id": "spoofed-attacker"})
    assert res.status_code == 200
    assert "track" in res.json()
    assert auth_external_id == "test-user-car23"
