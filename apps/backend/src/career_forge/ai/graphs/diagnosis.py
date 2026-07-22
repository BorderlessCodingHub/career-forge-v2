"""Diagnosis graph — rule-based identity engine (HAC-8)."""

from __future__ import annotations

import re
from collections.abc import AsyncIterator
from typing import Any
from career_forge.ai.streaming.langchain_events import (
    LangChainStreamEvent,
    emit_chain_end,
    emit_chain_start,
    emit_chain_stream,
    new_run_id,
)
from career_forge.schemas.diagnosis import DiagnosisProfile, DiagnosisRequest, DiagnosisResponse

GOAL_TRACKS: dict[str, str] = {
    "rag-engineer": "rag-engineer-beginner",
    "agent-engineer": "agent-engineer-beginner",
    "llm-evals": "llm-evals-beginner",
    "fine-tuning": "fine-tuning-beginner",
    # Legacy hackathon goal ids → default LLM track
    "backend": "rag-engineer-beginner",
    "data": "rag-engineer-beginner",
    "frontend": "rag-engineer-beginner",
}

DOMAIN_SIGNALS: dict[str, tuple[str, ...]] = {
    "rag-embeddings": (
        "javascript",
        "js",
        "programação",
        "programo",
        "lógica",
        "iniciante",
        "meses",
        "embedding",
        "vector",
    ),
    "rag-chunking": ("git", "github", "commit", "branch", "version", "versionar", "reposit", "chunk"),
    "rag-retrieval": (
        "http",
        "api",
        "rest",
        "get",
        "post",
        "status",
        "requisição",
        "endpoint",
        "cliente",
        "servidor",
        "retrieval",
        "retriev",
    ),
    "rag-rerank": (
        "banco",
        "sql",
        "postgres",
        "dados",
        "modelagem",
        "formulário",
        "persist",
        "tabela",
        "rerank",
    ),
}

DOMAIN_GAPS: dict[str, str] = {
    "rag-retrieval": "Vector retrieval — top-k search and relevance debugging",
    "rag-rerank": "Reranking — hybrid retrieval and candidate lift",
    "rag-chunking": "Chunking — size, overlap, and metadata",
    "rag-embeddings": "Embeddings — semantic vectors and similarity",
    "rag-grounding": "Grounded generation — citations and refuse-when-empty",
    "rag-eval": "RAG evaluation — faithfulness and relevance metrics",
}

DOMAIN_STRENGTHS: dict[str, str] = {
    "rag-embeddings": "Already understands basic programming logic",
    "rag-chunking": "Has used GitHub to version projects",
    "rag-retrieval": "Can explain client vs server at a high level",
    "rag-rerank": "Has a notion of persistence in applications",
}

DEFAULT_MASTERY: dict[str, int] = {
    "rag-embeddings": 55,
    "rag-chunking": 45,
    "rag-retrieval": 30,
    "rag-rerank": 25,
    "rag-grounding": 0,
    "rag-eval": 0,
    "rag-production": 0,
}

PRIORITY_ORDER = (
    "rag-retrieval",
    "rag-chunking",
    "rag-rerank",
    "rag-embeddings",
    "rag-grounding",
    "rag-eval",
)

YEARS_XP_BOOST: dict[str, int] = {
    "0-1": 0,
    "1-3": 4,
    "3-5": 8,
    "5+": 12,
}


