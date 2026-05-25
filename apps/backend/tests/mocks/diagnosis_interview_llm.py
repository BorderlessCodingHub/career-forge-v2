"""Test-only deterministic diagnosis interview LLM (pytest fixtures)."""

from __future__ import annotations

from career_forge.schemas.diagnosis import DiagnosisProfile, DiagnosisResponse
from career_forge.schemas.diagnosis_interview import (
    PROFILE_DIMENSION_LABELS,
    MAX_QUESTIONS_PER_TURN,
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

COMPOUND_ROUND_ONE = (
    "Conte a coisa mais concreta que você já fez ou tentou nesse caminho — "
    "o que construiu, com quem, quanto tempo dedica por semana e o que aprendeu.",
    "Ex.: fiz um app em grupo na faculdade, uso Git básico, estudo 5h/semana com tutoriais.",
)

FOLLOW_UP_BANK: dict[RubricDimensionKey, tuple[str, str]] = {
    "motivation_goal": (
        "O que te motiva de verdade a seguir esse caminho agora?",
        "Ex.: quero trabalhar com produto de IA e impacto global.",
    ),
    "background_transfer": (
        "De onde você vem e o que do seu background ajuda nessa transição?",
        "Ex.: venho de vendas, aprendi a explicar ideias complexas.",
    ),
    "learning_velocity": (
        "Com que frequência você pratica e como mantém consistência?",
        "Ex.: 1h por dia durante a semana, projetos no fim de semana.",
    ),
    "hands_on_proof": (
        "Qual foi a entrega mais concreta que você já tentou?",
        "Ex.: API simples no GitHub, dashboard, bot, pipeline.",
    ),
    "constraints": (
        "Quais limitações reais você tem hoje (tempo, idioma, budget)?",
        "Ex.: 8h/semana, inglês intermediário, sem bootcamp pago.",
    ),
}

TRACK_BY_GOAL = {
    "fullstack": "fullstack-beginner",
    "data": "data-beginner",
    "ai-ml": "ai-ml-beginner",
    "web3": "web3-beginner",
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

    if any(token in lower for token in ("git", "github", "api", "projeto", "app", "deploy")):
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
        interviewable = belief.interviewable_keys()
        if not interviewable:
            return []

        if "hands_on_proof" not in interviewable:
            interviewable = [key for key in interviewable if key != "hands_on_proof"]

        if round_count == 0 and len(belief.interviewable_keys()) >= 2:
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

        questions: list[InterviewQuestion] = []
        for index, key in enumerate(interviewable[:MAX_QUESTIONS_PER_TURN]):
            prompt, example = FOLLOW_UP_BANK[key]
            questions.append(
                InterviewQuestion(
                    id=f"q-r{round_count + 1}-{index + 1}",
                    topic=PROFILE_DIMENSION_LABELS[key],
                    rubric_key=key,
                    question=prompt,
                    example_of_answer=example,
                ),
            )
        return questions

    async def finalize_diagnosis(
        self,
        belief: BeliefState,
        intake: DiagnosisIntake,
    ) -> DiagnosisResponse:
        track_id = TRACK_BY_GOAL.get(intake.goal_id, "career-beginner")
        velocity = belief.dimensions["learning_velocity"].confidence
        proof = belief.dimensions["hands_on_proof"].confidence

        mastery = {
            "js": int(velocity * 100),
            "git": int(min(1.0, proof + 0.1) * 70),
            "http": int(min(1.0, proof) * 65),
            "db": int(min(1.0, proof - 0.1) * 60),
            "rest": int(belief.dimensions["background_transfer"].confidence * 50),
            "auth": 0,
            "final": 0,
        }

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

        goal_gaps = {
            "fullstack": ["HTTP/APIs e integração frontend-backend"],
            "data": ["SQL aplicado e pipelines de dados"],
            "ai-ml": ["Fundamentos de ML e experimentação reprodutível"],
            "web3": ["Smart contracts e segurança básica on-chain"],
        }
        gaps.extend(goal_gaps.get(intake.goal_id, ["Fundamentos de engenharia de software"])[:1])

        priorities = ["http", "git", "db"]
        if intake.goal_id == "data":
            priorities = ["db", "http", "git"]
        elif intake.goal_id == "ai-ml":
            priorities = ["http", "db", "git"]

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
