"""Chapter Q&A tutor agent — runs through GraphExecutor (HAC-71)."""

from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator
from typing import Any

from career_forge.ai.streaming.langchain_events import (
    LangChainStreamEvent,
    emit_chain_end,
    emit_chain_start,
    emit_chain_stream,
    new_run_id,
)
from career_forge.schemas.tutor import TutorContext, TutorRequest
from career_forge.services.tutor import build_tutor_response


class TutorAgentRunnable:
    """Maps chapter context + question → grounded TutorResponse via GraphExecutor."""

    graph_name = "tutor"

    async def astream_events(
        self,
        input_data: dict[str, Any],
        *,
        version: str = "v2",
    ) -> AsyncIterator[LangChainStreamEvent]:
        del version
        payload = TutorRequest.model_validate(input_data)
        context = TutorContext.model_validate(input_data.get("context_snapshot") or {})
        run_id = new_run_id()

        yield emit_chain_start(self.graph_name, run_id)
        yield emit_chain_stream(
            "compose_reply",
            run_id,
            {
                "type": "progress",
                "step": "compose_reply",
                "message": f"Consultando conceitos de {payload.node_title or 'capítulo'}",
            },
        )

        result = await asyncio.to_thread(build_tutor_response, payload, context)

        yield emit_chain_end(
            self.graph_name,
            run_id,
            output=result.model_dump(),
            input_data=input_data,
        )


def build_tutor_agent() -> TutorAgentRunnable:
    """Return tutor runnable registered under name ``tutor``."""
    return TutorAgentRunnable()
