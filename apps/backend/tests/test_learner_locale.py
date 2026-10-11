"""Learner-facing model text follows the stored account locale (CAR-133).

Seams: the language instruction, the diagnosis prompt composers, the
interview script, the rubric map, forge research, mentor templates, and
validation shells. The cookie and the client do not choose the language.
"""

from __future__ import annotations

import pytest

from career_forge.ai.graphs.diagnosis_interview import run_interview_phase
from career_forge.ai.graphs.roadmap_forge import _research_artifact, build_research_prompt
from career_forge.ai.tools.openai_web_search import WebSearchResult
from career_forge.ai.llm.diagnosis_interview import (
    reset_diagnosis_interview_llm,
    set_diagnosis_interview_llm,
)
from career_forge.ai.prompts.diagnosis_interview import (
    FINALIZE_SYSTEM,
    INTERVIEWER_SYSTEM,
    JUDGE_SYSTEM,
    finalize_system,
    interviewer_brief_for_goal,
    interviewer_system,
    judge_system,
)
from career_forge.ai.payloads.diagnosis_interview import apply_transcript_overrides
from career_forge.ai.tools.gap_classifier import gap_classifier_system, pin_gap_concepts
from career_forge.ai.tools.mock_interview_mcq import mock_interview_system
from career_forge.ai.tools.tutor_llm import tutor_system
from career_forge.schemas.diagnosis_interview import (
    BeliefState,
    DiagnosisIntake,
    DiagnosisSession,
    InterviewAnswer,
    InterviewQuestion,
    InterviewTurn,
    RubricDimension,
)
from career_forge.schemas.knowledge_gap import (
    KnowledgeGapClassification,
    KnowledgeGapDraft,
    WrongAnswerItem,
)
from career_forge.schemas.mentor import MentorContextSnapshot, MentorRequest
from career_forge.services.forge_context import LearnerForgeContext
from career_forge.learner_text import learner_text_instruction
from career_forge.services.mentor import build_mentor_response
from career_forge.services.validation import build_validation_questions
from career_forge.schemas.diagnosis import DiagnosisProfile, DiagnosisResponse
from tests.mocks.diagnosis_interview_llm import MockDiagnosisInterviewLlm

CRITERION = "cosine similarity over chunk vectors"
NODE_TITLE = "Grounded generation"
GAP = "chunk overlap"


def _context(locale: str) -> LearnerForgeContext:
    return LearnerForgeContext(
        user_id="user-1",
        goal_id="rag-engineer",
        motivation="Ship grounded answers.",
        diagnosis=DiagnosisResponse(
            profile=DiagnosisProfile(
                label="Beginner",
                track_id="rag-engineer-beginner",
                persona_slug="beginner",
            ),
            strengths=["Clear goal"],
            gaps=["Little practice"],
            starting_priorities=["rag-embeddings"],
            estimated_mastery={"rag-embeddings": 10},
        ),
        output_locale=locale,
    )


def test_empty_and_unknown_locales_ask_for_english() -> None:
    for stored in (None, "", "en", "fr"):
        instruction = learner_text_instruction(stored, "label and note")
        assert "in English" in instruction
        assert "Brazilian Portuguese" not in instruction
        assert "label and note" in instruction
        assert "rubric keys" in instruction
        assert "node ids" in instruction


def test_pt_br_names_brazilian_portuguese_in_an_english_instruction() -> None:
    instruction = learner_text_instruction("pt-BR", "topic, question, and example_of_answer")

    assert instruction.startswith("Write these learner-facing strings")
    assert "Brazilian Portuguese (português do Brasil)" in instruction
    assert "topic, question, and example_of_answer" in instruction
    assert "Do not translate the learner's own words." in instruction
    assert "Escreva" not in instruction


