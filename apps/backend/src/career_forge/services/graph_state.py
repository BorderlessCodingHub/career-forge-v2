"""Deterministic GraphPatch → accumulated graph merge."""

from __future__ import annotations

from career_forge.schemas.common import UserSkillNode
from career_forge.schemas.forge import GraphPatch, NodePatch


def apply_graph_patch(
    graph: list[UserSkillNode],
    patch: GraphPatch,
) -> list[UserSkillNode]:
    """Merge LLM patches into accumulated graph (deterministic, no LLM)."""
    by_id = {node.node_id: node.model_copy() for node in graph}
    for node_patch in patch.patches:
        existing = by_id.get(node_patch.node_id)
        if existing:
            existing.status = node_patch.status
            existing.mastery_score = node_patch.mastery_estimated
            existing.priority = node_patch.priority
            existing.rationale = node_patch.rationale or existing.rationale
        else:
            by_id[node_patch.node_id] = UserSkillNode(
                node_id=node_patch.node_id,
                status=node_patch.status,
                mastery_score=node_patch.mastery_estimated,
                priority=node_patch.priority,
                rationale=node_patch.rationale,
            )
    return list(by_id.values())
