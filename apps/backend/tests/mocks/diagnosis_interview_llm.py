"""Test-only deterministic diagnosis interview LLM (pytest fixtures)."""

from __future__ import annotations

from career_forge.ai.interview.script import (
    build_round_questions,
    round_index_for_count,
)
from career_forge.schemas.diagnosis import DiagnosisProfile, DiagnosisResponse
from career_forge.schemas.diagnosis_interview import (
    RubricDimensionKey,
    BeliefState,
    CvSignals,
    DiagnosisIntake,
    InterviewAnswer,
    InterviewQuestion,
    InterviewTurn,
    RubricDimension,
    SATURATION_CONFIDENCE_THRESHOLD,
)

TRACK_BY_GOAL = {
    "rag-engineer": "rag-engineer-beginner",
    "agent-engineer": "agent-engineer-beginner",
    "llm-evals": "llm-evals-beginner",
    "fine-tuning": "fine-tuning-beginner",
}

MASTERY_NODES_BY_GOAL = {
    "rag-engineer": [
        "rag-embeddings",
        "rag-chunking",
        "rag-retrieval",
        "rag-rerank",
        "rag-grounding",
        "rag-eval",
        "rag-production",
    ],
    "agent-engineer": [
        "agent-tool-use",
        "agent-mcp",
        "agent-planning",
        "agent-memory",
        "agent-failure-modes",
        "agent-observability",
        "agent-ship",
    ],
    "llm-evals": [
        "evals-metrics",
        "evals-llm-judge",
        "evals-datasets",
        "evals-regression",
        "evals-tracing",
        "evals-online",
        "evals-llmops",
    ],
    "fine-tuning": [
        "ft-data-prep",
        "ft-sft",
        "ft-lora",
        "ft-eval",
        "ft-dpo",
        "ft-serve",
        "ft-alignment",
    ],
}

GOAL_GAPS = {
    "rag-engineer": ["Grounded retrieval and citation discipline"],
    "agent-engineer": ["Tool-loop failure modes and MCP connectors"],
    "llm-evals": ["Judge calibration and regression gates"],
    "fine-tuning": ["LoRA setup and preference-data quality"],
}


def _boost_dim(
    belief: BeliefState,
    key: RubricDimensionKey,
    confidence: float,
    evidence: str,
    note: str,
) -> None:
    dim = belief.dimensions[key]
    new_conf = max(dim.confidence, confidence)
    belief.dimensions[key] = RubricDimension(
        key=key,
        label=dim.label,
        confidence=new_conf,
        evidence=[*dim.evidence, evidence][:5],
        status="mapped" if new_conf >= SATURATION_CONFIDENCE_THRESHOLD else "needs_clarification",
        note=note or dim.note,
    )


def _apply_rich_answer(belief: BeliefState, text: str) -> None:
    lower = text.lower()
    score = min(0.88, 0.5 + len(text) / 100)

    negative_proof = any(
        phrase in lower
        for phrase in (
            "nunca",
            "não tenho",
            "nao tenho",
            "sem prática",
            "sem pratica",
            "zero projeto",
            "nenhum projeto",
            "só teoria",
            "so teoria",
            "não fiz",
            "nao fiz",
        )
    )

    if negative_proof:
        _boost_dim(
            belief,
            "hands_on_proof",
            0.68,
            text[:160],
            "Sem prática hands-on ainda — baseline iniciante confirmado",
        )
    else:
        _boost_dim(belief, "hands_on_proof", score, text[:160], text[:100])

    if any(token in lower for token in ("semana", "dia", "hora", "consistent", "estudo", "português", "portugues", "inglês", "ingles")):
        _boost_dim(
            belief,
            "constraints",
            min(0.82, score),
            text[:120],
            "Tempo, idioma ou rotina de estudo mencionados",
        )
        _boost_dim(
            belief,
            "learning_velocity",
            min(0.85, score),
            text[:120],
            "Ritmo e consistência mencionados na resposta",
        )

    if any(token in lower for token in ("rag-chunking", "github", "api", "projeto", "app", "deploy")):
        _boost_dim(
            belief,
            "background_transfer",
            min(0.8, score - 0.05),
            text[:120],
            "Ferramentas e contexto prático citados",
        )

    if any(token in lower for token in ("tempo", "inglês", "budget", "bootcamp", "faculdade")):
        _boost_dim(
            belief,
            "constraints",
            min(0.78, score - 0.08),
            text[:120],
            "Restrições ou contexto real mencionados",
        )


