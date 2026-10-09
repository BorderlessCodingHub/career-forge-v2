"""Forge roadmap language is fixed when the run starts (CAR-132)."""

from __future__ import annotations

import inspect

from fastapi.testclient import TestClient

from career_forge.ai.graphs.diagnosis import build_diagnosis_response
from career_forge.ai.prompts.diagnosis_interview import (
    FINALIZE_SYSTEM,
    INTERVIEWER_SYSTEM,
    JUDGE_SYSTEM,
)
from career_forge.ai.run import get_graph_run_store
from career_forge.ai.tools.gap_classifier import OpenAiGapClassifier
from career_forge.ai.tools.mock_interview_mcq import OpenAiMockInterviewMcqGenerator
from career_forge.ai.tools.study_plan_planner import planner_system
from career_forge.ai.tools.tutor_llm import OpenAiTutor
from career_forge.auth.providers import get_auth_provider
from career_forge.db.repositories.user import ensure_user
from career_forge.db.session import SessionLocal
from career_forge.schemas.diagnosis import DiagnosisRequest
from career_forge.services.forge_context import build_forge_context_from_input
from career_forge.services.forge_locale import (
    forge_output_locale,
    roadmap_language_instruction,
    stamp_forge_output_locale,
)

DIAGNOSIS = {
    "profile": {
        "label": "Beginner",
        "track_id": "agent-engineer-beginner",
        "persona_slug": "beginner",
    },
    "strengths": ["Clear goal"],
    "gaps": ["Little practice"],
    "starting_priorities": ["Hands-on projects"],
    "estimated_mastery": {},
}


def test_missing_locale_asks_for_an_english_roadmap() -> None:
    assert forge_output_locale(None) == "en"
    assert forge_output_locale("") == "en"
    assert forge_output_locale("en") == "en"
    assert forge_output_locale("fr") == "en"

    instruction = roadmap_language_instruction(None)
    system = planner_system(None)

    assert system.startswith("You are the Career Forge planner.")
    assert instruction in system
    assert "in English" in instruction
    assert "Brazilian Portuguese" not in system


def test_pt_br_asks_for_brazilian_portuguese_in_an_english_prompt() -> None:
    assert forge_output_locale("pt-BR") == "pt-BR"

    system = planner_system("pt-BR")

    assert system.startswith("You are the Career Forge planner.")
    assert "Brazilian Portuguese" in system
    assert "português do Brasil" in system
    assert "Escreva" not in system


def test_stamp_keeps_this_run_and_a_later_switch_starts_a_new_one() -> None:
    base = {"diagnosis": DIAGNOSIS, "output_locale": "pt-BR"}

    first = stamp_forge_output_locale(base, None)
    second = stamp_forge_output_locale(first, "pt-BR")

    assert first["output_locale"] == "en"
    assert second["output_locale"] == "pt-BR"
    assert base["output_locale"] == "pt-BR"


def test_context_reads_the_locale_stamped_on_the_run() -> None:
    chosen = build_forge_context_from_input(
        user_id="user-1",
        input_data={"diagnosis": DIAGNOSIS, "output_locale": "pt-BR"},
    )
    missing = build_forge_context_from_input(
        user_id="user-1",
        input_data={"diagnosis": DIAGNOSIS},
    )

    assert chosen.output_locale == "pt-BR"
    assert missing.output_locale == "en"


def test_diagnosis_validation_and_mentor_prompts_stay_english() -> None:
    diagnosis = "\n".join([JUDGE_SYSTEM, INTERVIEWER_SYSTEM, FINALIZE_SYSTEM])
    assert "Conversational English" in INTERVIEWER_SYSTEM
    assert "in English" in FINALIZE_SYSTEM
    assert "Brazilian Portuguese" not in diagnosis

    assert "Respond in English." in inspect.getsource(OpenAiGapClassifier._invoke)
    assert "questions in English" in inspect.getsource(
        OpenAiMockInterviewMcqGenerator._invoke
    )
    assert "English." in inspect.getsource(OpenAiTutor._invoke)


def _headers(raw_client: TestClient, external_id: str) -> dict[str, str]:
    minted = raw_client.post("/auth/anon/mint", json={"external_id": external_id})
    assert minted.status_code == 200, minted.text
    token = get_auth_provider().mint_email(external_id)
    return {"Authorization": f"Bearer {token}"}


def _body(user_id: str) -> dict:
    diagnosis = build_diagnosis_response(
        DiagnosisRequest(
            goal_id="rag-engineer",
            motivation="I want to ship grounded RAG systems in production.",
            answers={"level": "beginner"},
        ),
    )
    return {
        "user_id": user_id,
        "diagnosis": diagnosis.model_dump(mode="json"),
        "input": {"output_locale": "pt-BR"},
    }


def test_forge_start_stamps_the_account_locale_and_leaves_the_open_run(
    raw_client: TestClient,
) -> None:
    user = "forge-locale-car-132"
    headers = _headers(raw_client, user)
    with SessionLocal() as session:
        row = ensure_user(session, user)
        row.membership_label = "base"
        row.membership_entitled = True
        row.ui_locale = None
        session.commit()

    first = raw_client.post("/forge/runs", json=_body(user), headers=headers)
    assert first.status_code == 202, first.text
    first_id = first.json()["run_id"]

    store = get_graph_run_store()
    assert store.get(first_id).input["output_locale"] == "en"

    with SessionLocal() as session:
        row = ensure_user(session, user)
        row.ui_locale = "pt-BR"
        session.commit()

    second = raw_client.post("/forge/runs", json=_body(user), headers=headers)
    assert second.status_code == 202, second.text

    assert store.get(first_id).input["output_locale"] == "en"
    assert store.get(second.json()["run_id"]).input["output_locale"] == "pt-BR"
