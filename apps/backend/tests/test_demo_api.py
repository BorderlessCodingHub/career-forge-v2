"""Tests for demo bootstrap API — HAC-12."""

from __future__ import annotations

from unittest.mock import patch

from career_forge.schemas.demo import DemoAnaResponse
from career_forge.schemas.diagnosis import DiagnosisResponse
from career_forge.services.roadmap import build_roadmap_from_catalog


def _sample_diagnosis() -> DiagnosisResponse:
    return DiagnosisResponse.model_validate(
        {
            "profile": {
                "label": "Iniciante com base em JavaScript",
                "track_id": "backend-beginner",
                "persona_slug": "iniciante_js",
            },
            "strengths": ["JavaScript"],
            "gaps": ["HTTP"],
            "starting_priorities": ["http"],
            "estimated_mastery": {"js": 65},
        },
    )


def test_demo_ana_endpoint(client):
    bundle = DemoAnaResponse(
        user_id="demo-ana",
        display_name="Ana",
        diagnosis=_sample_diagnosis(),
        roadmap=build_roadmap_from_catalog(),
        validations=[
            {"node_id": "js", "score": 65, "passed": True, "feedback": "ok"},
            {"node_id": "git", "score": 78, "passed": True, "feedback": "ok"},
        ],
        pitch_node_id="rest",
    )

    with patch("career_forge.api.demo.get_demo_ana", return_value=bundle):
        response = client.get("/demo/ana")

    assert response.status_code == 200
    payload = response.json()
    assert payload["user_id"] == "demo-ana"
    assert payload["display_name"] == "Ana"
    assert len(payload["validations"]) == 2
    assert payload["pitch_node_id"] == "rest"
    assert payload["roadmap"]["nodes"]
