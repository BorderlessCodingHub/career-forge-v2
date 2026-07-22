"""Cost guard — monthly pool + per-user forge cap (CAR-6).

Runtime proxy: ``runs × COST_P95_BRL_PER_RUN × COST_BUFFER_FACTOR``.
Excluded from the student pool: ``demo-ana`` and runs with
``input["_cost"]["synthetic_gate"] = true`` (CAR-7 gate synthetics).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from threading import Lock
from typing import Protocol

from career_forge.ai.run import GraphRun
from career_forge.config import Settings, settings
from career_forge.db.models.usage_monthly import GLOBAL_USAGE_USER_ID, UsageMonthly
from career_forge.db.session import SessionLocal
from career_forge.demo.ana_state import DEMO_ANA_EXTERNAL_ID
from career_forge.errors import QuotaExhaustedError
from career_forge.persistence.store_mode import resolve_persistence_backend

FORGE_GRAPH_NAME = "roadmap_forge"
EXCLUDE_DEMO = "demo"
EXCLUDE_SYNTHETIC_GATE = "synthetic_gate"


def current_year_month(now: datetime | None = None) -> str:
    stamp = now or datetime.now(UTC)
    return stamp.strftime("%Y-%m")


def unit_cost_brl(cfg: Settings | None = None) -> float:
    s = cfg or settings
    return s.cost_p95_brl_per_run * s.cost_buffer_factor


def resolve_exclude_reason(user_id: str, run_input: dict | None) -> str | None:
    if user_id == DEMO_ANA_EXTERNAL_ID:
        return EXCLUDE_DEMO
    cost_meta = (run_input or {}).get("_cost")
    if isinstance(cost_meta, dict) and cost_meta.get("synthetic_gate") is True:
        return EXCLUDE_SYNTHETIC_GATE
    return None


@dataclass
class UsageSnapshot:
    billable_runs: int = 0
    forge_runs: int = 0
    estimated_cost_brl: float = 0.0


class UsageStore(Protocol):
    def get(self, year_month: str, user_id: str) -> UsageSnapshot: ...

    def increment(
        self,
        year_month: str,
        user_id: str,
        *,
        billable_runs: int = 0,
        forge_runs: int = 0,
        estimated_cost_brl: float = 0.0,
    ) -> None: ...


@dataclass
class InMemoryUsageStore:
    """Process-local counters for tests / GRAPH_RUN_STORE=memory."""

    _rows: dict[tuple[str, str], UsageSnapshot] = field(default_factory=dict)
    _lock: Lock = field(default_factory=Lock)

    def get(self, year_month: str, user_id: str) -> UsageSnapshot:
        with self._lock:
            row = self._rows.get((year_month, user_id))
            if row is None:
                return UsageSnapshot()
            return UsageSnapshot(
                billable_runs=row.billable_runs,
                forge_runs=row.forge_runs,
                estimated_cost_brl=row.estimated_cost_brl,
            )

    def increment(
        self,
        year_month: str,
        user_id: str,
        *,
        billable_runs: int = 0,
        forge_runs: int = 0,
        estimated_cost_brl: float = 0.0,
    ) -> None:
        with self._lock:
            row = self._rows.get((year_month, user_id))
            if row is None:
                row = UsageSnapshot()
                self._rows[(year_month, user_id)] = row
            row.billable_runs += billable_runs
            row.forge_runs += forge_runs
            row.estimated_cost_brl += estimated_cost_brl


class PostgresUsageStore:
    """Persist monthly aggregates in ``usage_monthly``."""

    def get(self, year_month: str, user_id: str) -> UsageSnapshot:
        db = SessionLocal()
        try:
            row = db.get(UsageMonthly, {"year_month": year_month, "user_id": user_id})
            if row is None:
                return UsageSnapshot()
            return UsageSnapshot(
                billable_runs=row.billable_runs,
                forge_runs=row.forge_runs,
                estimated_cost_brl=float(row.estimated_cost_brl),
            )
        finally:
            db.close()

    def increment(
        self,
        year_month: str,
        user_id: str,
        *,
        billable_runs: int = 0,
        forge_runs: int = 0,
        estimated_cost_brl: float = 0.0,
    ) -> None:
        db = SessionLocal()
        try:
            row = db.get(UsageMonthly, {"year_month": year_month, "user_id": user_id})
            if row is None:
                row = UsageMonthly(
                    year_month=year_month,
                    user_id=user_id,
                    billable_runs=0,
                    forge_runs=0,
                    estimated_cost_brl=0.0,
                )
                db.add(row)
            row.billable_runs += billable_runs
            row.forge_runs += forge_runs
            row.estimated_cost_brl = float(row.estimated_cost_brl) + estimated_cost_brl
            db.commit()
        finally:
            db.close()


class CostGuard:
    """Pre-run gate + post-run counters for billable GraphRuns."""

    def __init__(
        self,
        store: UsageStore | None = None,
        cfg: Settings | None = None,
    ) -> None:
        self._store = store or _build_usage_store()
        self._cfg = cfg or settings

    def is_excluded(self, user_id: str, run_input: dict | None = None) -> bool:
        return resolve_exclude_reason(user_id, run_input) is not None

    def check(self, run: GraphRun) -> None:
        """Raise ``QuotaExhaustedError`` when pool or forge cap is exhausted."""
        if self.is_excluded(run.user_id, run.input):
            return

        year_month = current_year_month()
        global_usage = self._store.get(year_month, GLOBAL_USAGE_USER_ID)
        if global_usage.estimated_cost_brl >= self._cfg.monthly_api_budget_brl:
            raise QuotaExhaustedError("global_pool")

        if run.graph_name == FORGE_GRAPH_NAME:
            user_usage = self._store.get(year_month, run.user_id)
            if user_usage.forge_runs >= self._cfg.forge_cap_per_user_month:
                raise QuotaExhaustedError("per_user_cap")

    def record(self, run: GraphRun) -> None:
        """Annotate run + increment monthly counters for completed billable runs."""
        if run.status != "completed":
            return

        exclude = resolve_exclude_reason(run.user_id, run.input)
        cost = unit_cost_brl(self._cfg)
        if exclude is not None:
            run.billable = False
            run.exclude_reason = exclude
            run.estimated_cost_brl = cost
            return

        run.billable = True
        run.exclude_reason = None
        run.estimated_cost_brl = cost

        year_month = current_year_month(run.completed_at or datetime.now(UTC))
        is_forge = 1 if run.graph_name == FORGE_GRAPH_NAME else 0
        self._store.increment(
            year_month,
            run.user_id,
            billable_runs=1,
            forge_runs=is_forge,
            estimated_cost_brl=cost,
        )
        self._store.increment(
            year_month,
            GLOBAL_USAGE_USER_ID,
            billable_runs=1,
            forge_runs=is_forge,
            estimated_cost_brl=cost,
        )


def _build_usage_store() -> UsageStore:
    # Align with GraphRun persistence: memory backend → in-memory counters.
    backend = resolve_persistence_backend(None, env_var="GRAPH_RUN_STORE")
    if backend == "postgres":
        return PostgresUsageStore()
    return InMemoryUsageStore()


_default_guard: CostGuard | None = None


def get_cost_guard() -> CostGuard:
    global _default_guard
    if _default_guard is None:
        _default_guard = CostGuard()
    return _default_guard


def set_cost_guard(guard: CostGuard | None) -> None:
    global _default_guard
    _default_guard = guard
