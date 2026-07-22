"""GraphRun entity and persistence protocol."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, Literal, Protocol, TypeVar, runtime_checkable
from uuid import uuid4

from pydantic import BaseModel, Field

GraphRunStatus = Literal["pending", "running", "completed", "failed"]

ModelT = TypeVar("ModelT", bound=BaseModel)


def unwrap_graph_output(output: dict[str, Any] | None, schema: type[ModelT]) -> ModelT:
    """Validate a GraphExecutor output into a Pydantic schema.

    Accepts both the wrapped ``graph_complete`` envelope and a raw output dict.
    """
    if output is None:
        msg = f"Graph completed without output (expected {schema.__name__})"
        raise ValueError(msg)
    if output.get("type") == "graph_complete" and isinstance(output.get("output"), dict):
        return schema.model_validate(output["output"])
    return schema.model_validate(output)


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
    billable: bool = True
    exclude_reason: str | None = None
    estimated_cost_brl: float | None = None
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


# Module-level default for API layer (lazy-init for prod Postgres).
_default_store: GraphRunStore | None = None


def _build_graph_run_store() -> GraphRunStore:
    from career_forge.db.stores.postgres_graph_run import PostgresGraphRunStore
    from career_forge.persistence.store_mode import resolve_persistence_backend

    backend = resolve_persistence_backend(None, env_var="GRAPH_RUN_STORE")
    if backend == "postgres":
        return PostgresGraphRunStore()
    return InMemoryGraphRunStore()


def get_graph_run_store() -> GraphRunStore:
    global _default_store
    if _default_store is None:
        _default_store = _build_graph_run_store()
    return _default_store


def set_graph_run_store(store: GraphRunStore | None) -> None:
    global _default_store
    _default_store = store
