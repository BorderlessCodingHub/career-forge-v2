"""Tests for Roadmap Forge learner context builder."""

from __future__ import annotations

from career_forge.services.forge_context import build_forge_context_from_input


DIAGNOSIS = {
    "profile": {
        "label": "Iniciante com foco em IA/ML",
        "track_id": "agent-engineer-beginner",
        "persona_slug": "iniciante_ai_ml",
    },
    "strengths": ["Motivação clara"],
    "gaps": ["Falta de prática hands-on"],
    "starting_priorities": ["Projetos hands-on"],
    "estimated_mastery": {},
}


def test_build_forge_context_from_plain_input() -> None:
    context = build_forge_context_from_input(
        user_id="user-1",
        input_data={
            "diagnosis": DIAGNOSIS,
            "goal_id": "agent-engineer",
            "motivation": "Quero ser AI engineer.",
            "years_xp": "0-1",
            "answers": {"q-r1-1": "Nada."},
        },
    )

    assert context.goal_id == "agent-engineer"
    assert context.interview_answers["q-r1-1"] == "Nada."
    assert "Falta de prática" in context.compact_summary()


def test_build_forge_context_prefers_profile_envelope_intake() -> None:
    context = build_forge_context_from_input(
        user_id="user-1",
        input_data={
            "diagnosis": DIAGNOSIS,
            "profile_diagnosis": {
                "version": 2,
                "diagnosis": DIAGNOSIS,
                "intake": {
                    "goal_id": "agent-engineer",
                    "motivation": "Motivação persistida",
                    "answers": {"prova": "Nada."},
                },
            },
        },
    )

    assert context.motivation == "Motivação persistida"
    assert context.interview_answers == {"prova": "Nada."}
