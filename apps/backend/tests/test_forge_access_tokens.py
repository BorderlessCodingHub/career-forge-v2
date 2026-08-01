"""HTTP tests — share / resume deep-links (CAR-27)."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

from fastapi.testclient import TestClient
from sqlalchemy import select

from career_forge.auth.jwt_tokens import decode_token
from career_forge.db.models.forge_access_token import ROLE_RESUME, ForgeAccessToken
from career_forge.db.session import SessionLocal
from career_forge.schemas.common import Priority, SkillStatus, UserSkillNode
from career_forge.services.forge_persistence import persist_graph_ready


def _auth_headers(raw_client: TestClient, external_id: str) -> dict[str, str]:
    res = raw_client.post("/auth/anon/mint", json={"external_id": external_id})
    assert res.status_code == 200, res.text
    return {"Authorization": f"Bearer {res.json()['access_token']}"}


def _nodes(prefix: str, mastery: int = 20) -> list[dict]:
    return [
        UserSkillNode(
            node_id=f"{prefix}-a",
            title=f"{prefix} A",
            status=SkillStatus.RECOMENDADO,
            mastery_score=mastery,
            priority=Priority.HIGH,
            rationale="r",
            prerequisites=[],
            key_concepts=[],
            tasks=[{"title": "t", "outcome": "o", "evidence_prompt": "e"}],
            references=[],
        ).model_dump(mode="json"),
    ]


def _persist(user: str, run_id: str, goal: str = "rag-engineer"):
    return persist_graph_ready(
        user,
        {"type": "graph_ready", "graph": _nodes(run_id, mastery=30)},
        graph_run_id=run_id,
        goal_id=goal,
    )


def test_mint_share_requires_bearer(raw_client: TestClient) -> None:
    artifact = _persist("share-auth-user", "run-share-auth")
    assert artifact is not None
    res = raw_client.post(f"/me/forges/{artifact.public_id}/share")
    assert res.status_code == 401


def test_share_is_read_only_and_public(raw_client: TestClient) -> None:
    owner = "share-owner-user"
    artifact = _persist(owner, "run-share-ro")
    assert artifact is not None
    headers = _auth_headers(raw_client, owner)

    mint = raw_client.post(f"/me/forges/{artifact.public_id}/share", headers=headers)
    assert mint.status_code == 200, mint.text
    token = mint.json()["token"]
    path = mint.json()["path"]
    assert path == f"/share/{token}"

    # Guest (no Bearer) can read snapshot via API (app deep-link stays /share/…).
    api_path = f"/public/share/{token}"
    shared = raw_client.get(api_path)
    assert shared.status_code == 200, shared.text
    body = shared.json()
    assert body["nodes"]
    assert body["nodes"][0]["node_id"] == "run-share-ro-a"

    # Guest JWT unchanged — share does not mint owner session.
    guest = "share-guest-user"
    guest_headers = _auth_headers(raw_client, guest)
    guest_before = guest_headers["Authorization"]
    shared2 = raw_client.get(api_path, headers=guest_headers)
    assert shared2.status_code == 200
    # Still authenticated as guest afterward.
    me = raw_client.get("/me/forges", headers={"Authorization": guest_before})
    assert me.status_code == 200
    assert me.json()["items"] == []


def test_share_cross_user_mint_forbidden(raw_client: TestClient) -> None:
    artifact = _persist("share-owner-b", "run-share-x")
    assert artifact is not None
    other = _auth_headers(raw_client, "share-other-b")
    res = raw_client.post(f"/me/forges/{artifact.public_id}/share", headers=other)
    assert res.status_code == 404


def test_revoke_share_then_404(raw_client: TestClient) -> None:
    owner = "share-revoke-user"
    artifact = _persist(owner, "run-share-revoke")
    assert artifact is not None
    headers = _auth_headers(raw_client, owner)

    mint = raw_client.post(f"/me/forges/{artifact.public_id}/share", headers=headers)
    assert mint.status_code == 200
    token = mint.json()["token"]

    revoke = raw_client.post(
        f"/me/forges/{artifact.public_id}/share/revoke",
        headers=headers,
    )
    assert revoke.status_code == 200
    assert revoke.json()["revoked"] >= 1

    res = raw_client.get(f"/public/share/{token}")
    assert res.status_code == 404


def test_resume_sets_owner_jwt_single_use(raw_client: TestClient) -> None:
    owner = "resume-owner-user"
    artifact = _persist(owner, "run-resume-once")
    assert artifact is not None
    headers = _auth_headers(raw_client, owner)

    mint = raw_client.post(f"/me/forges/{artifact.public_id}/resume", headers=headers)
    assert mint.status_code == 200, mint.text
    token = mint.json()["token"]
    path = mint.json()["path"]
    assert path == f"/resume/{token}"
    api_path = f"/public/resume/{token}"

    first = raw_client.post(api_path)
    assert first.status_code == 200, first.text
    data = first.json()
    assert data["external_id"] == owner
    assert data["token_type"] == "bearer"
    claims = decode_token(data["access_token"])
    assert claims["sub"] == owner

    # Owner can list forges with adopted token.
    adopted = {"Authorization": f"Bearer {data['access_token']}"}
    listed = raw_client.get("/me/forges", headers=adopted)
    assert listed.status_code == 200
    assert len(listed.json()["items"]) == 1

    second = raw_client.post(api_path)
    assert second.status_code == 410


def test_resume_expired_fails(raw_client: TestClient) -> None:
    owner = "resume-expired-user"
    artifact = _persist(owner, "run-resume-exp")
    assert artifact is not None
    headers = _auth_headers(raw_client, owner)

    mint = raw_client.post(f"/me/forges/{artifact.public_id}/resume", headers=headers)
    assert mint.status_code == 200
    token = mint.json()["token"]

    with SessionLocal() as session:
        rows = list(
            session.scalars(
                select(ForgeAccessToken).where(ForgeAccessToken.role == ROLE_RESUME),
            ),
        )
        assert rows
        # Force-expire all resume rows so the minted token is gone.
        for row in rows:
            row.expires_at = datetime.now(UTC) - timedelta(hours=1)
        session.commit()

    res = raw_client.post(f"/public/resume/{token}")
    assert res.status_code == 410


def test_resume_unknown_token_404(raw_client: TestClient) -> None:
    res = raw_client.post("/public/resume/not-a-real-token-value")
    assert res.status_code == 404
