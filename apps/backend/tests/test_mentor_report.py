"""Tests for mentor report API — HAC-15."""

from __future__ import annotations

from datetime import UTC, datetime
from unittest.mock import patch
from uuid import uuid4

import pytest
from sqlalchemy import select

from career_forge.ai.graphs.diagnosis import build_diagnosis_response
from career_forge.db.models.user import User
from career_forge.db.models.user_skill_node import UserSkillNode as UserSkillNodeRow
from career_forge.db.models.validation import Validation
from career_forge.db.session import SessionLocal
from career_forge.schemas.common import Priority, SkillStatus, UserSkillNode, ValidationStatus
from career_forge.schemas.diagnosis import DiagnosisRequest
from career_forge.schemas.mentor_report import MentorReportResponse, MentorReportValidationEntry
from career_forge.services.mentor_report import (
    _evidence_from_skill_row,
    _humanize_node_id,
    _resolve_goal_display,
    get_mentor_report,
)

_SAMPLE = DiagnosisRequest(
    user_id="test-user",
    goal_id="backend",
    motivation="APIs para space tech e produtos digitais",
    years_xp="0-1",
    answers={"level": "Já programo em JavaScript há alguns meses."},
)

GENERATED_NODE_ID = "node-1-python-data-foundations"
GENERATED_NODE_TITLE = "Fundamentos de Python para IA/ML e ambiente de trabalho"


@pytest.fixture
def diagnosis_dict() -> dict:
    return build_diagnosis_response(_SAMPLE).model_dump()


@pytest.fixture
def external_user_id() -> str:
    return f"mentor-report-{uuid4().hex[:12]}"


def _generated_node() -> UserSkillNode:
    return UserSkillNode(
        node_id=GENERATED_NODE_ID,
        title=GENERATED_NODE_TITLE,
        status=SkillStatus.EM_ESTUDO,
        mastery_score=0,
        priority=Priority.HIGH,
        tasks=[
            {
                "title": "Ambiente virtual",
                "outcome": "venv ativo",
                "evidence_prompt": "ambiente virtual isolado",
            },
        ],
        references=[{"title": "Python docs", "url": "https://docs.python.org"}],
    )


def _sync_node(client, user_id: str) -> None:
    response = client.post(
        "/roadmap/sync",
        json={"user_id": user_id, "nodes": [_generated_node().model_dump()]},
    )
    assert response.status_code == 200


def _internal_user_id(external_id: str):
    with SessionLocal() as session:
        user = session.scalar(select(User).where(User.external_id == external_id))
        assert user is not None
        return user.id


def test_humanize_node_id_strips_prefix_and_hyphens() -> None:
    assert _humanize_node_id(GENERATED_NODE_ID) == "Python Data Foundations"


def test_resolve_goal_display_maps_known_slug() -> None:
    assert _resolve_goal_display("rag-engineer") == "Production RAG & Advanced Retrieval"


def test_resolve_goal_display_passes_through_human_text() -> None:
    human = "Backend para APIs em space tech"
    assert _resolve_goal_display(human) == human


def test_get_mentor_report_resolves_goal_slug_from_profile(client, diagnosis_dict) -> None:
    external_id = f"mentor-report-goal-{uuid4().hex[:8]}"
    confirm = client.post(
        "/diagnosis/confirm",
        json={
            "user_id": external_id,
            "diagnosis": diagnosis_dict,
            "goal_id": "agent-engineer",
            "motivation": "APIs para space tech",
            "years_xp": "0-1",
            "answers": {"level": "Já programo em JavaScript."},
        },
    )
    assert confirm.status_code == 200

    response = client.get(f"/mentor-report?user_id={external_id}")
    assert response.status_code == 200
    assert response.json()["goal"] == "Agent Engineering"


def test_evidence_from_skill_row_reads_validation_from_list() -> None:
    row = UserSkillNodeRow(
        user_id=uuid4(),
        skill_node_id=GENERATED_NODE_ID,
        status=SkillStatus.REVISAR.value,
        mastery_score=0,
        evidence=[
            {"type": "task", "title": "Ambiente virtual"},
            {
                "type": "validation",
                "strengths": ["Completou o mock interview"],
                "gaps": ["Errou (ambiente virtual isolado): marcou D, gabarito B"],
                "next_action": "Revise as lacunas e refaça o mock interview.",
                "mock_interview": True,
            },
        ],
    )
    evidence = _evidence_from_skill_row(row)
    assert evidence["strengths"] == ["Completou o mock interview"]
    assert evidence["gaps"][0].startswith("Errou")
    assert evidence["next_action"].startswith("Revise")


