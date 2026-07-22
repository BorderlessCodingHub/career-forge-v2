"""Roadmap forge graph — multi-step forge pipeline (HAC-18)."""

from __future__ import annotations

import asyncio
import os
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
from career_forge.ai.tools.openai_web_search import (
    WebSearchClient,
    WebSearchResult,
    build_openai_web_search_client_from_env,
)
from career_forge.ai.tools.study_plan_evaluator import (
    StudyPlanEvaluator,
    build_study_plan_evaluator_from_env,
)
from career_forge.ai.tools.study_plan_planner import (
    StudyPlanPlanner,
    build_study_plan_planner_from_env,
)
from career_forge.schemas.common import Priority, SkillStatus, UserSkillNode
from career_forge.schemas.diagnosis import DiagnosisResponse
from career_forge.services.forge_planning import (
    build_draft_study_plan,
    evaluation_artifact,
    study_plan_to_graph,
)
from career_forge.services.forge_context import (
    LearnerForgeContext,
    build_forge_context_from_input,
)
from career_forge.services.roadmap.catalog import load_roadmap_catalog

DEFAULT_STREAM_DELAY_SEC = 1.5
MAX_RESEARCH_ITERATIONS = 3
MAX_EVALUATION_ITERATIONS = 2

FORGE_STEPS = (
    "load_topics",
    "analyze_gaps",
    "research_enrich",
    "accumulate_graph",
)


def _load_catalog(track_id: str | None = None) -> dict[str, Any]:
    return load_roadmap_catalog(track_id)


def _mastery_to_status(score: int) -> SkillStatus:
    if score >= 70:
        return SkillStatus.APROVADO
    if score >= 45:
        return SkillStatus.RECOMENDADO
    return SkillStatus.BLOQUEADO


def _mastery_to_priority(score: int, is_priority: bool) -> Priority:
    if is_priority and score < 55:
        return Priority.HIGH
    if score < 40:
        return Priority.MEDIUM
    return Priority.LOW


def build_accumulated_graph(diagnosis: DiagnosisResponse) -> list[UserSkillNode]:
    """Deterministic graph from catalog + diagnosis mastery scores."""
    catalog = _load_catalog(diagnosis.profile.track_id)
    mastery = diagnosis.estimated_mastery
    priority_set = set(diagnosis.starting_priorities)
    nodes: list[UserSkillNode] = []

    for catalog_node in catalog.get("nodes", []):
        node_id = catalog_node["id"]
        score = int(mastery.get(node_id, 0))
        status = _mastery_to_status(score)
        if node_id in priority_set and status != SkillStatus.APROVADO:
            status = SkillStatus.RECOMENDADO
        nodes.append(
            UserSkillNode(
                node_id=node_id,
                title=catalog_node.get("title"),
                status=status,
                mastery_score=score,
                priority=_mastery_to_priority(score, node_id in priority_set),
                rationale=(
                    "Próximo nó da cadeia crítica"
                    if node_id in priority_set
                    else None
                ),
            ),
        )

    return nodes