class MockDiagnosisInterviewLlm:
    """Deterministic LLM for pytest — not used in production."""

    async def initialize_belief(
        self,
        intake: DiagnosisIntake,
        cv_signals: CvSignals | None,
        cv_text: str | None,
    ) -> BeliefState:
        belief = BeliefState.empty()

        _boost_dim(
            belief,
            "motivation_goal",
            0.72,
            intake.motivation[:160],
            intake.motivation[:100],
        )

        if intake.years_xp:
            boost = {"0-1": 0.45, "1-3": 0.58, "3-5": 0.68, "5+": 0.78}.get(intake.years_xp, 0.4)
            _boost_dim(
                belief,
                "learning_velocity",
                boost,
                f"Intake: {intake.years_xp} anos",
                f"Intake indica {intake.years_xp} de prática/experiência",
            )

        if cv_signals and cv_signals.roles:
            _boost_dim(
                belief,
                "background_transfer",
                0.62,
                f"CV: {cv_signals.roles[0]}",
                f"CV indica background: {cv_signals.roles[0]}",
            )

        del cv_text
        return belief

    async def update_belief(
        self,
        belief: BeliefState,
        intake: DiagnosisIntake,
        transcript: list[InterviewTurn],
        answers: list[InterviewAnswer],
    ) -> BeliefState:
        del intake
        updated = belief.model_copy(deep=True)
        answer_by_qid = {answer.question_id: answer.text for answer in answers}
        last_turn = transcript[-1] if transcript else None
        if not last_turn:
            return updated

        for question in last_turn.questions:
            text = answer_by_qid.get(question.id, "")
            if not text:
                continue
            _apply_rich_answer(updated, text)
            _boost_dim(
                updated,
                question.rubric_key,
                min(0.85, 0.55 + len(text) / 80),
                text[:160],
                text[:100],
            )
        return updated

    async def plan_questions(
        self,
        belief: BeliefState,
        intake: DiagnosisIntake,
        transcript: list[InterviewTurn],
        round_count: int,
    ) -> list[InterviewQuestion]:
        del intake
        round_index = round_index_for_count(round_count)
        if round_index is None:
            return []
        return build_round_questions(round_index, belief=belief, transcript=transcript)

    async def finalize_diagnosis(
        self,
        belief: BeliefState,
        intake: DiagnosisIntake,
    ) -> DiagnosisResponse:
        track_id = TRACK_BY_GOAL.get(intake.goal_id, "rag-engineer-beginner")
        velocity = belief.dimensions["learning_velocity"].confidence
        proof = belief.dimensions["hands_on_proof"].confidence

        node_ids = MASTERY_NODES_BY_GOAL.get(
            intake.goal_id,
            MASTERY_NODES_BY_GOAL["rag-engineer"],
        )
        scores = [
            int(velocity * 100),
            int(min(1.0, proof + 0.1) * 70),
            int(min(1.0, proof) * 65),
            int(min(1.0, proof - 0.1) * 60),
            int(belief.dimensions["background_transfer"].confidence * 50),
            0,
            0,
        ]
        mastery = {node_id: scores[i] for i, node_id in enumerate(node_ids)}

        strengths = [
            belief.dimensions["motivation_goal"].note or "Motivação clara para a transição",
        ]
        if proof >= 0.55:
            strengths.append("Evidência prática citada na entrevista")

        gaps = []
        if proof < 0.65:
            gaps.append("Prova prática — entregar um artefato mínimo (repo, demo ou deploy)")
        if velocity < 0.65:
            gaps.append("Consistência de estudo — rotina semanal mensurável")

        gaps.extend(GOAL_GAPS.get(intake.goal_id, ["Fundamentos de engenharia de software"])[:1])

        priorities = list(node_ids[2:5])

        return DiagnosisResponse(
            profile=DiagnosisProfile(
                label=f"Iniciante em transição — {intake.goal_id}",
                track_id=track_id,
                persona_slug="transicao_iniciante",
            ),
            strengths=strengths[:3],
            gaps=gaps[:4],
            starting_priorities=priorities[:3],
            estimated_mastery=mastery,
        )
