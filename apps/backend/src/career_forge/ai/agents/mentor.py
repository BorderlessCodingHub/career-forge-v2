"""Contextual mentor agent — HAC-13 (non-graph LLM calls)."""

from __future__ import annotations

from career_forge.ai.graphs.base import MockGraphRunnable


def build_mentor_agent() -> MockGraphRunnable:
    """Return mentor runnable registered under name ``mentor``."""
    return MockGraphRunnable(
        "mentor",
        end_output={
            "type": "graph_complete",
            "graph_name": "mentor",
            "status": "pending_implementation",
        },
    )
