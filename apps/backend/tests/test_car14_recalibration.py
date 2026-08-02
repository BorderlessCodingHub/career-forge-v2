"""CAR-14 recalibration fixtures — one synthetic transcript per LLM goal."""

from __future__ import annotations

import pytest

from career_forge.ai.prompts.diagnosis_interview import (
    FINALIZE_SYSTEM,
    GOAL_INTERVIEWER_BRIEFS,
    interviewer_brief_for_goal,
)
from career_forge.schemas.diagnosis_interview import (
    PROFILE_DIMENSION_KEYS,
    BeliefState,
    RubricDimension,
)
from career_forge.services.assessment_rubric import RUBRIC_KEYWORDS, keywords_for
from tests.mocks.diagnosis_interview_llm import (
    GOAL_GAPS,
    MASTERY_NODES_BY_GOAL,
    MockDiagnosisInterviewLlm,
)
from career_forge.schemas.diagnosis_interview import DiagnosisIntake

GOALS = ("rag-engineer", "agent-engineer", "llm-evals", "fine-tuning")

# One seed/must-have node per goal for keyword-hit acceptance
NODE_BY_GOAL = {
    "rag-engineer": "rag-grounding",
    "agent-engineer": "agent-tool-use",
    "llm-evals": "evals-llm-judge",
    "fine-tuning": "ft-lora",
}

LEGACY_SWE_GAP_MARKERS = ("git", "http", "db", "rest", "jwt", "sql schema")


def _belief_mid_confidence() -> BeliefState:
    belief = BeliefState.empty()
    for key in PROFILE_DIMENSION_KEYS:
        belief.dimensions[key] = RubricDimension(
            key=key,
            label=belief.dimensions[key].label,
            confidence=0.7,
            evidence=[f"evidence for {key}"],
            status="mapped",
            note=f"mapped {key}",
        )
    return belief


@pytest.mark.parametrize("goal_id", GOALS)
@pytest.mark.asyncio
async def test_synthetic_finalize_per_goal(goal_id: str) -> None:
    llm = MockDiagnosisInterviewLlm()
    belief = _belief_mid_confidence()
    intake = DiagnosisIntake(
        goal_id=goal_id,
        motivation="I want to ship production LLM systems with measurable quality.",
        years_xp="1-3",
    )

    diagnosis = await llm.finalize_diagnosis(belief, intake)

    assert set(belief.dimensions.keys()) == set(PROFILE_DIMENSION_KEYS)
    assert diagnosis.profile_score == pytest.approx(belief.mean_confidence())
    assert diagnosis.profile_score == pytest.approx(0.7)

    gaps_blob = " ".join(diagnosis.gaps).lower()
    for marker in LEGACY_SWE_GAP_MARKERS:
        assert marker not in gaps_blob, f"legacy SWE gap marker {marker!r} in {diagnosis.gaps}"

    expected_track_gap = GOAL_GAPS[goal_id][0].lower()
    assert any(expected_track_gap in gap.lower() for gap in diagnosis.gaps)

    for node_id in diagnosis.starting_priorities:
        assert node_id in MASTERY_NODES_BY_GOAL[goal_id]


@pytest.mark.parametrize("goal_id", GOALS)
def test_goal_interviewer_brief_exists(goal_id: str) -> None:
    brief = interviewer_brief_for_goal(goal_id)
    assert goal_id in GOAL_INTERVIEWER_BRIEFS
    assert "Early probes" in brief
    assert "Staff probes" in brief


def test_finalize_system_forbids_legacy_swe_checklist() -> None:
    lowered = FINALIZE_SYSTEM.lower()
    assert "not a legacy swe checklist" in lowered
    assert "rag" in lowered
    assert "lora" in lowered


@pytest.mark.parametrize("goal_id", GOALS)
def test_validation_keywords_hit_for_goal_node(goal_id: str) -> None:
    node_id = NODE_BY_GOAL[goal_id]
    assert node_id in RUBRIC_KEYWORDS
    keywords = keywords_for(node_id, 0, ["placeholder criterion text here"])
    assert len(keywords) >= 2
    sample = " ".join(keywords[:3])
    hits = sum(1 for kw in keywords if kw in sample.lower())
    assert hits >= 1
