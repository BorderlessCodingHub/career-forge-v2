"""LLM MCQ generator + deterministic fallback for mock interview (HAC-65)."""

from __future__ import annotations

import asyncio
from typing import Literal

from pydantic import BaseModel, Field, model_validator

from career_forge.ai.llm.client import StructuredToolClient
from career_forge.schemas.mock_interview import (
    MockInterviewOption,
    MockInterviewQuestion,
    MockInterviewQuestionsResponse,
)
from career_forge.services.mock_interview import build_mock_interview_questions
from career_forge.services.mock_interview_context import format_context_for_prompt
from career_forge.services.mock_interview_session import (
    MockInterviewSessionRecord,
    create_session_id,
    save_mock_interview_session,
)
from career_forge.services.forge_context import LearnerForgeContext

MCQ_LETTERS = ("A", "B", "C", "D")


class McqOptionDraft(BaseModel):
    letter: Literal["A", "B", "C", "D"]
    text: str = Field(min_length=4, max_length=240)


class McqQuestionDraft(BaseModel):
    prompt: str = Field(min_length=12)
    label: str
    phase: Literal["base", "gap_probe", "scenario"]
    concept: str = Field(
        min_length=2,
        max_length=120,
        description="Specific TECHNICAL concept tested (e.g. 'list comprehension', "
        "'np.reshape', 'PUT idempotency'). Never study-logistics language.",
    )
    hint: str | None = None
    options: list[McqOptionDraft] = Field(min_length=4, max_length=4)
    correct_option: Literal["A", "B", "C", "D"]

    @model_validator(mode="after")
    def validate_mcq_shape(self) -> McqQuestionDraft:
        letters = {option.letter for option in self.options}
        if letters != set(MCQ_LETTERS):
            msg = "options must include exactly A, B, C, D"
            raise ValueError(msg)
        if self.correct_option not in letters:
            msg = "correct_option must match one of the option letters"
            raise ValueError(msg)
        return self


class MockInterviewMcqDraft(BaseModel):
    subject: str = Field(
        min_length=2,
        max_length=120,
        description="TECHNICAL subject of the block, ignoring title logistics language "
        "(e.g. 'Python for AI/ML', 'REST APIs'). Determine this BEFORE the questions.",
    )
    questions: list[McqQuestionDraft] = Field(min_length=5, max_length=7)


def _fallback_mcq_from_templates(node_id: str, session_db) -> MockInterviewQuestionsResponse:
    """Deterministic MCQ when LLM is unavailable (tests / missing API key)."""
    template = build_mock_interview_questions(node_id, session_db)
    questions: list[MockInterviewQuestion] = []
    for item in template.questions:
        correct_text = item.rubric_criterion.rstrip(".")[:120]
        distractors = [
            f"Generic concept without applying {template.node_title}",
            "Shallow answer that does not cover the criterion",
            "Confuses terms or skips practical evidence",
        ]
        options = [
            MockInterviewOption(letter="A", text=correct_text),
            MockInterviewOption(letter="B", text=distractors[0]),
            MockInterviewOption(letter="C", text=distractors[1]),
            MockInterviewOption(letter="D", text=distractors[2]),
        ]
        questions.append(
            MockInterviewQuestion(
                id=item.id,
                index=item.index,
                label=item.label,
                prompt=item.prompt,
                hint=item.hint,
                rubric_criterion=item.rubric_criterion,
                phase=item.phase,
                options=options,
            ),
        )
    return MockInterviewQuestionsResponse(
        node_id=template.node_id,
        node_title=template.node_title,
        node_icon=template.node_icon,
        session_id=None,
        format="mcq",
        total_questions=len(questions),
        questions=questions,
    )


