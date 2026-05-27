"""Tests — diagnosis confirm persistence + forge motor input (HAC-52)."""

from __future__ import annotations

from uuid import uuid4

import pytest
from sqlalchemy import select

from career_forge.ai.graphs.diagnosis import build_diagnosis_response
from career_forge.db.models.profile import Profile
from career_forge.db.models.user import User
from career_forge.db.session import SessionLocal
from career_forge.schemas.diagnosis import DiagnosisRequest
from career_forge.schemas.profile_diagnosis import parse_profile_diagnosis
from career_forge.services.profile_diagnosis import confirm_diagnosis, load_forge_motor_input
from career_forge.schemas.profile_diagnosis import DiagnosisConfirmRequest

_SAMPLE = DiagnosisRequest(
    user_id="test-user",
    goal_id="backend",
    motivation="APIs para space tech e produtos digitais",
    years_xp="0-1",
    answers={
        "level": "Já programo em JavaScript há alguns meses.",
        "git": "Subi um projeto no GitHub.",
    },
)


@pytest.fixture
def diagnosis_dict() -> dict:
    return build_diagnosis_response(_SAMPLE).model_dump()


@pytest.fixture
def external_user_id() -> str:
    return f"hac52-test-{uuid4().hex[:12]}"


class TestProfileDiagnosisParsing:
    def test_parse_v2_envelope(self, diagnosis_dict: dict) -> None:
        raw = {
            "version": 2,
            "diagnosis": diagnosis_dict,
            "intake": {
                "goal_id": "backend",
                "motivation": "Motivação de teste",
                "answers": {"level": "resposta"},
            },
        }
        record = parse_profile_diagnosis(raw)
        assert record is not None
        assert record.diagnosis.profile.track_id
        assert record.intake.goal_id == "backend"
        assert record.intake.answers["level"] == "resposta"

    def test_parse_legacy_v1_diagnosis_only(self, diagnosis_dict: dict) -> None:
        record = parse_profile_diagnosis(diagnosis_dict)
        assert record is not None
        assert record.diagnosis.strengths



def test_confirm_and_forge_from_profile(
    client,
    diagnosis_dict: dict,
    external_user_id: str,
) -> None:
    confirm_body = {
        "user_id": external_user_id,
        "diagnosis": diagnosis_dict,
        "goal_id": "backend",
        "motivation": "Quero construir APIs para space tech",
        "years_xp": "0-1",
        "answers": _SAMPLE.answers,
    }
    confirm = client.post("/diagnosis/confirm", json=confirm_body)
    assert confirm.status_code == 200, confirm.text
    payload = confirm.json()
    assert payload["status"] == "confirmed"
    assert payload["profile_id"]

    forge = client.post("/forge", json={"user_id": external_user_id})
    assert forge.status_code == 202, forge.text
    forge_payload = forge.json()
    assert forge_payload["run_id"]
    assert forge_payload["status"] == "pending"

    with SessionLocal() as session:
        user = session.scalar(
            select(User).where(User.external_id == external_user_id),
        )
        assert user is not None
        profile = session.scalar(select(Profile).where(Profile.user_id == user.id))
        assert profile is not None
        assert profile.goal == "backend"
        motor = load_forge_motor_input(session, external_user_id)
        assert motor["goal_id"] == "backend"
        assert motor["answers"]["git"]


def test_forge_without_diagnosis_or_profile_returns_404(client) -> None:
    response = client.post("/forge", json={"user_id": "missing-user-hac52"})
    assert response.status_code == 404


def test_post_forge_api_still_accepts_inline_diagnosis(
    client,
    diagnosis_dict: dict,
) -> None:
    response = client.post(
        "/forge",
        json={"user_id": "demo-ana", "diagnosis": diagnosis_dict},
    )
    assert response.status_code == 202
    payload = response.json()
    assert payload["status"] == "pending"
    assert payload["run_id"]


def test_confirm_diagnosis_service_round_trip(
    diagnosis_dict: dict,
    external_user_id: str,
) -> None:
    from career_forge.schemas.diagnosis import DiagnosisResponse

    body = DiagnosisConfirmRequest(
        user_id=external_user_id,
        diagnosis=DiagnosisResponse.model_validate(diagnosis_dict),
        goal_id="backend",
        motivation="Motivação persistida no Postgres",
        years_xp="1-3",
        answers=_SAMPLE.answers,
    )
    with SessionLocal() as session:
        result = confirm_diagnosis(session, body)
        assert result.user_id == external_user_id
        motor = load_forge_motor_input(session, external_user_id)
        assert motor["motivation"] == body.motivation
        assert motor["years_xp"] == "1-3"