def test_prompt_bodies_stay_english_and_the_instruction_names_the_fields() -> None:
    bodies = "\n".join([JUDGE_SYSTEM, INTERVIEWER_SYSTEM, FINALIZE_SYSTEM])
    assert "Brazilian Portuguese" not in bodies
    assert "You are the Judge" in JUDGE_SYSTEM
    assert "You are the Interviewer" in INTERVIEWER_SYSTEM
    assert "Finalize the diagnosis" in FINALIZE_SYSTEM

    brief = interviewer_brief_for_goal("rag-engineer")
    assert brief.startswith("Goal: RAG Engineer.")
    assert "Brazilian Portuguese" not in brief

    judge = judge_system("pt-BR")
    interviewer = interviewer_system("pt-BR")
    finalize = finalize_system("pt-BR")

    assert judge.startswith("You are the Judge")
    assert "label, description, and note" in judge
    assert interviewer.startswith("You are the Interviewer")
    assert "topic, question, and example_of_answer" in interviewer
    assert finalize.startswith("Finalize the diagnosis")
    assert "profile label" in finalize
    assert "starting-priority prose" in finalize
    for prompt in (judge, interviewer, finalize):
        assert "Brazilian Portuguese" in prompt

    english = judge_system(None)
    assert "in English" in english
    assert "Brazilian Portuguese" not in english

    mock = mock_interview_system("pt-BR")
    gap = gap_classifier_system("pt-BR")
    tutor = tutor_system("pt-BR")
    assert mock.startswith("You create multiple-choice")
    assert "question, options, hint, and concept" in mock
    assert gap.startswith("You classify")
    assert "suggested_remediation" in gap
    assert "missed question's concept" in gap
    assert tutor.startswith("You are a Career Forge technical tutor")
    assert "the reply" in tutor
    for prompt in (mock, gap, tutor):
        assert "Brazilian Portuguese" in prompt
        assert "Escreva" not in prompt


def test_english_prompt_composers_do_not_ask_for_portuguese() -> None:
    for prompt in (
        mock_interview_system(""),
        gap_classifier_system("fr"),
        tutor_system(None),
    ):
        assert "in English" in prompt
        assert "Brazilian Portuguese" not in prompt


def test_interview_script_uses_the_locale_and_leaves_the_previous_question() -> None:
    from career_forge.ai.interview.script import build_round_questions

    first = build_round_questions(0)
    assert first[0].rubric_key == "hands_on_proof"
    assert first[0].topic == "Hands-on proof"
    assert "built or tried" in first[0].question

    transcript_question = first[0].question
    nxt = build_round_questions(1, locale="pt-BR")

    assert transcript_question == first[0].question
    assert nxt
    assert {question.rubric_key for question in nxt} == {
        "constraints",
        "background_transfer",
    }
    assert all(question.topic != question.rubric_key for question in nxt)
    assert any(question.topic == "Contexto real" for question in nxt)
    assert all("How " not in question.question for question in nxt)
    assert any("limites reais" in question.question for question in nxt)


@pytest.fixture
def mock_llm() -> None:
    set_diagnosis_interview_llm(MockDiagnosisInterviewLlm())
    yield
    reset_diagnosis_interview_llm()


@pytest.mark.asyncio
async def test_mid_interview_switch_changes_the_next_question_and_sidebar(
    mock_llm: None,
) -> None:
    del mock_llm
    intake = DiagnosisIntake(
        user_id="locale-switch",
        goal_id="rag-engineer",
        motivation="I want to ship RAG.",
        years_xp="0-1",
    )
    started = await run_interview_phase(
        phase="start",
        session=DiagnosisSession(session_id="sess-locale", intake=intake),
        locale="en",
    )
    first_question = started["questions"][0]["question"]
    assert "built or tried" in first_question
    assert started["mapping_progress"][0]["rubric_key"] == "motivation_goal"
    assert started["mapping_progress"][0]["label"] == "Goal"

    session = DiagnosisSession.model_validate(started["session"])
    turned = await run_interview_phase(
        phase="turn",
        session=session,
        answers=[
            InterviewAnswer(
                question_id=started["questions"][0]["id"],
                text="I built a small notebook and studied eight hours a week.",
            ),
        ],
        locale="pt-BR",
    )

    stored = turned["session"]["transcript"][0]["questions"][0]
    assert stored["question"] == first_question
    assert stored["rubric_key"] == "hands_on_proof"
    assert turned["questions"]
    assert all(question["rubric_key"].isascii() for question in turned["questions"])
    assert any("sua trajetória" in question["question"] for question in turned["questions"])
    labels = {item["rubric_key"]: item["label"] for item in turned["mapping_progress"]}
    assert labels["motivation_goal"] == "Objetivo"
    assert labels["hands_on_proof"] == "Prova prática"
    assert all(item["rubric_key"].isascii() for item in turned["mapping_progress"])
    note = next(
        item["note"]
        for item in turned["mapping_progress"]
        if item["rubric_key"] == "hands_on_proof"
    )
    assert "notebook" in note


def test_rubric_map_keeps_a_stored_note_and_translates_the_chrome_fields() -> None:
    from career_forge.schemas.diagnosis_interview import build_rubric_map

    belief = BeliefState.empty()
    belief.dimensions["hands_on_proof"].note = "I built a small notebook"
    mapped = build_rubric_map(belief, locale="pt-BR")
    proof = next(item for item in mapped if item.rubric_key == "hands_on_proof")

    assert proof.label == "Prova prática"
    assert proof.description == "A maior coisa que você construiu, tentou ou publicou"
    assert proof.note == "I built a small notebook"
    assert proof.rubric_key == "hands_on_proof"


