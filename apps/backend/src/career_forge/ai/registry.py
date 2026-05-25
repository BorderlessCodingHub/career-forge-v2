"""Maps graph names → builder callables for AgentFactory."""

from __future__ import annotations

from collections.abc import Callable

from career_forge.ai.agents.mentor import build_mentor_agent
from career_forge.ai.graphs.base import GraphRunnable
from career_forge.ai.graphs.diagnosis import build_diagnosis_graph
from career_forge.ai.graphs.roadmap_forge import build_roadmap_forge_graph
from career_forge.ai.graphs.validation import build_validation_graph

GraphBuilder = Callable[[], GraphRunnable]

GRAPH_BUILDERS: dict[str, GraphBuilder] = {
    "diagnosis": build_diagnosis_graph,
    "roadmap_forge": build_roadmap_forge_graph,
    "validation": build_validation_graph,
    "mentor": build_mentor_agent,
}
