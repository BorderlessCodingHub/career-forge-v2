"""CAR-18 — golden cases suite (deterministic)."""

from __future__ import annotations

from career_forge.services.golden_cases import (
    EXPECTED_CASE_COUNT,
    check_suite,
    load_all_golden_cases,
    recommended_cutoff_from_seeds,
)
from career_forge.services.soft_gate import DEFAULT_SOFT_GATE_CUTOFF


def test_sixteen_cases_present() -> None:
    cases = load_all_golden_cases()
    assert len(cases) == EXPECTED_CASE_COUNT


def test_suite_passes_at_default_cutoff() -> None:
    results = check_suite(cutoff=DEFAULT_SOFT_GATE_CUTOFF)
    failures = [r for r in results if not r.ok]
    assert failures == [], [f"{r.case_id}: {r.errors}" for r in failures]


def test_recommended_cutoff_matches_default() -> None:
    recommended = recommended_cutoff_from_seeds()
    assert recommended is not None
    assert abs(recommended - DEFAULT_SOFT_GATE_CUTOFF) < 1e-9