def _score_text(text: str, keywords: tuple[str, ...]) -> int:
    lowered = text.lower()
    hits = sum(1 for keyword in keywords if keyword in lowered)
    length_bonus = min(len(lowered) // 40, 3)
    uncertainty = sum(
        1 for token in ("acho", "não sei", "talvez", "nunca", "confuso")
        if token in lowered
    )
    return max(0, min(100, 35 + hits * 12 + length_bonus * 5 - uncertainty * 10))


def _merge_answer_text(answers: dict[str, str]) -> str:
    return " ".join(answers.values())


def _profile_label(goal_id: str, avg_score: int, answers: dict[str, str]) -> tuple[str, str]:
    merged = _merge_answer_text(answers).lower()
    if "javascript" in merged or "js" in merged:
        persona = "iniciante_js"
        label = "Iniciante com base em JavaScript"
    elif avg_score >= 70:
        persona = "intermediario_backend"
        label = "Desenvolvedor em transição para backend"
    elif goal_id == "backend":
        persona = "iniciante_backend"
        label = "Iniciante focado em backend"
    else:
        persona = "explorador"
        label = "Explorador em transição de carreira"
    return label, persona


def build_diagnosis_response(payload: DiagnosisRequest) -> DiagnosisResponse:
    """Deterministic diagnosis from onboarding answers (no LLM required for MVP)."""
    merged = _merge_answer_text(payload.answers)
    mastery = dict(DEFAULT_MASTERY)

    for domain, keywords in DOMAIN_SIGNALS.items():
        mastery[domain] = _score_text(merged, keywords)

    xp_boost = YEARS_XP_BOOST.get(payload.years_xp or "", 0)
    if xp_boost:
        for domain in mastery:
            mastery[domain] = min(100, mastery[domain] + xp_boost)

    if re.search(r"space|foguet|orbit|satél|satel", payload.motivation.lower()):
        mastery["rag-retrieval"] = min(100, mastery["rag-retrieval"] + 8)

    avg_score = sum(mastery.values()) // max(len(mastery), 1)
    label, persona = _profile_label(payload.goal_id, avg_score, payload.answers)
    track_id = GOAL_TRACKS.get(payload.goal_id, "rag-engineer-beginner")

    strengths: list[str] = []
    gaps: list[str] = []

    for domain in ("rag-embeddings", "rag-chunking", "rag-retrieval", "rag-rerank"):
        score = mastery.get(domain, 0)
        if score >= 55 and domain in DOMAIN_STRENGTHS:
            strengths.append(DOMAIN_STRENGTHS[domain])
        elif score < 50 and domain in DOMAIN_GAPS:
            gaps.append(DOMAIN_GAPS[domain])

    if not strengths:
        strengths.append("Motivação clara sobre o objetivo de carreira escolhido")

    if DOMAIN_GAPS["rag-eval"] not in gaps and mastery.get("rag-retrieval", 0) < 60:
        gaps.append(DOMAIN_GAPS["rag-eval"])

    if DOMAIN_GAPS["rag-grounding"] not in gaps and mastery.get("rag-retrieval", 0) < 55:
        gaps.append(DOMAIN_GAPS["rag-grounding"])

    if len(gaps) < 2:
        gaps.append("Chunking and retrieval quality — iterate on corpus fit")

    starting_priorities = [
        node_id
        for node_id in PRIORITY_ORDER
        if mastery.get(node_id, 100) < 70
    ][:3] or ["rag-retrieval", "rag-chunking", "rag-rerank"]

    return DiagnosisResponse(
        profile=DiagnosisProfile(
            label=label,
            track_id=track_id,
            persona_slug=persona,
        ),
        strengths=strengths[:3],
        gaps=gaps[:4],
        starting_priorities=starting_priorities,
        estimated_mastery=mastery,
    )


class DiagnosisGraphRunnable:
    """GraphRunnable that maps onboarding answers → DiagnosisResponse."""

    graph_name = "diagnosis"

    async def astream_events(
        self,
        input_data: dict[str, Any],
        *,
        version: str = "v2",
    ) -> AsyncIterator[LangChainStreamEvent]:
        del version
        payload = DiagnosisRequest.model_validate(input_data)
        diagnosis = build_diagnosis_response(payload)
        run_id = new_run_id()

        yield emit_chain_start(self.graph_name, run_id)

        yield emit_chain_stream(
            "analyze_signals",
            run_id,
            {
                "type": "progress",
                "step": "analyze_signals",
                "message": "Mapeando sinais nas respostas do onboarding",
            },
        )

        output = diagnosis.model_dump()
        yield emit_chain_end(
            self.graph_name,
            run_id,
            output=output,
            input_data=input_data,
        )


def build_diagnosis_graph() -> DiagnosisGraphRunnable:
    """Return configured diagnosis graph runnable."""
    return DiagnosisGraphRunnable()
