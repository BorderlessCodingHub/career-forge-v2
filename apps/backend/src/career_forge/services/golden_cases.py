"""CAR-18 golden cases — load fixtures + deterministic soft-gate / coverage checks."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

from career_forge.paths import GOAL_TO_CATALOG_TRACK, golden_cases_dir
from career_forge.schemas.diagnosis import DiagnosisResponse
from career_forge.services.lean_forge import compute_lean_allowlist, load_must_have_ids
from career_forge.services.must_have_coverage import (
    DEFAULT_COVERAGE_PASS_BAR,
    coverage_for_goal,
)
from career_forge.services.soft_gate import evaluate_soft_gate, soft_gate_cutoff

GOALS = ("rag-engineer", "agent-engineer", "llm-evals", "fine-tuning")
PERSONAS = ("early", "mid", "staff", "soft-gated-weak")
Persona = Literal["early", "mid", "staff", "soft-gated-weak"]

CASE_ID_RE = re.compile(
    r"^(rag-engineer|agent-engineer|llm-evals|fine-tuning)__"
    r"(early|mid|staff|soft-gated-weak)$",
)

EXPECTED_CASE_COUNT = 16


@dataclass(frozen=True)
class GoldenCase:
    """One golden fixture loaded from ``data/golden_cases/``."""

    path: Path
    payload: dict[str, Any]

    @property
    def case_id(self) -> str:
        return str(self.payload["case_id"])

    @property
    def goal_id(self) -> str:
        return str(self.payload["goal_id"])

    @property
    def persona(self) -> str:
        return str(self.payload["persona"])

    @property
    def is_soft_gated_weak(self) -> bool:
        return self.persona == "soft-gated-weak"

    def diagnosis(self) -> DiagnosisResponse:
        return DiagnosisResponse.model_validate(self.payload["diagnosis"])


@dataclass(frozen=True)
class CaseCheckResult:
    case_id: str
    ok: bool
    errors: tuple[str, ...]


def list_golden_case_paths(directory: Path | None = None) -> list[Path]:
    root = directory if directory is not None else golden_cases_dir()
    return sorted(
        path
        for path in root.glob("*.json")
        if path.name != "_TEMPLATE.json" and not path.name.startswith("_")
    )


def load_golden_case(path: Path) -> GoldenCase:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path}: expected JSON object")
    return GoldenCase(path=path, payload=payload)


def load_all_golden_cases(directory: Path | None = None) -> list[GoldenCase]:
    return [load_golden_case(path) for path in list_golden_case_paths(directory)]


def recommended_cutoff_from_seeds(
    cases: list[GoldenCase] | None = None,
) -> float | None:
    """Midpoint between max(weak) and min(early) profile_score (grill lock)."""
    cases = cases if cases is not None else load_all_golden_cases()
    weak_scores = [
        case.diagnosis().profile_score
        for case in cases
        if case.persona == "soft-gated-weak"
    ]
    early_scores = [
        case.diagnosis().profile_score
        for case in cases
        if case.persona == "early"
    ]
    if not weak_scores or not early_scores:
        return None
    return (max(weak_scores) + min(early_scores)) / 2.0


def validate_case_schema(case: GoldenCase) -> list[str]:
    errors: list[str] = []
    payload = case.payload
    case_id = payload.get("case_id")
    if not isinstance(case_id, str) or not CASE_ID_RE.match(case_id):
        errors.append(f"invalid case_id={case_id!r}")
    elif case.path.stem != case_id:
        errors.append(f"filename stem {case.path.stem!r} != case_id {case_id!r}")

    goal_id = payload.get("goal_id")
    persona = payload.get("persona")
    if goal_id not in GOALS:
        errors.append(f"invalid goal_id={goal_id!r}")
    if persona not in PERSONAS:
        errors.append(f"invalid persona={persona!r}")
    if isinstance(goal_id, str) and isinstance(persona, str):
        expected = f"{goal_id}__{persona}"
        if case_id != expected:
            errors.append(f"case_id {case_id!r} != {expected!r}")

    if not isinstance(payload.get("blurb"), str) or not str(payload.get("blurb")).strip():
        errors.append("blurb required")

    expectations = payload.get("expectations")
    if not isinstance(expectations, dict):
        errors.append("expectations object required")
    else:
        if "soft_gated" not in expectations or not isinstance(
            expectations["soft_gated"],
            bool,
        ):
            errors.append("expectations.soft_gated bool required")
        min_cov = expectations.get("min_pre_inject_coverage")
        if persona == "soft-gated-weak":
            if min_cov is not None:
                errors.append("soft-gated-weak must set min_pre_inject_coverage=null")
        elif min_cov is None or float(min_cov) < DEFAULT_COVERAGE_PASS_BAR:
            errors.append(
                f"non-weak min_pre_inject_coverage must be ≥ {DEFAULT_COVERAGE_PASS_BAR}",
            )

    try:
        diagnosis = case.diagnosis()
    except Exception as exc:  # noqa: BLE001 — surface schema errors
        errors.append(f"diagnosis invalid: {exc}")
        return errors

    if "profile_score" not in diagnosis.model_fields_set:
        errors.append("diagnosis.profile_score must be explicit (hand-seed)")

    track = diagnosis.profile.track_id
    expected_track = GOAL_TO_CATALOG_TRACK.get(str(goal_id))
    if expected_track and track != expected_track:
        errors.append(f"diagnosis.profile.track_id {track!r} != {expected_track!r}")

    snapshot = payload.get("snapshot")
    if not isinstance(snapshot, dict):
        errors.append("snapshot object required")
    else:
        forged = snapshot.get("forged_node_ids")
        if not isinstance(forged, list) or not all(isinstance(x, str) for x in forged):
            errors.append("snapshot.forged_node_ids string list required")
        sample = snapshot.get("validation_sample")
        if not isinstance(sample, dict):
            errors.append("snapshot.validation_sample object required")
        else:
            preview = sample.get("question_preview")
            if not isinstance(preview, str) or not preview.strip():
                errors.append("validation_sample.question_preview required")
            elif _looks_portuguese(preview):
                errors.append("validation_sample.question_preview must be English")

    return errors


def _looks_portuguese(text: str) -> bool:
    lowered = text.lower()
    markers = (" você ", "ção", "ã", "õ", "não ", "para o ", "explique ")
    return any(marker in f" {lowered} " or marker in lowered for marker in markers)


def check_soft_gate(case: GoldenCase, *, cutoff: float | None = None) -> list[str]:
    errors: list[str] = []
    bar = soft_gate_cutoff() if cutoff is None else cutoff
    decision = evaluate_soft_gate(case.diagnosis(), cutoff=bar)
    expected = bool(case.payload["expectations"]["soft_gated"])
    if decision.soft_gated != expected:
        errors.append(
            f"soft_gated got {decision.soft_gated} expected {expected} "
            f"(profile_score={case.diagnosis().profile_score}, cutoff={bar})",
        )
    if expected and case.persona != "soft-gated-weak":
        errors.append("expect soft_gated=true only for soft-gated-weak persona")
    if not expected and case.persona == "soft-gated-weak":
        errors.append("soft-gated-weak must expect soft_gated=true")
    return errors


def check_coverage(case: GoldenCase) -> list[str]:
    errors: list[str] = []
    forged = case.payload["snapshot"]["forged_node_ids"]
    result = coverage_for_goal(case.goal_id, forged)
    expectations = case.payload["expectations"]
    min_cov = expectations.get("min_pre_inject_coverage")

    snap_cov = case.payload["snapshot"].get("pre_inject_coverage")
    if snap_cov is not None and abs(float(snap_cov) - result.coverage) > 1e-6:
        errors.append(
            f"snapshot.pre_inject_coverage={snap_cov} != computed {result.coverage:.4f}",
        )

    if min_cov is not None:
        bar = float(min_cov)
        if result.coverage < bar:
            errors.append(
                f"pre-inject coverage {result.coverage:.0%} < {bar:.0%} "
                f"missing={result.missing_ids}",
            )
    else:
        # Weak: forged nodes must stay inside lean allowlist (must-haves ∪ 1 hop).
        allow = compute_lean_allowlist(case.goal_id, case.diagnosis().profile.track_id)
        must = set(load_must_have_ids(case.goal_id))
        forged_set = {str(node_id) for node_id in forged}
        if not forged_set:
            errors.append("soft-gated-weak snapshot.forged_node_ids must be non-empty")
        elif not forged_set.issubset(allow):
            errors.append(
                f"soft-gated-weak forged ids outside lean allowlist: "
                f"{sorted(forged_set - allow)}",
            )
        elif not forged_set & must:
            errors.append("soft-gated-weak forge should include ≥1 must-have id")
    return errors


def check_case(case: GoldenCase, *, cutoff: float | None = None) -> CaseCheckResult:
    errors = (
        validate_case_schema(case)
        + check_soft_gate(case, cutoff=cutoff)
        + check_coverage(case)
    )
    return CaseCheckResult(case_id=case.case_id, ok=not errors, errors=tuple(errors))


def check_suite(directory: Path | None = None, *, cutoff: float | None = None) -> list[CaseCheckResult]:
    cases = load_all_golden_cases(directory)
    results = [check_case(case, cutoff=cutoff) for case in cases]

    found_ids = {case.case_id for case in cases}
    expected_ids = {f"{goal}__{persona}" for goal in GOALS for persona in PERSONAS}
    missing = sorted(expected_ids - found_ids)
    extras = sorted(found_ids - expected_ids)
    if missing or extras or len(cases) != EXPECTED_CASE_COUNT:
        suite_errors: list[str] = []
        if len(cases) != EXPECTED_CASE_COUNT:
            suite_errors.append(f"expected {EXPECTED_CASE_COUNT} cases, found {len(cases)}")
        if missing:
            suite_errors.append(f"missing cases: {missing}")
        if extras:
            suite_errors.append(f"unexpected cases: {extras}")
        results.append(
            CaseCheckResult(case_id="__suite__", ok=False, errors=tuple(suite_errors)),
        )
    return results
