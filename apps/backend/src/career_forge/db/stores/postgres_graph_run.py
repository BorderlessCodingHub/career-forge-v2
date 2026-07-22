"""Postgres-backed GraphRun store (HAC-58)."""

from __future__ import annotations

from uuid import UUID

from career_forge.ai.run import GraphRun
from career_forge.db.models.graph_run import GraphRunRecord
from career_forge.db.session import SessionLocal


def graph_run_to_record_fields(run: GraphRun) -> dict:
    return {
        "graph_name": run.graph_name,
        "user_id": run.user_id,
        "status": run.status,
        "input": run.input,
        "output": run.output,
        "raw_events": run.raw_events,
        "normalized_events": run.normalized_events,
        "error": run.error,
        "billable": run.billable,
        "exclude_reason": run.exclude_reason,
        "estimated_cost_brl": run.estimated_cost_brl,
        "created_at": run.created_at,
        "updated_at": run.updated_at,
        "completed_at": run.completed_at,
    }


def record_to_graph_run(record: GraphRunRecord) -> GraphRun:
    return GraphRun(
        id=str(record.id),
        graph_name=record.graph_name,
        user_id=record.user_id,
        status=record.status,  # type: ignore[arg-type]
        input=record.input,
        output=record.output,
        raw_events=record.raw_events,
        normalized_events=record.normalized_events,
        error=record.error,
        billable=record.billable,
        exclude_reason=record.exclude_reason,
        estimated_cost_brl=record.estimated_cost_brl,
        created_at=record.created_at,
        updated_at=record.updated_at,
        completed_at=record.completed_at,
    )


class PostgresGraphRunStore:
    """Persist GraphRun rows in ``graph_runs``."""

    def save(self, run: GraphRun) -> None:
        db = SessionLocal()
        try:
            run_id = UUID(run.id)
            existing = db.get(GraphRunRecord, run_id)
            payload = graph_run_to_record_fields(run)
            if existing is None:
                db.add(GraphRunRecord(id=run_id, **payload))
            else:
                for key, value in payload.items():
                    setattr(existing, key, value)
            db.commit()
        finally:
            db.close()

    def get(self, run_id: str) -> GraphRun | None:
        db = SessionLocal()
        try:
            record = db.get(GraphRunRecord, UUID(run_id))
            if record is None:
                return None
            return record_to_graph_run(record)
        finally:
            db.close()
