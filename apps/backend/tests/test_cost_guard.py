"""Unit tests — CostGuard pool + per-user forge cap (CAR-6)."""

from __future__ import annotations

from datetime import UTC, datetime

import pytest
from fastapi.testclient import TestClient

from career_forge.ai.executor import GraphExecutor
from career_forge.ai.factory import AgentFactory
from career_forge.ai.graphs.base import MockGraphRunnable
from career_forge.ai.graphs.diagnosis import build_diagnosis_response
from career_forge.ai.run import GraphRun, InMemoryGraphRunStore
from career_forge.config import Settings
from career_forge.db.models.usage_monthly import GLOBAL_USAGE_USER_ID
from career_forge.demo.ana_state import DEMO_ANA_EXTERNAL_ID
from career_forge.errors import QUOTA_EXHAUSTED_MESSAGE, QuotaExhaustedError
from career_forge.schemas.diagnosis import DiagnosisRequest
from career_forge.services.cost_guard import (
    EXCLUDE_DEMO,
    EXCLUDE_SYNTHETIC_GATE,
    CostGuard,
    InMemoryUsageStore,
    current_year_month,
    unit_cost_brl,
)


def _settings(**overrides: float | int) -> Settings:
    base = Settings(
        monthly_api_budget_brl=500.0,
        forge_cap_per_user_month=2,
        cost_p95_brl_per_run=1.0,
        cost_buffer_factor=1.10,
    )
    return base.model_copy(update=overrides)


@pytest.fixture
def usage_store() -> InMemoryUsageStore:
    return InMemoryUsageStore()


@pytest.fixture
def guard(usage_store: InMemoryUsageStore) -> CostGuard:
    return CostGuard(store=usage_store, cfg=_settings())


def _completed_run(
    *,
    user_id: str = "student-1",
    graph_name: str = "validation",
    run_input: dict | None = None,
) -> GraphRun:
    now = datetime.now(UTC)
    return GraphRun(
        graph_name=graph_name,
        user_id=user_id,
        status="completed",
        input=run_input or {},
        completed_at=now,
    )


def test_unit_cost_includes_buffer() -> None:
    assert unit_cost_brl(_settings()) == pytest.approx(1.1)


def test_demo_ana_excluded_from_pool(guard: CostGuard, usage_store: InMemoryUsageStore) -> None:
    run = _completed_run(user_id=DEMO_ANA_EXTERNAL_ID, graph_name="roadmap_forge")
    guard.check(run)
    guard.record(run)

    assert run.billable is False
    assert run.exclude_reason == EXCLUDE_DEMO
    ym = current_year_month()
    assert usage_store.get(ym, GLOBAL_USAGE_USER_ID).billable_runs == 0
    assert usage_store.get(ym, DEMO_ANA_EXTERNAL_ID).billable_runs == 0


def test_synthetic_gate_excluded(guard: CostGuard, usage_store: InMemoryUsageStore) -> None:
    run = _completed_run(
        user_id="gate-runner",
        graph_name="roadmap_forge",
        run_input={"_cost": {"synthetic_gate": True}},
    )
    guard.check(run)
    guard.record(run)

    assert run.billable is False
    assert run.exclude_reason == EXCLUDE_SYNTHETIC_GATE
    ym = current_year_month()
    assert usage_store.get(ym, GLOBAL_USAGE_USER_ID).billable_runs == 0


def test_billable_run_increments_counters(
    guard: CostGuard, usage_store: InMemoryUsageStore
) -> None:
    run = _completed_run(graph_name="mentor")
    guard.record(run)

    ym = current_year_month()
    user = usage_store.get(ym, "student-1")
    global_row = usage_store.get(ym, GLOBAL_USAGE_USER_ID)
    cost = unit_cost_brl(_settings())

    assert run.billable is True
    assert run.estimated_cost_brl == pytest.approx(cost)
    assert user.billable_runs == 1
    assert user.forge_runs == 0
    assert user.estimated_cost_brl == pytest.approx(cost)
    assert global_row.billable_runs == 1
    assert global_row.estimated_cost_brl == pytest.approx(cost)


def test_forge_increments_forge_runs(guard: CostGuard, usage_store: InMemoryUsageStore) -> None:
    run = _completed_run(graph_name="roadmap_forge")
    guard.record(run)

    ym = current_year_month()
    assert usage_store.get(ym, "student-1").forge_runs == 1
    assert usage_store.get(ym, GLOBAL_USAGE_USER_ID).forge_runs == 1


def test_global_pool_blocks_when_budget_reached(
    guard: CostGuard, usage_store: InMemoryUsageStore
) -> None:
    ym = current_year_month()
    usage_store.increment(
        ym,
        GLOBAL_USAGE_USER_ID,
        estimated_cost_brl=500.0,
    )
    run = GraphRun(graph_name="validation", user_id="student-2", input={})
    with pytest.raises(QuotaExhaustedError) as exc_info:
        guard.check(run)
    assert exc_info.value.code == "global_pool"
    assert str(exc_info.value) == QUOTA_EXHAUSTED_MESSAGE


def test_per_user_forge_cap_enforced(
    guard: CostGuard, usage_store: InMemoryUsageStore
) -> None:
    ym = current_year_month()
    usage_store.increment(ym, "student-1", forge_runs=2)
    forge = GraphRun(graph_name="roadmap_forge", user_id="student-1", input={})
    with pytest.raises(QuotaExhaustedError) as exc_info:
        guard.check(forge)
    assert exc_info.value.code == "per_user_cap"

    # Non-forge graphs still allowed under forge cap.
    other = GraphRun(graph_name="mentor", user_id="student-1", input={})
    guard.check(other)


@pytest.mark.asyncio
async def test_executor_blocks_before_run(usage_store: InMemoryUsageStore) -> None:
    guard = CostGuard(store=usage_store, cfg=_settings(monthly_api_budget_brl=0.0))
    factory = AgentFactory()
    factory.register("validation", lambda: MockGraphRunnable("validation"))
    executor = GraphExecutor(
        factory=factory,
        store=InMemoryGraphRunStore(),
        cost_guard=guard,
    )
    run = GraphRun(graph_name="validation", user_id="student-x", input={})
    with pytest.raises(QuotaExhaustedError):
        await executor.execute(run, stream=False)


def test_quota_exhausted_http_shape(client: TestClient) -> None:
    from career_forge.services import cost_guard as cost_guard_mod

    store = InMemoryUsageStore()
    store.increment(
        current_year_month(),
        GLOBAL_USAGE_USER_ID,
        estimated_cost_brl=500.0,
    )
    cost_guard_mod.set_cost_guard(CostGuard(store=store, cfg=_settings()))

    diagnosis = build_diagnosis_response(
        DiagnosisRequest(
            goal_id="rag-engineer",
            motivation="I want to ship grounded RAG systems in production.",
            answers={"level": "beginner"},
        ),
    )

    response = client.post(
        "/forge",
        json={
            "user_id": "student-blocked",
            "diagnosis": diagnosis.model_dump(mode="json"),
        },
    )
    assert response.status_code == 429
    body = response.json()
    assert body["detail"]["code"] == "global_pool"
    assert body["detail"]["message"] == QUOTA_EXHAUSTED_MESSAGE
