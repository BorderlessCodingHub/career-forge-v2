"""Diagnosis LangGraph — HAC-8 implementation target."""

from __future__ import annotations

from career_forge.ai.graphs.base import MockGraphRunnable


def build_diagnosis_graph() -> MockGraphRunnable:
    """Return configured diagnosis graph runnable (mock until HAC-8)."""
    return MockGraphRunnable(
        "diagnosis",
        end_output={
            "type": "graph_complete",
            "graph_name": "diagnosis",
            "status": "pending_implementation",
        },
    )
