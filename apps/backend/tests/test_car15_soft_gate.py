"""CAR-15 — soft gate bar + lean forge prune."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from career_forge.schemas.diagnosis import DiagnosisProfile, DiagnosisResponse
from career_forge.services.lean_forge import (
    apply_lean_forge_input,
    compute_lean_allowlist,
    load_must_have_ids,
)
from career_forge.services.soft_gate import (
    SOFT_GATE_WARNING,
    diagnosis_dump_for_persist,
    enrich_diagnosis_soft_gate,
    evaluate_soft_gate,
)


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


class TestSoftGateBar:
    def test_missing_score_fail_open(self) -> None:
        diagnosis = _diagnosis()
        assert "profile_score" not in diagnosis.model_fields_set
        decision = evaluate_soft_gate(diagnosis, cutoff=0.55)
        assert decision.soft_gated is False
        assert decision.soft_gate_warning is None

    def test_explicit_zero_gates(self) -> None:
        diagnosis = _diagnosis(profile_score=0.0)
        decision = evaluate_soft_gate(diagnosis, cutoff=0.55)
        assert decision.soft_gated is True
        assert decision.soft_gate_warning == SOFT_GATE_WARNING

    def test_below_cutoff_gates(self) -> None:
        diagnosis = _diagnosis(profile_score=0.4)
        enriched = enrich_diagnosis_soft_gate(diagnosis, cutoff=0.55)
        assert enriched.soft_gated is True
        assert enriched.soft_gate_warning == SOFT_GATE_WARNING

    def test_at_or_above_cutoff_full_forge(self) -> None:
        diagnosis = _diagnosis(profile_score=0.55)
        decision = evaluate_soft_gate(diagnosis, cutoff=0.55)
        assert decision.soft_gated is False
        diagnosis_high = _diagnosis(profile_score=0.9)
        assert evaluate_soft_gate(diagnosis_high, cutoff=0.55).soft_gated is False

    def test_persist_omits_soft_gate_and_unset_score(self) -> None:
        diagnosis = enrich_diagnosis_soft_gate(_diagnosis(profile_score=0.2), cutoff=0.55)
        dumped = diagnosis_dump_for_persist(diagnosis)
        assert "soft_gated" not in dumped
        assert "soft_gate_warning" not in dumped
        assert dumped["profile_score"] == pytest.approx(0.2)

        legacy = _diagnosis()
        legacy_dump = diagnosis_dump_for_persist(legacy)
        assert "profile_score" not in legacy_dump


class TestLeanPrune:
    def test_must_have_ids_loaded(self) -> None:
        ids = load_must_have_ids("rag-engineer")
        assert "rag-embeddings" in ids
        assert "rag-hybrid-search" not in ids  # net-new excluded from sidecar

    def test_allowlist_includes_one_hop_prereqs(self, tmp_path: Path) -> None:
        catalog = {
            "nodes": [
                {"id": "a", "prerequisites": []},
                {"id": "b", "prerequisites": ["a"]},
                {"id": "c", "prerequisites": ["b"]},
                {"id": "d", "prerequisites": []},
            ],
        }
        # must-have c → foundation hop adds b only (not a)
        allow = compute_lean_allowlist(
            "rag-engineer",
            "rag-engineer-beginner",
            must_have_ids=["c"],
            catalog=catalog,
        )
        assert allow == {"c", "b"}

    def test_empty_allowlist_fail_open(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("MUST_HAVES_DIR", str(tmp_path))
        (tmp_path / "rag-engineer.json").write_text(
            json.dumps({"goal_id": "rag-engineer", "ids": []}),
            encoding="utf-8",
        )
        forge_input = {
            "goal_id": "rag-engineer",
            "diagnosis": _diagnosis(profile_score=0.1).model_dump(mode="json"),
        }
        result = apply_lean_forge_input(forge_input)
        assert result["soft_gated"] is True
        assert "lean_allowed_node_ids" not in result

    def test_apply_lean_attaches_allowlist(self) -> None:
        forge_input = {
            "goal_id": "rag-engineer",
            "diagnosis": _diagnosis(profile_score=0.2).model_dump(mode="json"),
        }
        result = apply_lean_forge_input(forge_input)
        assert result["soft_gated"] is True
        assert "lean_allowed_node_ids" in result
        assert "rag-embeddings" in result["lean_allowed_node_ids"]

    def test_legacy_missing_score_apply_lean_fail_open(self) -> None:
        # Dump without profile_score key (legacy confirm)
        raw = _diagnosis().model_dump(mode="json")
        raw.pop("profile_score", None)
        result = apply_lean_forge_input(
            {"goal_id": "rag-engineer", "diagnosis": raw},
        )
        assert result["soft_gated"] is False
        assert "lean_allowed_node_ids" not in result


def test_build_accumulated_graph_respects_allowlist() -> None:
    from career_forge.ai.graphs.roadmap_forge import build_accumulated_graph

    diagnosis = _diagnosis(profile_score=0.2)
    full = build_accumulated_graph(diagnosis)
    lean = build_accumulated_graph(
        diagnosis,
        allowed_node_ids={"rag-embeddings", "rag-chunking"},
    )
    assert len(lean) < len(full)
    assert {n.node_id for n in lean} == {"rag-embeddings", "rag-chunking"}
