"""Tests for persistence store mode resolution and GraphRun mapping (HAC-58)."""

from __future__ import annotations

from datetime import UTC, datetime

import pytest

from uuid import UUID

from career_forge.ai.run import GraphRun, InMemoryGraphRunStore, get_graph_run_store, set_graph_run_store
from career_forge.db.stores.postgres_graph_run import (
    PostgresGraphRunStore,
    graph_run_to_record_fields,
    record_to_graph_run,
)
from career_forge.db.models.graph_run import GraphRunRecord
from career_forge.persistence.store_mode import resolve_persistence_backend


def test_resolve_persistence_backend_memory() -> None:
    assert resolve_persistence_backend("memory", env_var="GRAPH_RUN_STORE") == "memory"


def test_resolve_persistence_backend_postgres_explicit() -> None:
    assert resolve_persistence_backend("postgres", env_var="GRAPH_RUN_STORE") == "postgres"


def test_resolve_persistence_backend_auto_production(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ENV", "production")
    assert resolve_persistence_backend("auto", env_var="GRAPH_RUN_STORE") == "postgres"


def test_resolve_persistence_backend_auto_local(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ENV", "local")
    assert resolve_persistence_backend("auto", env_var="GRAPH_RUN_STORE") == "memory"


def test_graph_run_record_roundtrip_fields() -> None:
    run = GraphRun(
        id="550e8400-e29b-41d4-a716-446655440000",
        graph_name="roadmap_forge",
        user_id="user-1",
        status="completed",
        input={"diagnosis": {"profile": {"label": "Backend"}}},
        output={"graph": []},
        raw_events=[{"event": "on_chain_start"}],
        normalized_events=[{"type": "step_complete"}],
        error=None,
        created_at=datetime(2026, 5, 26, tzinfo=UTC),
        updated_at=datetime(2026, 5, 26, 1, tzinfo=UTC),
        completed_at=datetime(2026, 5, 26, 2, tzinfo=UTC),
    )
    record = GraphRunRecord(
        id=UUID(run.id),
        **graph_run_to_record_fields(run),
    )
    restored = record_to_graph_run(record)
    assert restored.id == run.id
    assert restored.graph_name == "roadmap_forge"
    assert restored.status == "completed"
    assert restored.normalized_events[0]["type"] == "step_complete"


def test_get_graph_run_store_uses_memory_in_local(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ENV", "local")
    monkeypatch.setenv("GRAPH_RUN_STORE", "auto")
    set_graph_run_store(None)
    store = get_graph_run_store()
    assert isinstance(store, InMemoryGraphRunStore)


def test_get_graph_run_store_uses_postgres_in_production(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ENV", "production")
    monkeypatch.setenv("GRAPH_RUN_STORE", "auto")
    set_graph_run_store(None)
    store = get_graph_run_store()
    assert isinstance(store, PostgresGraphRunStore)
