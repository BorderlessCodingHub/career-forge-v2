"""Tests for demo user Ana seed data — HAC-12."""

from __future__ import annotations

from career_forge.demo.ana_state import (
    DEMO_ANA_EXTERNAL_ID,
    DEMO_ANA_SKILL_STATE,
    DEMO_ANA_VALIDATIONS,
    load_demo_diagnosis,
)
from career_forge.schemas.common import SkillStatus
from career_forge.services.roadmap import build_roadmap_from_catalog


def test_demo_ana_constants() -> None:
    assert DEMO_ANA_EXTERNAL_ID == "demo-ana"
    assert len(DEMO_ANA_VALIDATIONS) == 2
    node_ids = {row["skill_node_id"] for row in DEMO_ANA_VALIDATIONS}
    assert node_ids == {"js", "git"}
    assert all(row["passed"] for row in DEMO_ANA_VALIDATIONS)
    assert DEMO_ANA_SKILL_STATE["rest"]["status"] == "validar"


def test_load_demo_diagnosis_fixture() -> None:
    diagnosis = load_demo_diagnosis()
    assert "profile" in diagnosis
    assert "strengths" in diagnosis
    assert "gaps" in diagnosis
    assert diagnosis["profile"]["track_id"] == "backend-beginner"


def test_demo_catalog_state_pitch_ready() -> None:
    roadmap = build_roadmap_from_catalog()
    http = next(node for node in roadmap.nodes if node.node_id == "http")
    rest = next(node for node in roadmap.nodes if node.node_id == "rest")
    assert http.status == SkillStatus.EM_ESTUDO
    assert rest.status == SkillStatus.VALIDAR
