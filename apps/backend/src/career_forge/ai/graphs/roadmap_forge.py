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
from career_forge.services.lean_forge import (
    load_must_have_ids,
    resolve_lean_allowed_node_ids,
)
from career_forge.services.must_have_coverage import apply_must_have_inject
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


def build_accumulated_graph(
    diagnosis: DiagnosisResponse,
    *,
    allowed_node_ids: set[str] | None = None,
) -> list[UserSkillNode]:
    """Deterministic graph from catalog + diagnosis mastery scores.

    When ``allowed_node_ids`` is set (lean forge), only those catalog nodes
    are included.
    """
    catalog = _load_catalog(diagnosis.profile.track_id)
    mastery = diagnosis.estimated_mastery
    priority_set = set(diagnosis.starting_priorities)
    nodes: list[UserSkillNode] = []

    for catalog_node in catalog.get("nodes", []):
        node_id = catalog_node["id"]
        if allowed_node_ids is not None and node_id not in allowed_node_ids:
            continue
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
                    "Next node on the critical path"
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
    allowed_node_ids: set[str] | None = None,
) -> list[dict[str, Any]]:
    """Ordered forge SSE payloads for the four pipeline steps."""
    return [
        *build_forge_intro_events(diagnosis, allowed_node_ids=allowed_node_ids),
        *(research_artifacts or []),
        *build_forge_tail_events(
            diagnosis,
            graph=build_accumulated_graph(
                diagnosis,
                allowed_node_ids=allowed_node_ids,
            ),
        ),
    ]


def build_forge_intro_events(
    diagnosis: DiagnosisResponse,
    *,
    allowed_node_ids: set[str] | None = None,
) -> list[dict[str, Any]]:
    """Events up to the start of research_enrich."""
    persona = diagnosis.profile.persona_slug or "profile"
    track = diagnosis.profile.track_id
    top_strength = diagnosis.strengths[0] if diagnosis.strengths else "clear motivation"
    top_gap = diagnosis.gaps[0] if diagnosis.gaps else "backend gaps"
    graph = build_accumulated_graph(diagnosis, allowed_node_ids=allowed_node_ids)


    events: list[dict[str, Any]] = [
        {
            "type": "reasoning_delta",
            "text": f"Loading catalog `{track}` and matching with {persona}…",
            "step": "load_topics",
        },
        {
            "type": "step_complete",
            "step": "load_topics",
            "iteration": 0,
        },
        {
            "type": "reasoning_delta",
            "text": f"Prioritizing gaps: {top_gap[:80]}…",
            "step": "analyze_gaps",
        },
        {
            "type": "artifact_found",
            "label": f"Strong signal: {top_strength[:48]}",
            "detail": "evidence from editable diagnosis · pre-validated",
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
            "text": "Searching official sources to enrich missions and references…",
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
            "text": "Consolidating accumulated graph with prerequisites and priorities…",
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
            focus="official roadmap and prerequisites",
            instruction=(
                "Find official sources to structure the learner's goal journey. "
                "Prefer roadmap.sh, official language/framework docs, and fundamentals."
            ),
            summary=summary,
        ),
        build_research_prompt(
            context,
            focus="hands-on projects and practical evidence",
            instruction=(
                "Find official sources or canonical examples that help the learner go "
                "from zero practice to demonstrable projects."
            ),
            summary=summary,
        ),
        build_research_prompt(
            context,
            focus="APIs and real AI products",
            instruction=(
                "Find official documentation for building APIs/products with AI, "
                "including the OpenAI API when relevant."
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
        "You must use web_search. Run a focused search, cite sources, and "
        "reply in English with at most 2 useful sentences for the UI.\n\n"
        f"Search focus: {focus}\n"
        f"Instruction: {instruction}\n\n"
        f"Learner context:\n{summary}\n"
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
        "label": f"Roadmap planner: version {iteration}",
        "detail": "Structured study plan with context, sources, and practice tasks.",
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
        allowed_node_ids = resolve_lean_allowed_node_ids(input_data)
        run_id = new_run_id()

        yield emit_chain_start(self.graph_name, run_id)

        for payload in build_forge_intro_events(
            diagnosis,
            allowed_node_ids=allowed_node_ids,
        ):
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
        graph = build_accumulated_graph(diagnosis, allowed_node_ids=allowed_node_ids)
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
                            "text": "Applying evaluator feedback to the study plan…",
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
        if allowed_node_ids is not None:
            filtered = [n for n in final_graph if n.node_id in allowed_node_ids]
            final_graph = filtered or graph

        # CAR-17: measure pre-inject coverage, then inject missing must-haves (both paths).
        raw_must = input_data.get("must_have_node_ids")
        if isinstance(raw_must, list) and raw_must:
            must_ids = [str(node_id) for node_id in raw_must if node_id]
        else:
            must_ids = load_must_have_ids(context.goal_id)
        final_graph, _pre_coverage = apply_must_have_inject(
            final_graph,
            goal_id=context.goal_id,
            track_id=diagnosis.profile.track_id,
            must_have_ids=must_ids,
        )

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
