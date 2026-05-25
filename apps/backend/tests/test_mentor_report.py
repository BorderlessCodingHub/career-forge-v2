"""Tests for mentor report API — HAC-15."""

from __future__ import annotations

from datetime import UTC, datetime
from unittest.mock import patch

from career_forge.schemas.common import ValidationStatus
from career_forge.schemas.mentor_report import MentorReportResponse, MentorReportValidationEntry


def _sample_report() -> MentorReportResponse:
    return MentorReportResponse(
        user_id="demo-ana",
        display_name="Ana",
        goal="Backend para APIs em space tech",
        track_title="Backend Developer",
        profile_label="Iniciante com base em JavaScript",
        learner_gaps=["HTTP", "APIs REST"],
        validations=[
            MentorReportValidationEntry(
                node_id="js",
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
                node_id="git",
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
    assert payload["learner_gaps"] == ["HTTP", "APIs REST"]


def test_mentor_report_not_found(client):
    with patch(
        "career_forge.api.mentor_report.get_mentor_report",
        side_effect=ValueError("User not found: unknown"),
    ):
        response = client.get("/mentor-report?user_id=unknown")

    assert response.status_code == 404
