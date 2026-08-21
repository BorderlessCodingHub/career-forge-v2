"""HTTP tests — /me/profile + /me/email (CAR-29)."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from career_forge.ai.graphs.diagnosis import build_diagnosis_response
from career_forge.db.session import SessionLocal
from career_forge.schemas.diagnosis import DiagnosisRequest, DiagnosisResponse
from career_forge.schemas.profile_diagnosis import DiagnosisConfirmRequest
from career_forge.services.profile_diagnosis import confirm_diagnosis

_SAMPLE = DiagnosisRequest(
    user_id="test-user",
    goal_id="rag-engineer",
    motivation="APIs para space tech e produtos digitais",
    years_xp="0-1",
    answers={
        "level": "Já programo em JavaScript há alguns meses.",
        "rag-chunking": "Subi um projeto no GitHub.",
    },
)


@pytest.fixture
def diagnosis_dict() -> dict:
    return build_diagnosis_response(_SAMPLE).model_dump()


def _auth_headers(raw_client: TestClient, external_id: str) -> dict[str, str]:
    res = raw_client.post("/auth/anon/mint", json={"external_id": external_id})
    assert res.status_code == 200, res.text
    return {"Authorization": f"Bearer {res.json()['access_token']}"}


def test_get_profile_empty(raw_client: TestClient) -> None:
    headers = _auth_headers(raw_client, "me-profile-empty")
    res = raw_client.get("/me/profile", headers=headers)
    assert res.status_code == 200, res.text
    body = res.json()
    assert body["external_id"] == "me-profile-empty"
    assert body["has_diagnosis"] is False
    assert body["email"] is None
    assert body["diagnosis"] is None
    assert body["membership_label"] == "external"
    assert body["membership_entitled"] is False


def test_get_profile_with_diagnosis(
    raw_client: TestClient,
    diagnosis_dict: dict,
) -> None:
    user = "me-profile-diag"
    with SessionLocal() as session:
        confirm_diagnosis(
            session,
            DiagnosisConfirmRequest(
                user_id=user,
                diagnosis=DiagnosisResponse.model_validate(diagnosis_dict),
                goal_id="rag-engineer",
                motivation="build rag systems for production",
                years_xp="1-3",
                answers={"q1": "a1"},
            ),
        )

    headers = _auth_headers(raw_client, user)
    res = raw_client.get("/me/profile", headers=headers)
    assert res.status_code == 200, res.text
    body = res.json()
    assert body["has_diagnosis"] is True
    assert body["diagnosis"] is not None
    assert body["intake"]["goal_id"] == "rag-engineer"
    assert body["intake"]["motivation"] == "build rag systems for production"


def test_patch_email_store_and_conflict(raw_client: TestClient) -> None:
    a = _auth_headers(raw_client, "me-email-a")
    b = _auth_headers(raw_client, "me-email-b")

    ok = raw_client.patch(
        "/me/email",
        headers=a,
        json={"email": "alice@example.com"},
    )
    assert ok.status_code == 200, ok.text
    assert ok.json()["email"] == "alice@example.com"

    profile = raw_client.get("/me/profile", headers=a)
    assert profile.json()["email"] == "alice@example.com"

    conflict = raw_client.patch(
        "/me/email",
        headers=b,
        json={"email": "alice@example.com"},
    )
    assert conflict.status_code == 409

    bad = raw_client.patch(
        "/me/email",
        headers=b,
        json={"email": "not-an-email"},
    )
    assert bad.status_code == 422
