"""Persist Forge output into the user's roadmap state."""

from __future__ import annotations

from typing import Any

from career_forge.db.session import SessionLocal
from career_forge.schemas.common import UserSkillNode
from career_forge.services.roadmap import sync_user_graph


def persist_graph_ready(user_id: str, graph_ready_event: dict[str, Any] | None) -> None:
    """Persist graph_ready nodes for reload after the Forge stream completes."""
    if not graph_ready_event or graph_ready_event.get("type") != "graph_ready":
        return
    raw_nodes = graph_ready_event.get("graph")
    if not isinstance(raw_nodes, list) or not raw_nodes:
        return

    nodes = [UserSkillNode.model_validate(node) for node in raw_nodes]
    with SessionLocal() as session:
        sync_user_graph(session, user_id, nodes)