def test_get_mentor_report_resolves_generated_title_and_list_evidence(client) -> None:
    external_id = f"mentor-report-gen-{uuid4().hex[:8]}"
    _sync_node(client, external_id)
    user_uuid = _internal_user_id(external_id)

    with SessionLocal() as session:
        user_skill = session.scalar(
            select(UserSkillNodeRow).where(
                UserSkillNodeRow.user_id == user_uuid,
                UserSkillNodeRow.skill_node_id == GENERATED_NODE_ID,
            ),
        )
        assert user_skill is not None
        user_skill.evidence = [
            {"type": "task", "title": "Ambiente virtual"},
            {
                "type": "validation",
                "strengths": ["Completou o mock interview MCQ"],
                "gaps": ["Errou (list comprehension): marcou D, gabarito C"],
                "next_action": "Revise as lacunas de Python e refaça o mock interview.",
                "mock_interview": True,
            },
        ]
        session.add(
            Validation(
                user_id=user_uuid,
                skill_node_id=GENERATED_NODE_ID,
                user_skill_node_id=user_skill.id,
                score=0,
                passed=False,
                feedback="Mock interview MCQ de Fundamentos de Python — 0/7 acertos.",
            ),
        )
        session.commit()

    with SessionLocal() as session:
        report = get_mentor_report(session, external_id)

    assert len(report.validations) == 1
    entry = report.validations[0]
    assert entry.node_title == GENERATED_NODE_TITLE
    assert entry.strengths == ["Completou o mock interview MCQ"]
    assert entry.gaps[0].startswith("Errou")
    assert entry.recommended_intervention.startswith("Revise as lacunas")


def _sample_report() -> MentorReportResponse:
    return MentorReportResponse(
        user_id="demo-ana",
        display_name="Ana",
        goal="Backend para APIs em space tech",
        track_title="Backend Developer",
        profile_label="Iniciante com base em JavaScript",
        learner_gaps=["HTTP", "Grounded generation"],
        validations=[
            MentorReportValidationEntry(
                node_id="rag-embeddings",
                node_title="JavaScript",
                score=65,
                status=ValidationStatus.APROVADO,
                strengths=["Sintaxe e lógica JavaScript sólidas"],
                gaps=[],
                mentor_summary="Domínio sólido de JavaScript básico — pronto para APIs.",
                recommended_intervention="Avançar para HTTP e APIs.",
                validated_at=datetime(2026, 5, 25, 12, 0, tzinfo=UTC),
            ),
            MentorReportValidationEntry(
                node_id="rag-chunking",
                node_title="Git & GitHub",
                score=78,
                status=ValidationStatus.APROVADO,
                strengths=["Versionamento com commits e branches"],
                gaps=[],
                mentor_summary="Bom domínio de Git — pronto para fluxo colaborativo.",
                recommended_intervention="Aplicar Git em fluxo de API.",
                validated_at=datetime(2026, 5, 25, 13, 0, tzinfo=UTC),
            ),
        ],
    )


def test_mentor_report_endpoint(client):
    report = _sample_report()
    with patch("career_forge.api.mentor_report.get_mentor_report", return_value=report):
        response = client.get("/mentor-report?user_id=demo-ana")

    assert response.status_code == 200
    payload = response.json()
    assert payload["user_id"] == "demo-ana"
    assert payload["display_name"] == "Ana"
    assert payload["goal"] == "Backend para APIs em space tech"
    assert len(payload["validations"]) == 2
    assert payload["validations"][0]["node_title"] == "JavaScript"
    assert payload["validations"][0]["recommended_intervention"]
    assert payload["learner_gaps"] == ["HTTP", "Grounded generation"]


def test_mentor_report_not_found(client):
    with patch(
        "career_forge.api.mentor_report.get_mentor_report",
        side_effect=ValueError("User not found: unknown"),
    ):
        response = client.get("/mentor-report?user_id=unknown")

    assert response.status_code == 404


def test_mentor_report_reads_v2_profile_envelope(
    client,
    diagnosis_dict: dict,
    external_user_id: str,
) -> None:
    """HAC-52 v2 profile envelope must not break mentor report."""
    confirm = client.post(
        "/diagnosis/confirm",
        json={
            "user_id": external_user_id,
            "diagnosis": diagnosis_dict,
            "goal_id": "backend",
            "motivation": "APIs para space tech",
            "years_xp": "0-1",
            "answers": {"level": "Já programo em JavaScript."},
        },
    )
    assert confirm.status_code == 200

    response = client.get(f"/mentor-report?user_id={external_user_id}")
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["user_id"] == external_user_id
    assert payload["profile_label"]
    assert isinstance(payload["validations"], list)