def test_forge_research_follows_the_locale_stamped_on_the_run() -> None:
    portuguese = build_research_prompt(
        _context("pt-BR"),
        focus="official roadmap and prerequisites",
        instruction="Find official sources to structure the learner's goal journey.",
        summary="goal_id: rag-engineer",
    )
    english = build_research_prompt(
        _context("en"),
        focus="official roadmap and prerequisites",
        instruction="Find official sources to structure the learner's goal journey.",
        summary="goal_id: rag-engineer",
    )

    assert portuguese.startswith("You must use web_search.")
    assert "the two UI sentences" in portuguese
    assert "Brazilian Portuguese" in portuguese
    assert "Find official sources" in portuguese
    assert "in English" in english
    assert "Brazilian Portuguese" not in english

    empty = WebSearchResult(query="q", summary="", sources=[])
    assert _research_artifact(empty, locale="pt-BR")["label"] == "Pesquisando fontes oficiais..."
    assert _research_artifact(empty, locale="pt-BR")["detail"] == "0 fontes encontradas"
    assert _research_artifact(empty, locale="en")["label"] == "Searching official sources..."
    assert _research_artifact(empty, locale=None)["detail"] == "0 sources found"


def test_mentor_template_keeps_the_forged_title_and_the_stored_gap() -> None:
    context = MentorContextSnapshot(recent_gaps=[GAP])
    payload = MentorRequest(
        user_id="ana",
        node_id="rag-grounding",
        node_title=NODE_TITLE,
        message="what gap should I review?",
    )

    portuguese = build_mentor_response(payload, context, locale="pt-BR")
    english = build_mentor_response(payload, context, locale=None)

    assert NODE_TITLE in portuguese.reply
    assert GAP in portuguese.reply
    assert "I see you still have gaps" not in portuguese.reply
    assert "I see you still have gaps" in english.reply
    assert NODE_TITLE in english.reply
    assert GAP in english.reply


def test_validation_shell_keeps_the_forged_criterion() -> None:
    portuguese = build_validation_questions("rag-retrieval", locale="pt-BR")
    english = build_validation_questions("rag-retrieval", locale=None)

    assert portuguese.node_title == english.node_title
    assert portuguese.questions[0].rubric_criterion == english.questions[0].rubric_criterion
    criterion = portuguese.questions[0].rubric_criterion
    assert criterion in portuguese.questions[0].prompt
    assert portuguese.questions[0].prompt.startswith("Com suas palavras")
    assert english.questions[0].prompt.startswith("In your own words")
    assert portuguese.questions[0].rubric_criterion == criterion


def test_sidebar_override_note_follows_the_account_locale() -> None:
    belief = BeliefState.empty()
    turn = InterviewTurn(
        questions=[
            InterviewQuestion(
                id="q-1",
                topic="Hands-on proof",
                rubric_key="hands_on_proof",
                question="What have you built?",
                example_of_answer="A notebook.",
            ),
        ],
        answers=[InterviewAnswer(question_id="q-1", text="I never built anything")],
    )

    portuguese = apply_transcript_overrides(belief, [turn], locale="pt-BR")
    english = apply_transcript_overrides(belief, [turn], locale=None)

    assert "sem prática" in portuguese.dimensions["hands_on_proof"].note
    assert english.dimensions["hands_on_proof"].note.startswith("No hands-on")
    assert "English" not in (RubricDimension.model_fields["note"].description or "")


def test_gap_concept_stays_the_missed_question() -> None:
    miss = WrongAnswerItem(
        question_id="q-1",
        concept="retry with backoff",
        prompt="What do you do when the API fails?",
        chosen="A",
        chosen_text="Ignore it",
        correct="B",
        correct_text="Retry with backoff",
    )
    paraphrased = KnowledgeGapClassification(
        gaps=[
            KnowledgeGapDraft(
                concept="Handling transient API errors",
                severity="high",
                evidence="Missed the retry question.",
                suggested_remediation="Revise retries.",
            ),
        ],
    )

    pinned = pin_gap_concepts(paraphrased, [miss], locale="pt-BR")

    assert [gap.concept for gap in pinned.gaps] == ["retry with backoff"]
    assert "Revise o conceito" in pinned.gaps[0].suggested_remediation
    assert pinned.gaps[0].evidence.startswith("Missed a question")
