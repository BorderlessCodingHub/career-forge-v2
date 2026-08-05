"""Soft gate — profile_score bar → warning + lean forge (CAR-15)."""

from __future__ import annotations

import os
from dataclasses import dataclass

from career_forge.schemas.diagnosis import DiagnosisResponse

# Retuned CAR-18 from golden hand-seeds: midpoint(max weak=0.42, min early=0.58)=0.50
DEFAULT_SOFT_GATE_CUTOFF = 0.50

SOFT_GATE_WARNING = (
    "Your diagnosis confidence is below our bar — we'll build a leaner roadmap "
    "focused on must-have foundations. You can still continue."
)

SOFT_GATE_RESPONSE_FIELDS = frozenset({"soft_gated", "soft_gate_warning"})


@dataclass(frozen=True, slots=True)
class SoftGateDecision:
    soft_gated: bool
    soft_gate_warning: str | None


def soft_gate_cutoff() -> float:
    raw = os.getenv("SOFT_GATE_CUTOFF", str(DEFAULT_SOFT_GATE_CUTOFF)).strip()
    try:
        return float(raw)
    except ValueError:
        return DEFAULT_SOFT_GATE_CUTOFF


def profile_score_present(diagnosis: DiagnosisResponse) -> bool:
    """True when profile_score was explicitly set (not a legacy default)."""
    return "profile_score" in diagnosis.model_fields_set


def evaluate_soft_gate(
    diagnosis: DiagnosisResponse,
    *,
    cutoff: float | None = None,
) -> SoftGateDecision:
    """Derive soft-gate from score vs cutoff.

    Missing/legacy score (not in model_fields_set) → fail-open (no gate).
    Explicit ``0.0`` → gated when below cutoff.
    """
    if not profile_score_present(diagnosis):
        return SoftGateDecision(soft_gated=False, soft_gate_warning=None)

    bar = soft_gate_cutoff() if cutoff is None else cutoff
    if diagnosis.profile_score < bar:
        return SoftGateDecision(soft_gated=True, soft_gate_warning=SOFT_GATE_WARNING)
    return SoftGateDecision(soft_gated=False, soft_gate_warning=None)


def enrich_diagnosis_soft_gate(
    diagnosis: DiagnosisResponse,
    *,
    cutoff: float | None = None,
) -> DiagnosisResponse:
    """Attach runtime soft-gate fields for API responses (not for persistence)."""
    decision = evaluate_soft_gate(diagnosis, cutoff=cutoff)
    return diagnosis.model_copy(
        update={
            "soft_gated": decision.soft_gated,
            "soft_gate_warning": decision.soft_gate_warning,
        },
    )


def diagnosis_dump_for_persist(diagnosis: DiagnosisResponse) -> dict:
    """Serialize diagnosis for profile JSONB without soft-gate fields.

    Omits ``profile_score`` when it was never set so legacy/fail-open survives
    confirm round-trips (default ``0.0`` must not become an explicit score).
    """
    exclude: set[str] = set(SOFT_GATE_RESPONSE_FIELDS)
    if not profile_score_present(diagnosis):
        exclude.add("profile_score")
    return diagnosis.model_dump(mode="json", exclude=exclude)
