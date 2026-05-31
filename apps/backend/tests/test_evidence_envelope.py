"""Unit tests for the canonical evidence envelope + legacy adapter (HAC-85)."""

from __future__ import annotations

from career_forge.services.roadmap.evidence import (
    REMEDIATION_PREFIX,
    EvidenceEnvelope,
    read_evidence,
)


class TestReadEvidenceLegacy:
    def test_none_yields_empty_envelope(self) -> None:
        env = read_evidence(None)
        assert env.checklist == []
        assert env.validation is None
        assert env.remediation == []
        assert env.metadata == {}

    def test_legacy_dict_summary_maps_to_validation(self) -> None:
        env = read_evidence({"strengths": ["s1"], "gaps": ["g1"], "next_action": "do x"})
        assert env.validation == {"strengths": ["s1"], "gaps": ["g1"], "next_action": "do x"}
        assert env.checklist == []
        assert env.remediation == []

    def test_legacy_list_splits_into_canonical_buckets(self) -> None:
        env = read_evidence(
            [
                {"type": "metadata", "sort_order": 4},
                {"type": "task", "title": "Build API"},
                {"type": "reference", "title": "Docs"},
                {"type": "task", "id": f"{REMEDIATION_PREFIX}rest", "source": "gap"},
                {"type": "validation", "strengths": ["s"], "gaps": ["g"], "next_action": "n"},
            ],
        )
        assert env.metadata == {"sort_order": 4}
        assert env.sort_order() == 4
        assert [t["title"] for t in env.checklist if t["type"] == "task"] == ["Build API"]
        assert env.reference_items() == [{"type": "reference", "title": "Docs"}]
        assert len(env.remediation) == 1
        assert env.remediation[0]["id"] == f"{REMEDIATION_PREFIX}rest"
        assert env.validation == {"strengths": ["s"], "gaps": ["g"], "next_action": "n"}

    def test_task_items_appends_remediation_after_checklist_tasks(self) -> None:
        env = read_evidence(
            [
                {"type": "task", "title": "Original"},
                {"type": "task", "id": f"{REMEDIATION_PREFIX}x", "source": "gap"},
            ],
        )
        items = env.task_items()
        assert items[0]["title"] == "Original"
        assert items[-1]["source"] == "gap"


class TestCanonicalEnvelope:
    def test_canonical_round_trips_through_read(self) -> None:
        stored = EvidenceEnvelope(
            checklist=[{"type": "task", "title": "T"}],
            validation={"strengths": [], "gaps": ["g"], "next_action": "n"},
            remediation=[{"type": "task", "id": f"{REMEDIATION_PREFIX}c", "source": "gap"}],
            metadata={"sort_order": 2},
        ).to_storage()

        env = read_evidence(stored)
        assert env.sort_order() == 2
        assert env.validation_summary() == {"strengths": [], "gaps": ["g"], "next_action": "n"}
        assert len(env.task_items()) == 2  # checklist task + remediation

    def test_to_storage_has_canonical_keys(self) -> None:
        storage = EvidenceEnvelope().to_storage()
        assert set(storage.keys()) == {"checklist", "validation", "remediation", "metadata"}

    def test_validation_summary_empty_when_none(self) -> None:
        assert read_evidence(None).validation_summary() == {}
