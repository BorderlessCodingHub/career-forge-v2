"""Unit tests — AgentFactory register/get pattern."""

from __future__ import annotations

import pytest

from career_forge.ai.factory import AgentFactory
from career_forge.ai.agents.mentor import MentorAgentRunnable
from career_forge.ai.graphs.base import GraphRunnable, MockGraphRunnable
from career_forge.ai.graphs.roadmap_forge import RoadmapForgeGraphRunnable


def test_factory_returns_registered_names() -> None:
    factory = AgentFactory()
    assert factory.names() == ["diagnosis", "mentor", "roadmap_forge", "validation"]


def test_factory_get_returns_runnable() -> None:
    factory = AgentFactory()
    runnable = factory.get("roadmap_forge")
    assert isinstance(runnable, RoadmapForgeGraphRunnable)
    assert runnable.graph_name == "roadmap_forge"


def test_factory_get_mentor_returns_runnable() -> None:
    factory = AgentFactory()
    runnable = factory.get("mentor")
    assert isinstance(runnable, MentorAgentRunnable)
    assert runnable.graph_name == "mentor"


def test_factory_get_unknown_raises() -> None:
    factory = AgentFactory()
    with pytest.raises(KeyError, match="Unknown graph/agent"):
        factory.get("nonexistent")


def test_factory_register_custom_builder() -> None:
    factory = AgentFactory()

    def build_custom() -> GraphRunnable:
        return MockGraphRunnable("custom")

    factory.register("custom", build_custom)
    assert factory.get("custom").graph_name == "custom"
