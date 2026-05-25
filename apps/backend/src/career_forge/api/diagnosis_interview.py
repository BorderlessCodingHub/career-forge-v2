"""Multi-turn diagnosis interview HTTP routes (HAC-44)."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from career_forge.ai.llm.diagnosis_interview import DiagnosisInterviewLlmError
from career_forge.schemas.diagnosis_interview import (
    InterviewStartRequest,
    InterviewTurnRequest,
    InterviewTurnResponse,
)
from career_forge.services.diagnosis_session import (
    DiagnosisInterviewTurnError,
    DiagnosisSessionCompleteError,
    DiagnosisSessionNotFoundError,
    get_diagnosis_session_service,
)

router = APIRouter()


@router.post("/interview/start", response_model=InterviewTurnResponse)
async def start_diagnosis_interview(
    body: InterviewStartRequest,
) -> InterviewTurnResponse:
    """Start adaptive diagnosis interview — intake + optional CV → first questions."""
    service = get_diagnosis_session_service()
    try:
        return await service.start_interview(body)
    except DiagnosisInterviewLlmError as exc:
        raise HTTPException(
            status_code=503,
            detail={"message": exc.retry_message, "retry": True},
        ) from exc


@router.post("/interview/{session_id}/turn", response_model=InterviewTurnResponse)
async def submit_diagnosis_turn(
    session_id: str,
    body: InterviewTurnRequest,
) -> InterviewTurnResponse:
    """Submit answers for current round → next questions or final diagnosis."""
    service = get_diagnosis_session_service()
    try:
        return await service.submit_turn(session_id, body)
    except DiagnosisSessionNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Sessão não encontrada.") from exc
    except DiagnosisSessionCompleteError as exc:
        raise HTTPException(status_code=409, detail="Sessão já finalizada.") from exc
    except DiagnosisInterviewTurnError as exc:
        raise HTTPException(status_code=422, detail=exc.message) from exc
    except DiagnosisInterviewLlmError as exc:
        raise HTTPException(
            status_code=503,
            detail={"message": exc.retry_message, "retry": True},
        ) from exc
