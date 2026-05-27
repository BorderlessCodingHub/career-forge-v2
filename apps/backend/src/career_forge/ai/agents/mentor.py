"""Contextual mentor agent — HAC-13 (GraphExecutor path)."""

from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Any

from career_forge.ai.streaming.langchain_events import (
    LangChainStreamEvent,
    emit_chain_end,
    emit_chain_start,
    emit_chain_stream,
    new_run_id,
)
from career_forge.schemas.mentor import MentorContextSnapshot, MentorRequest, MentorResponse
from career_forge.services.mentor import build_mentor_response


class MentorAgentRunnable:
    """Agent runnable that maps learner context + message → MentorResponse."""

    graph_name = "mentor"

    async def astream_events(
        self,
        input_data: dict[str, Any],
        *,
        version: str = "v2",
    ) -> AsyncIterator[LangChainStreamEvent]:
        del version
        payload = MentorRequest.model_validate(input_data)
        context_raw = input_data.get("context_snapshot") or {}
        context = MentorContextSnapshot.model_validate(context_raw)
        result = build_mentor_response(payload, context)
        run_id = new_run_id()

        yield emit_chain_start(self.graph_name, run_id)

        yield emit_chain_stream(
            "compose_reply",
            run_id,
            {
                "type": "progress",
                "step": "compose_reply",
                "message": f"Consultando memória de {payload.node_title or 'trilha'}",
            },
        )

        output = result.model_dump()
        yield emit_chain_end(
            self.graph_name,
            run_id,
            output=output,
            input_data=input_data,
        )


def build_mentor_agent() -> MentorAgentRunnable:
    """Return mentor runnable registered under name ``mentor``."""
    return MentorAgentRunnable()
