"""Diagnosis graph — rule-based identity engine (HAC-8)."""

from __future__ import annotations

import re
from collections.abc import AsyncIterator
from typing import Any
from uuid import uuid4

from career_forge.schemas.diagnosis import DiagnosisProfile, DiagnosisRequest, DiagnosisResponse

GOAL_TRACKS: dict[str, str] = {
    "backend": "backend-beginner",
    "data": "backend-beginner",
    "frontend": "backend-beginner",
}

DOMAIN_SIGNALS: dict[str, tuple[str, ...]] = {
    "js": (
        "javascript",
        "js",
        "programação",
        "programo",
        "lógica",
        "iniciante",
        "meses",
    ),
    "git": ("git", "github", "commit", "branch", "version", "versionar", "reposit"),
    "http": (
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
    ),
    "db": (
        "banco",
        "sql",
        "postgres",
        "dados",
        "modelagem",
        "formulário",
        "persist",
        "tabela",
    ),
}

DOMAIN_GAPS: dict[str, str] = {
    "http": "HTTP e APIs REST — métodos, status codes e contrato",
    "db": "Banco relacional — modelagem e SQL aplicado",
    "git": "Git avançado — branches, merge e fluxo colaborativo",
    "js": "JavaScript aplicado — sintaxe e raciocínio assíncrono",
    "rest": "APIs REST — recursos, verbos e stateless",
    "auth": "Autenticação — sessões, tokens e fluxo seguro",
}

DOMAIN_STRENGTHS: dict[str, str] = {
    "js": "Já entende lógica básica e sintaxe JavaScript",
    "git": "Já usou GitHub superficialmente para versionar projetos",
    "http": "Consegue explicar diferença entre frontend e backend",
    "db": "Tem noção de persistência de dados em aplicações",
}

DEFAULT_MASTERY: dict[str, int] = {
    "js": 55,
    "git": 45,
    "http": 30,
    "db": 25,
    "rest": 0,
    "auth": 0,
    "final": 0,
}

PRIORITY_ORDER = ("http", "git", "db", "js", "rest", "auth")

YEARS_XP_BOOST: dict[str, int] = {
    "0-1": 0,
    "1-3": 4,
    "3-5": 8,
    "5+": 12,
}


def _lc_event(
    event: str,
    name: str,
    run_id: str,
    data: dict[str, Any],
) -> dict[str, Any]:
    return {
        "event": event,
        "name": name,
        "run_id": run_id,
        "tags": [],
        "metadata": {},
        "data": data,
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
        mastery["http"] = min(100, mastery["http"] + 8)

    avg_score = sum(mastery.values()) // max(len(mastery), 1)
    label, persona = _profile_label(payload.goal_id, avg_score, payload.answers)
    track_id = GOAL_TRACKS.get(payload.goal_id, "backend-beginner")

    strengths: list[str] = []
    gaps: list[str] = []

    for domain in ("js", "git", "http", "db"):
        score = mastery.get(domain, 0)
        if score >= 55 and domain in DOMAIN_STRENGTHS:
            strengths.append(DOMAIN_STRENGTHS[domain])
        elif score < 50 and domain in DOMAIN_GAPS:
            gaps.append(DOMAIN_GAPS[domain])

    if not strengths:
        strengths.append("Motivação clara sobre o objetivo de carreira escolhido")

    if "auth" not in gaps and mastery.get("http", 0) < 60:
        gaps.append(DOMAIN_GAPS["auth"])

    if "rest" not in gaps and mastery.get("http", 0) < 55:
        gaps.append(DOMAIN_GAPS["rest"])

    if len(gaps) < 2:
        gaps.append("Persistência relacional — modelagem e SQL aplicado")

    starting_priorities = [
        node_id
        for node_id in PRIORITY_ORDER
        if mastery.get(node_id, 100) < 70
    ][:3] or ["http", "git", "db"]

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
    ) -> AsyncIterator[dict[str, Any]]:
        del version
        payload = DiagnosisRequest.model_validate(input_data)
        diagnosis = build_diagnosis_response(payload)
        run_id = str(uuid4())

        yield _lc_event("on_chain_start", self.graph_name, run_id, {})

        yield _lc_event(
            "on_chain_stream",
            "analyze_signals",
            run_id,
            {
                "chunk": {
                    "type": "progress",
                    "step": "analyze_signals",
                    "message": "Mapeando sinais nas respostas do onboarding",
                },
            },
        )

        output = diagnosis.model_dump()
        yield _lc_event(
            "on_chain_end",
            self.graph_name,
            run_id,
            {"output": output, "input": input_data},
        )


def build_diagnosis_graph() -> DiagnosisGraphRunnable:
    """Return configured diagnosis graph runnable."""
    return DiagnosisGraphRunnable()
