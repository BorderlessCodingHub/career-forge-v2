"""Roadmap forge graph — multi-step forge pipeline (HAC-18)."""

from __future__ import annotations

import asyncio
import json
from collections.abc import AsyncIterator
from typing import Any
from uuid import uuid4

from career_forge.paths import roadmap_json_path
from career_forge.schemas.common import Priority, SkillStatus, UserSkillNode
from career_forge.schemas.diagnosis import DiagnosisResponse

ROADMAP_PATH = roadmap_json_path()

STREAM_DELAY_SEC = 0.12

FORGE_STEPS = (
    "load_topics",
    "analyze_gaps",
    "research_enrich",
    "accumulate_graph",
)


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


def _load_catalog() -> dict[str, Any]:
    with ROADMAP_PATH.open(encoding="utf-8") as handle:
        return json.load(handle)


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
    catalog = _load_catalog()
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


def build_forge_timeline(diagnosis: DiagnosisResponse) -> list[dict[str, Any]]:
    """Ordered forge SSE payloads for the four pipeline steps."""
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

    events.extend(
        [
            {
                "type": "reasoning_delta",
                "text": "Pesquisando tendências 2026 em APIs e space tech para enriquecer missões…",
                "step": "research_enrich",
            },
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
                "graph": [n.model_dump() for n in graph],
            },
        ],
    )
    return events


class RoadmapForgeGraphRunnable:
    """GraphRunnable — load_topics → analyze_gaps → research_enrich → accumulate_graph."""

    graph_name = "roadmap_forge"

    async def astream_events(
        self,
        input_data: dict[str, Any],
        *,
        version: str = "v2",
    ) -> AsyncIterator[dict[str, Any]]:
        del version
        raw_diagnosis = input_data.get("diagnosis") or input_data
        diagnosis = DiagnosisResponse.model_validate(raw_diagnosis)
        timeline = build_forge_timeline(diagnosis)
        run_id = str(uuid4())

        yield _lc_event("on_chain_start", self.graph_name, run_id, {})

        for payload in timeline:
            await asyncio.sleep(STREAM_DELAY_SEC)
            yield _lc_event(
                "on_chain_stream",
                payload.get("step", "emit_forge_event"),
                run_id,
                {"chunk": {"forge_event": payload}},
            )

        yield _lc_event(
            "on_chain_end",
            self.graph_name,
            run_id,
            {"output": timeline[-1], "input": input_data},
        )


def build_roadmap_forge_graph() -> RoadmapForgeGraphRunnable:
    """Return configured roadmap forge graph runnable."""
    return RoadmapForgeGraphRunnable()
