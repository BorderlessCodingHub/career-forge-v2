"""Validation LangGraph — HAC-10 implementation target."""

from __future__ import annotations

from career_forge.ai.graphs.base import MockGraphRunnable


def build_validation_graph() -> MockGraphRunnable:
    """Return configured validation graph runnable (mock until HAC-10)."""
    return MockGraphRunnable(
        "validation",
        end_output={
            "type": "graph_complete",
            "graph_name": "validation",
            "status": "pending_implementation",
        },
    )
