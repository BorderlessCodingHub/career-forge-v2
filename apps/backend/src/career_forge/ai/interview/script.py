"""Deterministic 2-round diagnosis interview script — no LLM planning."""

from __future__ import annotations

from career_forge.ai.payloads.diagnosis_interview import closed_dimensions_from_transcript
from career_forge.schemas.diagnosis_interview import (
    PROFILE_DIMENSION_LABELS,
    BeliefState,
    InterviewQuestion,
    InterviewTurn,
    RubricDimensionKey,
)

COMPOUND_ROUND_ONE = (
    "Tell me the most concrete thing you have built or tried on this path — "
    "what you shipped, with whom, and what you learned.",
    "e.g. group app in school, basic Git, deploy on Vercel, a small RAG notebook.",
)

FOLLOW_UP_BANK: dict[RubricDimensionKey, tuple[str, str]] = {
    "motivation_goal": (
        "What truly motivates you to follow this path right now?",
        "e.g. I want to ship AI product features with real user impact.",
    ),
    "background_transfer": (
        "Where are you coming from, and what from your background helps this transition?",
        "e.g. sales background — I explain complex ideas clearly.",
    ),
    "learning_velocity": (
        "How often do you practice, and how do you stay consistent?",
        "e.g. 1h weekdays, weekend projects.",
    ),
    "hands_on_proof": (
        "What is the most concrete delivery you have attempted?",
        "e.g. simple API on GitHub, dashboard, bot, eval harness.",
    ),
    "constraints": (
        "What real constraints do you have today (time, language, budget)?",
        "e.g. 8h/week, intermediate English, no paid bootcamp.",
    ),
}

INTERVIEW_ROUND_LABELS: tuple[str, ...] = (
    "Practice and routine",
    "Context and constraints",
)

ROUND_TWO_KEYS: tuple[RubricDimensionKey, ...] = (
    "constraints",
    "background_transfer",
)


def round_index_for_count(round_count: int) -> int | None:
    """Map session.round_count to the next script round index, or None when done."""
    if round_count == 0:
        return 0
    if round_count == 1:
        return 1
    return None


def pending_round_two_keys(
    belief: BeliefState,
    transcript: list[InterviewTurn],
) -> list[RubricDimensionKey]:
    """Round-2 keys still open — skip dimensions already mapped or answered."""
    closed = closed_dimensions_from_transcript(transcript)
    pending: list[RubricDimensionKey] = []
    for key in ROUND_TWO_KEYS:
        if belief.dimensions[key].status == "mapped":
            continue
        if key in closed:
            continue
        pending.append(key)
    return pending


def build_round_questions(
    round_index: int,
    *,
    belief: BeliefState | None = None,
    transcript: list[InterviewTurn] | None = None,
) -> list[InterviewQuestion]:
    """Return fixed questions for round_index (0 = practical proof, 1 = context)."""
    if round_index == 0:
        prompt, example = COMPOUND_ROUND_ONE
        return [
            InterviewQuestion(
                id="q-r1-1",
                topic=PROFILE_DIMENSION_LABELS["hands_on_proof"],
                rubric_key="hands_on_proof",
                question=prompt,
                example_of_answer=example,
            ),
        ]

    if round_index == 1:
        keys = (
            pending_round_two_keys(belief, transcript or [])
            if belief is not None
            else list(ROUND_TWO_KEYS)
        )
        questions: list[InterviewQuestion] = []
        for index, key in enumerate(keys):
            prompt, example = FOLLOW_UP_BANK[key]
            questions.append(
                InterviewQuestion(
                    id=f"q-r2-{index + 1}",
                    topic=PROFILE_DIMENSION_LABELS[key],
                    rubric_key=key,
                    question=prompt,
                    example_of_answer=example,
                ),
            )
        return questions

    msg = f"invalid round_index {round_index}; expected 0 or 1"
    raise ValueError(msg)
