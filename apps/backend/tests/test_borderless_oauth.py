"""LABS01-199 — Borderless OAuth sign-in."""

from __future__ import annotations

import base64
import hashlib

from fastapi.testclient import TestClient
from sqlalchemy import select

from career_forge.auth.providers import get_auth_provider
from career_forge.db.models.user import User
from career_forge.db.session import SessionLocal
from career_forge.services.borderless_oauth import REDIRECT_URI
from career_forge.services.borderless_profile import open_access_token
from tests.borderless_oauth_support import (
    AUTHORIZE,
    CLIENT_ID,
    enable_oauth,
    sign_in_with_borderless,
)


def test_oauth_control_stays_hidden_without_client_credentials(
    raw_client: TestClient,
) -> None:
    mode = raw_client.get("/auth/identity-mode")
    assert mode.status_code == 200
    assert mode.json()["borderless_oauth"] is False
    start = raw_client.get("/auth/borderless/start", follow_redirects=False)
    assert start.status_code == 400
    assert "location" not in {key.lower() for key in start.headers}


def test_code_exchange_stores_sub_and_a_sealed_refresh_token(
    raw_client: TestClient,
) -> None:
    response, fake = sign_in_with_borderless(
        raw_client,
        email="oauth-ada@example.com",
        sub="borderless-ada",
        membership="BASE",
        name="Ada Lovelace",
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["provider"] == "email"
    principal = get_auth_provider().verify(body["access_token"])
    assert principal.external_id == body["external_id"]
    assert principal.external_id.startswith("user-")
    assert principal.external_id != "borderless-ada"
    assert fake.last_form is not None
    assert fake.last_form["redirect_uri"] == REDIRECT_URI
    assert fake.last_form["grant_type"] == "authorization_code"
    assert fake.last_form["code_verifier"]
    with SessionLocal() as session:
        user = session.scalar(select(User).where(User.email == "oauth-ada@example.com"))
        assert user is not None
        assert user.borderless_user_id == "borderless-ada"
        assert user.external_id == body["external_id"]
        assert user.membership_label == "base"
        assert user.membership_entitled is True
        assert user.borderless_access_token is None
        assert open_access_token(user.borderless_refresh_token) == "refresh-1"
        assert user.display_name == "Ada Lovelace"


def test_start_redirect_carries_pkce(raw_client: TestClient) -> None:
    enable_oauth()
    from tests.borderless_oauth_support import FakeBorderlessOAuth
    from career_forge.services.borderless_oauth import set_borderless_oauth_client

    set_borderless_oauth_client(FakeBorderlessOAuth())
    start = raw_client.get("/auth/borderless/start", follow_redirects=False)
    assert start.status_code == 302
    location = start.headers["location"]
    assert location.startswith(AUTHORIZE)
    assert f"client_id={CLIENT_ID}" in location
    assert "code_challenge_method=S256" in location
    assert "code_challenge=" in location
    verifier = raw_client.cookies.get("cf_borderless_oauth_verifier")
    assert verifier
    challenge = base64.urlsafe_b64encode(
        hashlib.sha256(verifier.encode()).digest()
    ).rstrip(b"=").decode()
    assert f"code_challenge={challenge}" in location


def test_free_and_starter_stay_external_and_psp_is_included(
    raw_client: TestClient,
) -> None:
    free, _ = sign_in_with_borderless(
        raw_client, email="oauth-free@example.com", sub="borderless-free", membership="FREE"
    )
    starter, _ = sign_in_with_borderless(
        raw_client,
        email="oauth-starter@example.com",
        sub="borderless-starter",
        membership="STARTER",
    )
    psp, _ = sign_in_with_borderless(
        raw_client, email="oauth-psp@example.com", sub="borderless-psp", membership="PSP"
    )
    assert free.status_code == 200
    assert starter.status_code == 200
    assert psp.status_code == 200
    with SessionLocal() as session:
        free_user = session.scalar(select(User).where(User.email == "oauth-free@example.com"))
        starter_user = session.scalar(
            select(User).where(User.email == "oauth-starter@example.com")
        )
        psp_user = session.scalar(select(User).where(User.email == "oauth-psp@example.com"))
        assert free_user is not None and free_user.membership_label == "external"
        assert free_user.membership_entitled is False
        assert starter_user is not None and starter_user.membership_label == "external"
        assert starter_user.membership_entitled is False
        assert psp_user is not None and psp_user.membership_label == "psp"
        assert psp_user.membership_entitled is True


def test_refresh_rotates_the_token_and_updates_the_label(
    raw_client: TestClient,
) -> None:
    response, fake = sign_in_with_borderless(
        raw_client, email="oauth-refresh@example.com", sub="borderless-refresh", membership="BASE"
    )
    assert response.status_code == 200, response.text
    fake.refresh_membership = "PSP"
    fake.rotated_refresh = "refresh-2"
    started = raw_client.post(
        "/diagnosis/interview/start",
        json={
            "user_id": response.json()["external_id"],
            "goal_id": "rag-engineer",
            "motivation": "I want to build production RAG systems with evals.",
            "years_xp": "0-1",
        },
        headers={"Authorization": f"Bearer {response.json()['access_token']}"},
    )
    assert started.status_code == 200, started.text
    assert fake.refresh_calls == 1
    with SessionLocal() as session:
        user = session.scalar(select(User).where(User.email == "oauth-refresh@example.com"))
        assert user is not None
        assert user.membership_label == "psp"
        assert open_access_token(user.borderless_refresh_token) == "refresh-2"


def test_invalid_grant_keeps_the_label_and_the_session(
    raw_client: TestClient,
) -> None:
    response, fake = sign_in_with_borderless(
        raw_client, email="oauth-grant@example.com", sub="borderless-grant", membership="BASE"
    )
    fake.invalid_grant = True
    token = response.json()["access_token"]
    external_id = response.json()["external_id"]
    started = raw_client.post(
        "/diagnosis/interview/start",
        json={
            "user_id": external_id,
            "goal_id": "rag-engineer",
            "motivation": "I want to build production RAG systems with evals.",
            "years_xp": "0-1",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert started.status_code == 200, started.text
    again = raw_client.post(
        "/diagnosis/interview/start",
        json={
            "user_id": external_id,
            "goal_id": "rag-engineer",
            "motivation": "I want to build production RAG systems with evals.",
            "years_xp": "0-1",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert again.status_code == 200, again.text
    assert fake.refresh_calls == 1
    with SessionLocal() as session:
        user = session.scalar(select(User).where(User.email == "oauth-grant@example.com"))
        assert user is not None
        assert user.membership_label == "base"
        assert user.borderless_access_unrenewable is True


def test_mismatched_sub_is_409_and_unverified_email_is_403(
    raw_client: TestClient,
) -> None:
    first, _ = sign_in_with_borderless(
        raw_client, email="oauth-link@example.com", sub="borderless-link", membership="FREE"
    )
    assert first.status_code == 200, first.text
    clash, _ = sign_in_with_borderless(
        raw_client, email="oauth-link@example.com", sub="borderless-other", membership="BASE"
    )
    assert clash.status_code == 409
    unverified, _ = sign_in_with_borderless(
        raw_client,
        email="oauth-unverified@example.com",
        sub="borderless-unverified",
        email_verified=False,
    )
    assert unverified.status_code == 403
    with SessionLocal() as session:
        assert (
            session.scalar(select(User).where(User.email == "oauth-unverified@example.com"))
            is None
        )


def test_borderless_password_proxy_is_gone(raw_client: TestClient) -> None:
    gone = raw_client.post(
        "/auth/signin",
        json={"email": "oauth-gone@example.com", "password": "secret-pass"},
    )
    assert gone.status_code == 410
