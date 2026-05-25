"""Contextual mentor agent — HAC-13 (GraphExecutor path)."""

from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Any
from uuid import uuid4

from career_forge.schemas.mentor import MentorContextSnapshot, MentorRequest, MentorResponse
from career_forge.services.mentor import build_mentor_response


def _lc_event(
    event: str,
    name: str,
    run_id: str,
    data: dict[str, Any],
) -> dict[str, Any]:
    return {
        "event": event,
        "name": name,
        "run_id": run_id,
        "tags": [],
        "metadata": {},
        "data": data,
    }


class MentorAgentRunnable:
    """Agent runnable that maps learner context + message → MentorResponse."""

    graph_name = "mentor"

    async def astream_events(
        self,
        input_data: dict[str, Any],
        *,
        version: str = "v2",
    ) -> AsyncIterator[dict[str, Any]]:
        del version
        payload = MentorRequest.model_validate(input_data)
        context_raw = input_data.get("context_snapshot") or {}
        context = MentorContextSnapshot.model_validate(context_raw)
        result = build_mentor_response(payload, context)
        run_id = str(uuid4())

        yield _lc_event("on_chain_start", self.graph_name, run_id, {})

        yield _lc_event(
            "on_chain_stream",
            "compose_reply",
            run_id,
            {
                "chunk": {
                    "type": "progress",
                    "step": "compose_reply",
                    "message": f"Consultando memória de {payload.node_title or 'trilha'}",
                },
            },
        )

        output = result.model_dump()
        yield _lc_event(
            "on_chain_end",
            self.graph_name,
            run_id,
            {"output": output, "input": input_data},
        )


def build_mentor_agent() -> MentorAgentRunnable:
    """Return mentor runnable registered under name ``mentor``."""
    return MentorAgentRunnable()