def _draft_to_public(
    node_id: str,
    node_title: str,
    node_icon: str,
    draft: MockInterviewMcqDraft,
) -> tuple[MockInterviewQuestionsResponse, dict[str, str], list[str]]:
    questions: list[MockInterviewQuestion] = []
    answer_key: dict[str, str] = {}
    rubric: list[str] = []
    for index, item in enumerate(draft.questions, start=1):
        question_id = f"{node_id}-mi-q{index}"
        options = [
            MockInterviewOption(letter=option.letter, text=option.text)
            for option in sorted(item.options, key=lambda opt: opt.letter)
        ]
        questions.append(
            MockInterviewQuestion(
                id=question_id,
                index=index,
                label=item.label,
                prompt=item.prompt,
                hint=item.hint,
                rubric_criterion=item.concept,
                concept=item.concept,
                phase=item.phase,
                options=options,
            ),
        )
        answer_key[question_id] = item.correct_option
        rubric.append(item.concept)
    response = MockInterviewQuestionsResponse(
        node_id=node_id,
        node_title=node_title,
        node_icon=node_icon,
        session_id=None,
        format="mcq",
        total_questions=len(questions),
        questions=questions,
    )
    return response, answer_key, rubric


class OpenAiMockInterviewMcqGenerator:
    def __init__(self, *, model: str | None = None, api_key: str | None = None) -> None:
        self._client = StructuredToolClient(
            model_env="MOCK_INTERVIEW_MODEL",
            default_model="gpt-5.4-mini",
            temperature=0.3,
            model=model,
            api_key=api_key,
        )

    async def generate(
        self,
        *,
        study_block: dict,
        learner: LearnerForgeContext | None,
    ) -> MockInterviewMcqDraft:
        return await asyncio.to_thread(self._invoke, study_block=study_block, learner=learner)

    def _invoke(
        self,
        *,
        study_block: dict,
        learner: LearnerForgeContext | None,
    ) -> MockInterviewMcqDraft:
        context = format_context_for_prompt(study_block, learner)
        system = (
            "You create multiple-choice mock interviews that validate TECHNICAL MASTERY of "
            "a study chapter.\n\n"
            "STEP 1 — Determine `subject`: the real TECHNICAL TOPIC of the chapter. "
            "The title may include study-logistics language (e.g. 'build a study routine', "
            "'Weeks 1–4', 'master the minimum of'). IGNORE that frame and extract the technical topic "
            "(e.g. 'Python for AI/ML', 'REST APIs', 'Git and versioning').\n\n"
            "STEP 2 — Generate 5 to 7 questions in English that test TECHNICAL UNDERSTANDING of "
            "the subject. Each question has exactly 4 options (A–D), one correct answer, and a specific "
            "technical `concept` (e.g. 'list comprehension', 'np.reshape', 'PUT idempotency').\n\n"
            "STRICTLY FORBIDDEN: questions about study habits, routine, scheduling, time management, "
            "motivation, how to organize learning, or how many hours to study. That is NOT "
            "technical knowledge and must not appear.\n\n"
            "Mix phases: base (fundamental concept), gap_probe (common mistake/typical gap), "
            "scenario (practical application). Plausible but clearly weaker distractors. "
            "Anchor questions in the official references when provided."
        )
        user = (
            f"{context}\n\n"
            "Determine the technical subject (ignoring title logistics) and generate the MCQ questionnaire now."
        )
        return self._client.invoke(system=system, user=user, schema=MockInterviewMcqDraft)


async def generate_mcq_mock_interview(
    *,
    user_id: str,
    node_id: str,
    study_block: dict,
    learner: LearnerForgeContext | None,
    session_db,
    node_icon: str = "code",
) -> MockInterviewQuestionsResponse:
    """Generate MCQ session; uses LLM when configured, else deterministic fallback."""
    node_title = str(study_block.get("title") or node_id)
    try:
        generator = OpenAiMockInterviewMcqGenerator()
        draft = await generator.generate(study_block=study_block, learner=learner)
        public, answer_key, rubric = _draft_to_public(node_id, node_title, node_icon, draft)
    except RuntimeError:
        public = _fallback_mcq_from_templates(node_id, session_db)
        answer_key = {
            question.id: "A"
            for question in public.questions
        }
        rubric = [question.rubric_criterion for question in public.questions]

    session_id = create_session_id()
    save_mock_interview_session(
        MockInterviewSessionRecord(
            session_id=session_id,
            user_id=user_id,
            node_id=node_id,
            node_title=node_title,
            rubric=rubric,
            answer_key=answer_key,
            questions_public=[question.model_dump() for question in public.questions],
        ),
    )
    return public.model_copy(update={"session_id": session_id})
