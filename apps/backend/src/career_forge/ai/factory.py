"""AgentFactory — register and resolve runnables by schema attribute name."""

from __future__ import annotations

from collections.abc import Callable

from career_forge.ai.graphs.base import GraphRunnable
from career_forge.ai.registry import GRAPH_BUILDERS, GraphBuilder


class AgentFactory:
    """Single interface: ``factory.get('roadmap_forge')`` → configured runnable."""

    def __init__(self) -> None:
        self._builders: dict[str, GraphBuilder] = dict(GRAPH_BUILDERS)

    def register(self, name: str, builder: GraphBuilder) -> None:
        self._builders[name] = builder

    def get(self, name: str) -> GraphRunnable:
        try:
            builder = self._builders[name]
        except KeyError as exc:
            known = ", ".join(sorted(self._builders))
            msg = f"Unknown graph/agent {name!r}. Registered: {known}"
            raise KeyError(msg) from exc
        return builder()

    def names(self) -> list[str]:
        return sorted(self._builders)


_default_factory = AgentFactory()


def get_agent_factory() -> AgentFactory:
    return _default_factory
