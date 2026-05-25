"""Test-only deterministic diagnosis interview LLM (pytest fixtures)."""

from __future__ import annotations

from career_forge.schemas.diagnosis import DiagnosisProfile, DiagnosisResponse
from career_forge.schemas.diagnosis_interview import (
    CTRR_DIMENSION_LABELS,
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


class MockDiagnosisInterviewLlm:
    """Deterministic LLM for pytest — not used in production."""

    QUESTION_BANK: dict[RubricDimensionKey, tuple[str, str]] = {
        "learning_stage": (
            "Como você descreveria seu nível atual com programação?",
            "Ex.: estou no início, fiz um curso de JS há 3 meses.",
        ),
        "project_scope": (
            "Qual foi o maior projeto que você já construiu ou tentou construir?",
            "Ex.: um todo app, uma API simples, um site estático.",
        ),
        "background_context": (
            "De onde você vem e como está estudando tecnologia hoje?",
            "Ex.: migrei de outra área, estudo sozinho à noite.",
        ),
        "hands_on_evidence": (
            "Conte algo concreto que você já fez ou tentou fazer na prática.",
            "Ex.: subi um projeto no GitHub, fiz exercícios de lógica.",
        ),
        "git": (
            "Você já usou Git ou GitHub em algum projeto?",
            "Ex.: clone, commit, push — mesmo que básico.",
        ),
        "client_server": (
            "Consegue explicar, com suas palavras, frontend vs backend?",
            "Ex.: frontend é o que o usuário vê; backend processa dados.",
        ),
        "http_apis": (
            "Você já fez ou viu uma requisição HTTP ou chamada de API?",
            "Ex.: GET/POST, JSON, status code 200 ou 404.",
        ),
        "database": (
            "Já trabalhou ou ouviu falar de banco de dados em algum projeto?",
            "Ex.: salvar dados de um formulário, SQL básico.",
        ),
    }

    async def initialize_belief(
        self,
        intake: DiagnosisIntake,
        cv_signals: CvSignals | None,
        cv_text: str | None,
    ) -> BeliefState:
        belief = BeliefState.empty()
        merged = intake.motivation.lower()

        if intake.years_xp:
            boost = {"0-1": 0.35, "1-3": 0.5, "3-5": 0.65, "5+": 0.75}.get(intake.years_xp, 0.3)
            belief.dimensions["learning_stage"] = RubricDimension(
                key="learning_stage",
                label=CTRR_DIMENSION_LABELS["learning_stage"],
                confidence=boost,
                evidence=[f"Autodeclaração: {intake.years_xp} anos de experiência"],
            )
            belief.dimensions["background_context"] = RubricDimension(
                key="background_context",
                label=CTRR_DIMENSION_LABELS["background_context"],
                confidence=min(0.7, boost),
                evidence=[intake.motivation[:120]],
            )

        if cv_signals:
            if cv_signals.skills:
                if any(s.lower().find("git") >= 0 for s in cv_signals.skills):
                    belief.dimensions["git"] = RubricDimension(
                        key="git",
                        label=CTRR_DIMENSION_LABELS["git"],
                        confidence=0.78,
                        evidence=[f"CV menciona: {', '.join(cv_signals.skills[:3])}"],
                    )
                if any("api" in s.lower() or "http" in s.lower() for s in cv_signals.skills):
                    belief.dimensions["http_apis"] = RubricDimension(
                        key="http_apis",
                        label=CTRR_DIMENSION_LABELS["http_apis"],
                        confidence=0.76,
                        evidence=["CV menciona APIs/HTTP"],
                    )
            if cv_signals.roles:
                belief.dimensions["hands_on_evidence"] = RubricDimension(
                    key="hands_on_evidence",
                    label=CTRR_DIMENSION_LABELS["hands_on_evidence"],
                    confidence=0.72,
                    evidence=[f"CV: {cv_signals.roles[0]}"],
                )

        if any(token in merged for token in ("javascript", "js", "program")):
            belief.dimensions["learning_stage"].confidence = max(
                belief.dimensions["learning_stage"].confidence,
                0.55,
            )
            belief.dimensions["learning_stage"].evidence.append("Motivação menciona programação")

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
            score = min(0.85, 0.45 + len(text) / 120)
            dim = updated.dimensions[question.rubric_key]
            updated.dimensions[question.rubric_key] = RubricDimension(
                key=question.rubric_key,
                label=dim.label,
                confidence=max(dim.confidence, score),
                evidence=[*dim.evidence, text[:160]],
            )
        return updated

    async def plan_questions(
        self,
        belief: BeliefState,
        intake: DiagnosisIntake,
        transcript: list[InterviewTurn],
        round_count: int,
    ) -> list[InterviewQuestion]:
        del intake, transcript
        unsaturated = belief.unsaturated_keys(SATURATION_CONFIDENCE_THRESHOLD)
        if not unsaturated:
            return []

        questions: list[InterviewQuestion] = []
        for index, key in enumerate(unsaturated[:MAX_QUESTIONS_PER_TURN]):
            prompt, example = self.QUESTION_BANK[key]
            questions.append(
                InterviewQuestion(
                    id=f"q-r{round_count + 1}-{index + 1}",
                    topic=CTRR_DIMENSION_LABELS[key],
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
        mastery = {
            "js": int(belief.dimensions["learning_stage"].confidence * 100),
            "git": int(belief.dimensions["git"].confidence * 100),
            "http": int(belief.dimensions["http_apis"].confidence * 100),
            "db": int(belief.dimensions["database"].confidence * 100),
            "rest": int(belief.dimensions["client_server"].confidence * 40),
            "auth": 0,
            "final": 0,
        }
        strengths: list[str] = []
        gaps: list[str] = []

        if belief.dimensions["learning_stage"].confidence >= 0.55:
            strengths.append("Motivação clara e noção do próprio estágio de aprendizado")
        if belief.dimensions["git"].confidence >= 0.6:
            strengths.append("Já tem exposição a Git/versionamento")
        if belief.dimensions["http_apis"].confidence >= 0.55:
            strengths.append("Familiaridade inicial com HTTP e APIs")

        if belief.dimensions["http_apis"].confidence < 0.6:
            gaps.append("HTTP e APIs REST — métodos, status codes e contrato")
        if belief.dimensions["database"].confidence < 0.6:
            gaps.append("Banco relacional — modelagem e SQL aplicado")
        if belief.dimensions["git"].confidence < 0.55:
            gaps.append("Git colaborativo — branches, merge e fluxo em equipe")

        if not strengths:
            strengths.append("Motivação clara sobre o objetivo de carreira escolhido")
        if len(gaps) < 2:
            gaps.append("Persistência relacional — modelagem e SQL aplicado")

        priorities = []
        for node_id, key in (
            ("http", "http_apis"),
            ("git", "git"),
            ("db", "database"),
        ):
            if belief.dimensions[key].confidence < 0.7:
                priorities.append(node_id)
        if not priorities:
            priorities = ["http", "git", "db"]

        label = "Iniciante em transição para backend"
        if intake.goal_id == "backend":
            label = "Iniciante focado em backend"

        return DiagnosisResponse(
            profile=DiagnosisProfile(
                label=label,
                track_id="backend-beginner",
                persona_slug="transicao_iniciante",
            ),
            strengths=strengths[:3],
            gaps=gaps[:4],
            starting_priorities=priorities[:3],
            estimated_mastery=mastery,
        )