def build_forge_timeline(
    diagnosis: DiagnosisResponse,
    *,
    research_artifacts: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    """Ordered forge SSE payloads for the four pipeline steps."""
    return [
        *build_forge_intro_events(diagnosis),
        *(research_artifacts or []),
        *build_forge_tail_events(diagnosis),
    ]


def build_forge_intro_events(diagnosis: DiagnosisResponse) -> list[dict[str, Any]]:
    """Events up to the start of research_enrich."""
    persona = diagnosis.profile.persona_slug or "perfil"
    track = diagnosis.profile.track_id
    top_strength = diagnosis.strengths[0] if diagnosis.strengths else "motivação clara"
    top_gap = diagnosis.gaps[0] if diagnosis.gaps else "lacunas em backend"
    graph = build_accumulated_graph(diagnosis)

    events: list[dict[str, Any]] = [
        {
            "type": "reasoning_delta",
            "text": f"Carregando catálogo `{track}` e cruzando com {persona}…",
            "step": "load_topics",
        },
        {
            "type": "step_complete",
            "step": "load_topics",
            "iteration": 0,
        },
        {
            "type": "reasoning_delta",
            "text": f"Priorizando lacunas: {top_gap[:80]}…",
            "step": "analyze_gaps",
        },
        {
            "type": "artifact_found",
            "label": f"Sinal forte: {top_strength[:48]}",
            "detail": "evidência do diagnóstico editável · pré-validado",
        },
    ]

    for node in graph:
        if node.status == SkillStatus.APROVADO:
            events.append(
                {
                    "type": "node_updated",
                    "node": {
                        "node_id": node.node_id,
                        "title": node.title,
                        "status": node.status.value,
                        "mastery_score": node.mastery_score,
                        "priority": node.priority.value if node.priority else None,
                    },
                },
            )

    events.append(
        {
            "type": "reasoning_delta",
            "text": "Pesquisando fontes oficiais para enriquecer missões e referências…",
            "step": "research_enrich",
        },
    )
    return events


def build_forge_tail_events(
    diagnosis: DiagnosisResponse,
    *,
    graph: list[UserSkillNode] | None = None,
) -> list[dict[str, Any]]:
    """Events after research is complete."""
    resolved_graph = graph or build_accumulated_graph(diagnosis)
    return [
        {
            "type": "step_complete",
            "step": "research_enrich",
            "iteration": 1,
        },
        {
            "type": "reasoning_delta",
            "text": "Consolidando grafo acumulado com pré-requisitos e prioridades…",
            "step": "accumulate_graph",
        },
        {
            "type": "step_complete",
            "step": "accumulate_graph",
            "iteration": 2,
        },
        {
            "type": "graph_ready",
            "graph": [n.model_dump() for n in resolved_graph],
        },
    ]


def build_research_prompts(context: LearnerForgeContext) -> list[str]:
    """Focused prompts for a visible multi-step native search loop."""
    summary = context.compact_summary()
    return [
        build_research_prompt(
            context,
            focus="roteiro oficial e pré-requisitos",
            instruction=(
                "Encontre fontes oficiais para estruturar a jornada do objetivo do aluno. "
                "Priorize roadmap.sh, docs oficiais de linguagem/framework e fundamentos."
            ),
            summary=summary,
        ),
        build_research_prompt(
            context,
            focus="projetos hands-on e evidência prática",
            instruction=(
                "Encontre fontes oficiais ou exemplos canônicos que ajudem o aluno a sair "
                "de zero prática para projetos demonstráveis."
            ),
            summary=summary,
        ),
        build_research_prompt(
            context,
            focus="APIs e produto real com IA",
            instruction=(
                "Encontre documentação oficial para construir APIs/produtos com IA, "
                "incluindo OpenAI API quando fizer sentido."
            ),
            summary=summary,
        ),
    ][:MAX_RESEARCH_ITERATIONS]


def build_research_prompt(
    context: LearnerForgeContext,
    *,
    focus: str,
    instruction: str,
    summary: str,
) -> str:
    return (
        "Use web_search obrigatoriamente. Faça uma busca focada, cite as fontes e "
        "responda em português com no máximo 2 frases úteis para a UI.\n\n"
        f"Foco desta busca: {focus}\n"
        f"Instrução: {instruction}\n\n"
        f"Contexto do aluno:\n{summary}\n"
    )


async def research_enrichment_events(
    diagnosis: DiagnosisResponse,
    input_data: dict[str, Any],
    search_client: WebSearchClient,
) -> list[dict[str, Any]]:
    context = build_forge_context_from_input(user_id="forge-user", input_data=input_data)
    return [
        event
        async for event in iter_research_enrichment_events(context, search_client)
    ]


async def iter_research_enrichment_events(
    context: LearnerForgeContext,
    search_client: WebSearchClient,
) -> AsyncIterator[dict[str, Any]]:
    for index, prompt in enumerate(build_research_prompts(context), start=1):
        result = await search_client.search(prompt)
        yield _research_artifact(result, iteration=index)


def _research_artifact(result: WebSearchResult, *, iteration: int = 1) -> dict[str, Any]:
    del iteration
    return {
        "type": "artifact_found",
        "label": "Pesquisando fontes oficiais...",
        "detail": _clean_research_summary(result.summary)
        or f"{len(result.sources)} fontes encontradas",
        "sources": [
            {"title": source.title, "url": source.url, "snippet": source.snippet}
            for source in result.sources
        ],
    }


def _clean_research_summary(summary: str) -> str:
    """Keep model markdown but remove inline citation links duplicated in source cards."""
    without_parenthetical_links = re.sub(
        r"\s*\(\[[^\]]+\]\([^)]+\)\)",
        "",
        summary,
    )
    without_inline_links = re.sub(
        r"\[([^\]]+)\]\([^)]+\)",
        r"\1",
        without_parenthetical_links,
    )
    without_bare_urls = re.sub(r"https?://\S+", "", without_inline_links)
    return without_bare_urls.strip()


async def _sleep_between_events() -> None:
    delay = float(os.getenv("FORGE_STREAM_DELAY_SEC", str(DEFAULT_STREAM_DELAY_SEC)))
    if delay > 0:
        await asyncio.sleep(delay)


def _planner_artifact(iteration: int) -> dict[str, Any]:
    return {
        "type": "artifact_found",
        "label": f"Planner do roadmap: versão {iteration}",
        "detail": "Plano de estudo estruturado com contexto, fontes e tarefas práticas.",
    }


class RoadmapForgeGraphRunnable:
    """GraphRunnable — load_topics → analyze_gaps → research_enrich → accumulate_graph."""

    graph_name = "roadmap_forge"

    def __init__(
        self,
        search_client: WebSearchClient | None = None,
        planner: StudyPlanPlanner | None = None,
        evaluator: StudyPlanEvaluator | None = None,
    ) -> None:
        self._search_client = search_client
        self._planner = planner
        self._evaluator = evaluator

    async def astream_events(
        self,
        input_data: dict[str, Any],
        *,
        version: str = "v2",
    ) -> AsyncIterator[LangChainStreamEvent]:
        del version
        raw_diagnosis = input_data.get("diagnosis") or input_data
        diagnosis = DiagnosisResponse.model_validate(raw_diagnosis)
        context = build_forge_context_from_input(user_id="forge-user", input_data=input_data)
        run_id = new_run_id()

        yield emit_chain_start(self.graph_name, run_id)

        for payload in build_forge_intro_events(diagnosis):
            await _sleep_between_events()
            yield emit_chain_stream(
                payload.get("step", "emit_forge_event"),
                run_id,
                {"forge_event": payload},
            )

        search_client = self._search_client or build_openai_web_search_client_from_env()
        research_events: list[dict[str, Any]] = []
        async for payload in iter_research_enrichment_events(context, search_client):
            research_events.append(payload)
            await _sleep_between_events()
            yield emit_chain_stream(
                payload.get("step", "emit_forge_event"),
                run_id,
                {"forge_event": payload},
            )

        planner = self._planner or build_study_plan_planner_from_env()
        evaluator = self._evaluator or build_study_plan_evaluator_from_env()
        graph = build_accumulated_graph(diagnosis)
        plan = build_draft_study_plan(
            context=context,
            diagnosis=diagnosis,
            graph=graph,
            research_events=research_events,
        )

        for iteration in range(1, MAX_EVALUATION_ITERATIONS + 1):
            if iteration == 1:
                plan = await planner.create_plan(
                    context=context,
                    research_events=research_events,
                )
            yield emit_chain_stream(
                "plan_study_graph",
                run_id,
                {"forge_event": _planner_artifact(iteration)},
            )

            evaluation = await evaluator.evaluate(plan)
            yield emit_chain_stream(
                "evaluate_plan",
                run_id,
                {"forge_event": evaluation_artifact(evaluation)},
            )
            if evaluation.verdict == "ship":
                break
            if iteration < MAX_EVALUATION_ITERATIONS:
                yield emit_chain_stream(
                    "revise_plan",
                    run_id,
                    {
                        "forge_event": {
                            "type": "reasoning_delta",
                            "step": "revise_plan",
                            "text": "Aplicando feedback do avaliador ao plano de estudos…",
                        },
                    },
                )
                plan = await planner.revise_plan(
                    context=context,
                    research_events=research_events,
                    plan=plan,
                    evaluation=evaluation,
                )

        final_graph = study_plan_to_graph(plan)
        tail_events = build_forge_tail_events(diagnosis, graph=final_graph)
        for payload in tail_events:
            await _sleep_between_events()
            yield emit_chain_stream(
                payload.get("step", "emit_forge_event"),
                run_id,
                {"forge_event": payload},
            )

        output = tail_events[-1]
        yield emit_chain_end(
            self.graph_name,
            run_id,
            output=output,
            input_data=input_data,
        )


def build_roadmap_forge_graph() -> RoadmapForgeGraphRunnable:
    """Return configured roadmap forge graph runnable."""
    return RoadmapForgeGraphRunnable()
