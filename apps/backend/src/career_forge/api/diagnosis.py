"""Diagnosis HTTP routes — sync collect via GraphExecutor."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from career_forge.ai.executor import get_graph_executor
from career_forge.ai.run import GraphRun, GraphRunResult, get_graph_run_store
from career_forge.db.session import get_db
from career_forge.schemas.diagnosis import DiagnosisRequest, DiagnosisResponse
from career_forge.schemas.profile_diagnosis import (
    DiagnosisConfirmRequest,
    DiagnosisConfirmResponse,
)
from career_forge.services.profile_diagnosis import confirm_diagnosis

router = APIRouter()


class DiagnosisRunResponse(BaseModel):
    run_id: str
    status: str
    events: list[dict[str, Any]]
    diagnosis: DiagnosisResponse


def _extract_diagnosis(output: dict[str, Any] | None) -> DiagnosisResponse:
    if output is None:
        msg = "Diagnosis graph completed without output"
        raise ValueError(msg)

    if output.get("type") == "graph_complete" and isinstance(output.get("output"), dict):
        return DiagnosisResponse.model_validate(output["output"])

    return DiagnosisResponse.model_validate(output)


@router.post("", response_model=DiagnosisRunResponse)
async def create_diagnosis(body: DiagnosisRequest) -> DiagnosisRunResponse:
    """Run onboarding diagnosis — collect full result (no SSE to client)."""
    store = get_graph_run_store()
    run = GraphRun(
        graph_name="diagnosis",
        user_id=body.user_id,
        input=body.model_dump(),
    )
    store.save(run)

    executor = get_graph_executor()
    result = await executor.execute(run, stream=False)
    assert isinstance(result, GraphRunResult)

    diagnosis = _extract_diagnosis(result.run.output)

    return DiagnosisRunResponse(
        run_id=result.run.id,
        status=result.run.status,
        events=result.events,
        diagnosis=diagnosis,
    )


@router.post("/confirm", response_model=DiagnosisConfirmResponse)
def confirm_diagnosis_route(
    body: DiagnosisConfirmRequest,
    db: Session = Depends(get_db),
) -> DiagnosisConfirmResponse:
    """Persist confirmed diagnosis + intake context for forge motor."""
    return confirm_diagnosis(db, body)
