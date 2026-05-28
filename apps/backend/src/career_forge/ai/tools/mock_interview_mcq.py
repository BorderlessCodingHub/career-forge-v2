"""LLM MCQ generator + deterministic fallback for mock interview (HAC-65)."""

from __future__ import annotations

import asyncio
import os
from typing import Literal

from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field, model_validator

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
    rubric_criterion: str
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
    questions: list[McqQuestionDraft] = Field(min_length=5, max_length=7)


def _fallback_mcq_from_templates(node_id: str, session_db) -> MockInterviewQuestionsResponse:
    """Deterministic MCQ when LLM is unavailable (tests / missing API key)."""
    template = build_mock_interview_questions(node_id, session_db)
    questions: list[MockInterviewQuestion] = []
    for item in template.questions:
        correct_text = item.rubric_criterion.rstrip(".")[:120]
        distractors = [
            f"Conceito genérico sem aplicar {template.node_title}",
            "Resposta superficial que não cobre o critério",
            "Confunde termos ou pula a evidência prática",
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
                rubric_criterion=item.rubric_criterion,
                phase=item.phase,
                options=options,
            ),
        )
        answer_key[question_id] = item.correct_option
        rubric.append(item.rubric_criterion)
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
        resolved_key = (api_key if api_key is not None else os.getenv("OPENAI_API_KEY", "")).strip()
        if not resolved_key:
            msg = "OPENAI_API_KEY não configurada"
            raise RuntimeError(msg)
        self._model = model or os.getenv("MOCK_INTERVIEW_MODEL", "gpt-5.4-mini")
        self._llm = ChatOpenAI(model=self._model, api_key=resolved_key, temperature=0.3)

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
        structured = self._llm.with_structured_output(MockInterviewMcqDraft, method="json_schema")
        system = (
            "Você cria mock interviews de múltipla escolha para validar mastery de um bloco de estudo. "
            "Gere 5 a 7 perguntas em português (BR), cada uma com exatamente 4 opções (A–D) e uma única "
            "resposta correta. Misture fases: base (conceito), gap_probe (lacuna), scenario (aplicação). "
            "Distractors devem ser plausíveis mas claramente inferiores à correta. "
            "Ancore perguntas no bloco de estudo e no perfil do learner."
        )
        user = f"{context}\n\nGere o questionário MCQ agora."
        result = structured.invoke([("system", system), ("human", user)])
        return MockInterviewMcqDraft.model_validate(result)


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
