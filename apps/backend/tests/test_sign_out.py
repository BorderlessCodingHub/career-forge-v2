"""Sign out + JWT jti revocation tests (CAR-69)."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import jwt
from fastapi.testclient import TestClient
from sqlalchemy import select

from career_forge.auth.jwt_tokens import ANON_PROVIDER, EMAIL_PROVIDER
from career_forge.config import settings
from career_forge.db.models.revoked_token_jti import RevokedTokenJti
from career_forge.db.session import SessionLocal


def _mint_legacy_token_without_jti(external_id: str) -> str:
    now = datetime.now(UTC)
    payload = {
        "sub": external_id,
        "provider": ANON_PROVIDER,
        "iat": now,
        "exp": now + timedelta(days=1),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm="HS256")


def test_mint_includes_jti(raw_client: TestClient) -> None:
    res = raw_client.post("/auth/anon/mint", json={"external_id": "user-jti-mint"})
    assert res.status_code == 200
    payload = jwt.decode(
        res.json()["access_token"],
        settings.jwt_secret,
        algorithms=["HS256"],
    )
    assert isinstance(payload.get("jti"), str)
    assert payload["jti"]


def test_token_without_jti_rejected_after_cutover(raw_client: TestClient) -> None:
    token = _mint_legacy_token_without_jti("user-no-jti")
    res = raw_client.get(
        "/roadmap/",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 401


def test_sign_out_revokes_current_token(raw_client: TestClient) -> None:
    from career_forge.auth.providers import get_auth_provider
    from career_forge.db.repositories.user import ensure_user

    external_id = "user-sign-out"
    with SessionLocal() as session:
        ensure_user(session, external_id)
        session.commit()

    token = get_auth_provider().mint_email(external_id)

    ok = raw_client.get("/me/profile", headers={"Authorization": f"Bearer {token}"})
    assert ok.status_code == 200

    sign_out = raw_client.post(
        "/auth/sign-out",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert sign_out.status_code == 204

    reuse = raw_client.get("/me/profile", headers={"Authorization": f"Bearer {token}"})
    assert reuse.status_code == 401

    with SessionLocal() as session:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=["HS256"])
        row = session.scalar(
            select(RevokedTokenJti).where(RevokedTokenJti.jti == payload["jti"]),
        )
        assert row is not None


def test_sign_out_requires_bearer(raw_client: TestClient) -> None:
    res = raw_client.post("/auth/sign-out")
    assert res.status_code == 401


def test_sign_out_twice_returns_401(raw_client: TestClient) -> None:
    from career_forge.auth.providers import get_auth_provider
    from career_forge.db.repositories.user import ensure_user

    external_id = "user-sign-out-twice"
    with SessionLocal() as session:
        ensure_user(session, external_id)
        session.commit()

    token = get_auth_provider().mint_email(external_id)
    headers = {"Authorization": f"Bearer {token}"}

    first = raw_client.post("/auth/sign-out", headers=headers)
    assert first.status_code == 204

    second = raw_client.post("/auth/sign-out", headers=headers)
    assert second.status_code == 401


def test_lazy_cleanup_drops_expired_revocations(raw_client: TestClient) -> None:
    from career_forge.auth.providers import get_auth_provider
    from career_forge.db.repositories.user import ensure_user

    external_id = "user-lazy-cleanup"
    with SessionLocal() as session:
        ensure_user(session, external_id)
        session.commit()

    token = get_auth_provider().mint_email(external_id)
    payload = jwt.decode(token, settings.jwt_secret, algorithms=["HS256"])

    with SessionLocal() as session:
        session.add(
            RevokedTokenJti(
                jti="expired-jti",
                exp=datetime.now(UTC) - timedelta(days=1),
            ),
        )
        session.commit()

    headers = {"Authorization": f"Bearer {token}"}
    assert raw_client.get("/me/profile", headers=headers).status_code == 200

    with SessionLocal() as session:
        assert session.get(RevokedTokenJti, "expired-jti") is None
        assert session.get(RevokedTokenJti, payload["jti"]) is None


def test_email_mint_includes_jti(raw_client: TestClient) -> None:
    from career_forge.auth.providers import get_auth_provider

    token = get_auth_provider().mint_email("user-email-jti")
    payload = jwt.decode(token, settings.jwt_secret, algorithms=["HS256"])
    assert payload["provider"] == EMAIL_PROVIDER
    assert isinstance(payload.get("jti"), str)
