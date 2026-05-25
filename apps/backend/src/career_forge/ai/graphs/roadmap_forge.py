"""Roadmap forge LangGraph — HAC-18 implementation target."""

from __future__ import annotations

from career_forge.ai.graphs.base import MockGraphRunnable


def build_roadmap_forge_graph() -> MockGraphRunnable:
    """Return configured roadmap forge graph runnable (mock streams fixture)."""
    return MockGraphRunnable(
        "roadmap_forge",
        stream_fixture="roadmap_forge_events.json",
    )
