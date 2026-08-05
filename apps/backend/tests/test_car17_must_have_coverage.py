"""CAR-17 — must-have coverage helper + inject + forge input wiring."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from career_forge.schemas.common import Priority, SkillStatus, UserSkillNode
from career_forge.schemas.diagnosis import DiagnosisProfile, DiagnosisResponse
from career_forge.services.lean_forge import apply_lean_forge_input, load_must_have_ids
from career_forge.services.must_have_coverage import (
    DEFAULT_COVERAGE_PASS_BAR,
    apply_must_have_inject,
    compute_must_have_coverage,
    coverage_for_goal,
    inject_missing_must_haves,
)

GOALS = ("rag-engineer", "agent-engineer", "llm-evals", "fine-tuning")
FIXTURES = Path(__file__).resolve().parent / "fixtures" / "must_have_coverage"


def _diagnosis(**overrides: object) -> DiagnosisResponse:
    base = {
        "profile": DiagnosisProfile(
            label="Test",
            track_id="rag-engineer-beginner",
            persona_slug="test",
        ),
        "strengths": ["motivation"],
        "gaps": ["retrieval"],
        "starting_priorities": ["rag-retrieval"],
        "estimated_mastery": {"rag-retrieval": 20},
    }
    base.update(overrides)
    return DiagnosisResponse.model_validate(base)


def _node(node_id: str, *, prereqs: list[str] | None = None) -> UserSkillNode:
    return UserSkillNode(
        node_id=node_id,
        title=node_id,
        status=SkillStatus.RECOMENDADO,
        mastery_score=0,
        priority=Priority.HIGH,
        prerequisites=prereqs or [],
    )


class TestMustHaveSidecars:
    def test_each_goal_has_ten_frozen_ids(self) -> None:
        for goal in GOALS:
            ids = load_must_have_ids(goal)
            assert len(ids) == 10, goal
            assert len(set(ids)) == 10, goal

    def test_rag_includes_former_gap_ids(self) -> None:
        ids = load_must_have_ids("rag-engineer")
        assert "rag-hybrid-search" in ids
        assert "rag-orchestration" in ids
        assert "rag-latency-cost" in ids


class TestCoverageHelper:
    def test_coverage_formula(self) -> None:
        result = compute_must_have_coverage(
            ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j"],
            ["a", "b", "c", "d", "e", "f", "g", "x"],
            goal_id="demo",
        )
        assert result.coverage == pytest.approx(0.7)
        assert result.passed is True
        assert result.missing_ids == ["h", "i", "j"]

    def test_below_bar_fails(self) -> None:
        result = compute_must_have_coverage(
            ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j"],
            ["a", "b", "c", "d", "e", "f"],
        )
        assert result.coverage == pytest.approx(0.6)
        assert result.passed is False
        assert result.pass_bar == DEFAULT_COVERAGE_PASS_BAR

    def test_empty_must_haves_full_coverage(self) -> None:
        result = compute_must_have_coverage([], ["a"])
        assert result.coverage == 1.0
        assert result.passed is True


class TestInject:
    def test_inject_appends_missing_with_prereq_edges(self) -> None:
        catalog = {
            "nodes": [
                {"id": "a", "title": "A", "prerequisites": []},
                {"id": "b", "title": "B", "prerequisites": ["a"]},
                {"id": "c", "title": "C", "prerequisites": ["b"]},
            ],
        }
        graph = [_node("a"), _node("b")]
        out = inject_missing_must_haves(
            graph,
            ["a", "b", "c"],
            track_id="rag-engineer-beginner",
            catalog=catalog,
        )
        assert [n.node_id for n in out] == ["a", "b", "c"]
        injected = out[-1]
        assert injected.prerequisites == ["b"]
        assert injected.rationale == "Injected must-have (CAR-17)"

    def test_inject_skips_unknown_catalog_ids(self) -> None:
        catalog = {"nodes": [{"id": "a", "title": "A", "prerequisites": []}]}
        out = inject_missing_must_haves(
            [_node("a")],
            ["a", "missing"],
            track_id="x",
            catalog=catalog,
        )
        assert [n.node_id for n in out] == ["a"]

    def test_apply_returns_pre_inject_coverage(self) -> None:
        must = load_must_have_ids("rag-engineer")
        # 7 of 10 → 0.7
        partial = [_node(node_id) for node_id in must[:7]]
        injected, pre = apply_must_have_inject(
            partial,
            goal_id="rag-engineer",
            track_id="rag-engineer-beginner",
            must_have_ids=must,
        )
        assert pre.coverage == pytest.approx(0.7)
        assert pre.passed is True
        assert {n.node_id for n in injected} >= set(must)
        # Post-inject always covers all catalog-backed must-haves
        post = coverage_for_goal(
            "rag-engineer",
            [n.node_id for n in injected],
            must_have_ids=must,
        )
        assert post.coverage == pytest.approx(1.0)


class TestForgeInputWiring:
    def test_normal_path_attaches_must_have_ids(self) -> None:
        forge_input = {
            "goal_id": "rag-engineer",
            "diagnosis": _diagnosis(profile_score=0.9).model_dump(mode="json"),
        }
        result = apply_lean_forge_input(forge_input)
        assert result["soft_gated"] is False
        assert "lean_allowed_node_ids" not in result
        assert result["must_have_node_ids"] == load_must_have_ids("rag-engineer")

    def test_lean_path_attaches_both(self) -> None:
        forge_input = {
            "goal_id": "rag-engineer",
            "diagnosis": _diagnosis(profile_score=0.2).model_dump(mode="json"),
        }
        result = apply_lean_forge_input(forge_input)
        assert result["soft_gated"] is True
        assert "must_have_node_ids" in result
        assert "lean_allowed_node_ids" in result
        # All must-haves should be in lean allowlist once catalog has gaps
        must = set(result["must_have_node_ids"])
        allow = set(result["lean_allowed_node_ids"])
        assert must <= allow


class TestSmokeFixtures:
    @pytest.mark.parametrize("goal", GOALS)
    def test_smoke_fixture_per_goal(self, goal: str) -> None:
        path = FIXTURES / f"{goal}.json"
        payload = json.loads(path.read_text(encoding="utf-8"))
        assert payload["goal_id"] == goal
        result = coverage_for_goal(goal, payload["forged_node_ids"])
        assert result.coverage == pytest.approx(payload["expected_coverage"])
        assert result.passed is payload["expect_pass"]
