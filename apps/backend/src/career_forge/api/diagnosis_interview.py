"""Multi-turn diagnosis interview HTTP routes (HAC-44)."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from career_forge.ai.llm.diagnosis_interview import DiagnosisInterviewLlmError
from career_forge.ai.streaming.sse import format_sse
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


@router.post("/interview/start/stream")
async def start_diagnosis_interview_stream(
    body: InterviewStartRequest,
) -> StreamingResponse:
    """SSE stream — live mapping progress while starting the interview."""
    service = get_diagnosis_session_service()

    async def sse_body():
        try:
            async for line in service.stream_interview_start(body):
                yield line
        except DiagnosisInterviewLlmError as exc:
            yield format_sse({"type": "error", "message": exc.retry_message})

    return StreamingResponse(sse_body(), media_type="text/event-stream")


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


@router.post("/interview/{session_id}/turn/stream")
async def submit_diagnosis_turn_stream(
    session_id: str,
    body: InterviewTurnRequest,
) -> StreamingResponse:
    """SSE stream — live mapping progress while processing a turn."""
    service = get_diagnosis_session_service()

    async def sse_body():
        try:
            async for line in service.stream_interview_turn(session_id, body):
                yield line
        except DiagnosisSessionNotFoundError:
            yield format_sse({"type": "error", "message": "Sessão não encontrada."})
        except DiagnosisSessionCompleteError:
            yield format_sse({"type": "error", "message": "Sessão já finalizada."})
        except DiagnosisInterviewTurnError as exc:
            yield format_sse({"type": "error", "message": exc.message})
        except DiagnosisInterviewLlmError as exc:
            yield format_sse({"type": "error", "message": exc.retry_message})

    return StreamingResponse(sse_body(), media_type="text/event-stream")
