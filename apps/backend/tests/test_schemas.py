"""Unit tests — AI JSON contract fixtures parse via Pydantic."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from career_forge.ai.graphs.state import SkillGraphState, new_skill_graph_state
from career_forge.schemas import (
    DiagnosisResponse,
    GraphPatch,
    GraphReadyEvent,
    PlanUpdateResponse,
    RoadmapForgeEvent,
    ValidationResponse,
    parse_forge_event,
)
from career_forge.schemas.common import SkillNode, SkillStatus

FIXTURES = (
    Path(__file__).resolve().parents[1]
    / "src"
    / "career_forge"
    / "fixtures"
)
ROADMAP_JSON = Path(__file__).resolve().parents[3] / "data" / "roadmap.json"


def load_fixture(name: str) -> dict | list:
    with (FIXTURES / name).open(encoding="utf-8") as f:
        return json.load(f)


class TestDiagnosisResponse:
    def test_parses_fixture(self) -> None:
        data = load_fixture("diagnosis_response.json")
        model = DiagnosisResponse.model_validate(data)
        assert model.profile.label.startswith("Iniciante")
        assert "http" in model.starting_priorities
        assert model.estimated_mastery["git"] == 78

    def test_rejects_invalid_mastery(self) -> None:
        data = load_fixture("diagnosis_response.json")
        data["estimated_mastery"]["js"] = 150
        with pytest.raises(ValidationError):
            DiagnosisResponse.model_validate(data)


class TestGraphPatch:
    def test_parses_fixture(self) -> None:
        model = GraphPatch.model_validate(load_fixture("graph_patch.json"))
        assert len(model.patches) == 2
        assert model.patches[0].status == SkillStatus.RECOMENDADO
        assert model.continue_research is True


class TestRoadmapForgeEvents:
    def test_each_fixture_event(self) -> None:
        events = load_fixture("roadmap_forge_events.json")
        assert isinstance(events, list)
        parsed: list[RoadmapForgeEvent] = [parse_forge_event(e) for e in events]
        assert parsed[0].type == "reasoning_delta"
        assert parsed[-1].type == "graph_ready"
        assert isinstance(parsed[-1], GraphReadyEvent)
        assert len(parsed[-1].graph) == 7

    def test_discriminator_rejects_unknown_type(self) -> None:
        with pytest.raises(ValidationError):
            parse_forge_event({"type": "unknown", "foo": "bar"})


class TestSkillGraphState:
    def test_factory_serializes_diagnosis(self) -> None:
        diagnosis = DiagnosisResponse.model_validate(
            load_fixture("diagnosis_response.json"),
        )
        catalog = [
            SkillNode.model_validate(n)
            for n in json.loads(ROADMAP_JSON.read_text(encoding="utf-8"))["nodes"]
        ]
        state: SkillGraphState = new_skill_graph_state(
            user_id="demo-ana",
            profile=diagnosis,
            base_catalog=catalog[:3],
            max_iterations=3,
        )
        assert state["user_id"] == "demo-ana"
        assert state["status"] == "running"
        assert state["max_iterations"] == 3
        profile = DiagnosisResponse.model_validate(state["profile"])
        assert profile.profile.track_id == "backend-beginner"


class TestValidationResponse:
    def test_parses_fixture(self) -> None:
        model = ValidationResponse.model_validate(
            load_fixture("validation_response.json"),
        )
        assert model.score == 48
        assert model.status.value == "revisar"
        assert "mentor" in model.mentor_summary.lower()


class TestPlanUpdateResponse:
    def test_parses_fixture(self) -> None:
        model = PlanUpdateResponse.model_validate(
            load_fixture("plan_update_response.json"),
        )
        assert model.today_focus.node_id == "http"
        assert model.today_focus.duration_minutes == 40
        assert "HTTP" in model.next_mission
