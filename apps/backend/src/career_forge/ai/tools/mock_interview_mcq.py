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
        description="Conceito TÉCNICO específico testado (ex: 'list comprehension', "
        "'np.reshape', 'idempotência de PUT'). Nunca logística de estudo.",
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
        description="Assunto TÉCNICO do bloco, ignorando linguagem de logística do título "
        "(ex: 'Python para AI/ML', 'APIs REST'). Determine isto ANTES das perguntas.",
    )
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
            "Você cria mock interviews de múltipla escolha que validam DOMÍNIO TÉCNICO do "
            "conteúdo de um capítulo de estudo.\n\n"
            "PASSO 1 — Determine o `subject`: o ASSUNTO TÉCNICO real do capítulo. "
            "O título pode conter linguagem de logística de estudo (ex: 'criar rotina de estudo', "
            "'Semanas 1–4', 'dominar o mínimo de'). IGNORE essa moldura e extraia o tema técnico "
            "(ex: 'Python para AI/ML', 'APIs REST', 'Git e versionamento').\n\n"
            "PASSO 2 — Gere 5 a 7 perguntas em português (BR) que testam COMPREENSÃO TÉCNICA do "
            "subject. Cada pergunta tem exatamente 4 opções (A–D), uma única correta, e um `concept` "
            "técnico específico (ex: 'list comprehension', 'np.reshape', 'idempotência de PUT').\n\n"
            "PROIBIDO terminantemente: perguntas sobre hábitos de estudo, rotina, agenda, gestão de "
            "tempo, motivação, como organizar o aprendizado, quantas horas estudar. Isso NÃO é "
            "conhecimento técnico e não pode aparecer.\n\n"
            "Misture fases: base (conceito fundamental), gap_probe (erro comum/lacuna típica), "
            "scenario (aplicação prática). Distractors plausíveis mas claramente inferiores. "
            "Ancore as perguntas nas referências oficiais fornecidas quando houver."
        )
        user = (
            f"{context}\n\n"
            "Determine o subject técnico (ignorando logística do título) e gere o questionário MCQ agora."
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
