"""GraphRun entity and persistence protocol."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, Literal, Protocol, runtime_checkable
from uuid import uuid4

from pydantic import BaseModel, Field

GraphRunStatus = Literal["pending", "running", "completed", "failed"]


class GraphRun(BaseModel):
    """One execution of a registered graph/agent."""

    id: str = Field(default_factory=lambda: str(uuid4()))
    graph_name: str
    user_id: str
    status: GraphRunStatus = "pending"
    input: dict[str, Any] = Field(default_factory=dict)
    output: dict[str, Any] | None = None
    raw_events: list[dict[str, Any]] = Field(default_factory=list)
    normalized_events: list[dict[str, Any]] = Field(default_factory=list)
    error: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    completed_at: datetime | None = None


class GraphRunResult(BaseModel):
    """Collected result from a non-streaming GraphExecutor run."""

    run: GraphRun
    events: list[dict[str, Any]]


@runtime_checkable
class GraphRunStore(Protocol):
    """Persistence boundary for GraphRun records."""

    def save(self, run: GraphRun) -> None: ...

    def get(self, run_id: str) -> GraphRun | None: ...


class InMemoryGraphRunStore:
    """Process-local store for scaffold/tests. Phase 2: SQLAlchemy GraphRunRecord."""

    def __init__(self) -> None:
        self._runs: dict[str, GraphRun] = {}

    def save(self, run: GraphRun) -> None:
        run.updated_at = datetime.now(UTC)
        self._runs[run.id] = run.model_copy(deep=True)

    def get(self, run_id: str) -> GraphRun | None:
        stored = self._runs.get(run_id)
        return stored.model_copy(deep=True) if stored else None


# Module-level default for API layer (replaced by DI in production).
_default_store = InMemoryGraphRunStore()


def get_graph_run_store() -> GraphRunStore:
    return _default_store
