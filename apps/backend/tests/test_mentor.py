"""Unit tests — contextual mentor agent, service, and HTTP API."""

from __future__ import annotations

import pytest

from career_forge.ai.agents.mentor import MentorAgentRunnable
from career_forge.ai.executor import GraphExecutor
from career_forge.ai.factory import AgentFactory
from career_forge.ai.run import GraphRun, GraphRunResult, InMemoryGraphRunStore
from career_forge.schemas.mentor import MentorRequest, MentorResponse
from career_forge.services.mentor import build_mentor_response

SAMPLE_REQUEST = MentorRequest(
    user_id="demo-ana",
    node_id="rag-grounding",
    node_title="Grounded generation",
    message="Onde errei na validação de REST?",
)


class TestMentorService:
    def test_build_mentor_response_matches_contract(self) -> None:
        from career_forge.services.mentor import _demo_context

        context = _demo_context("rag-grounding")
        result = build_mentor_response(SAMPLE_REQUEST, context)
        assert isinstance(result, MentorResponse)
        assert result.reply
        assert result.context_snapshot.validation_count >= 0

    def test_gaps_intent_uses_memory(self) -> None:
        from career_forge.services.mentor import _demo_context

        context = _demo_context("rag-grounding")
        request = SAMPLE_REQUEST.model_copy(update={"message": "Quais lacunas eu ainda tenho?"})
        result = build_mentor_response(request, context)
        assert "lacuna" in result.reply.lower() or "revis" in result.reply.lower()

    def test_references_intent_returns_outcomes(self) -> None:
        from career_forge.services.mentor import _demo_context

        context = _demo_context("rag-grounding")
        request = SAMPLE_REQUEST.model_copy(update={"message": "Me dê referências para estudar"})
        result = build_mentor_response(request, context)
        assert result.references or "refer" in result.reply.lower()


class TestMentorAgent:
    @pytest.mark.asyncio
    async def test_mentor_agent_via_graph_executor(self) -> None:
        from career_forge.services.mentor import _demo_context

        context = _demo_context("rag-grounding")
        store = InMemoryGraphRunStore()
        executor = GraphExecutor(store=store)
        run = GraphRun(
            graph_name="mentor",
            user_id="demo-ana",
            input={
                **SAMPLE_REQUEST.model_dump(),
                "context_snapshot": context.model_dump(),
            },
        )
        store.save(run)
        result = await executor.execute(run, stream=False)
        assert isinstance(result, GraphRunResult)
        assert result.run.status == "completed"
        assert result.run.output is not None
        assert result.run.output["type"] == "graph_complete"
        mentor = MentorResponse.model_validate(result.run.output["output"])
        assert mentor.reply

    def test_factory_returns_mentor_runnable(self) -> None:
        factory = AgentFactory()
        runnable = factory.get("mentor")
        assert isinstance(runnable, MentorAgentRunnable)
        assert runnable.graph_name == "mentor"


def test_get_mentor_context_api(client) -> None:
    response = client.get("/mentor/context", params={"user_id": "demo-ana", "node_id": "rag-grounding"})
    assert response.status_code == 200
    payload = response.json()
    assert "validation_count" in payload
    assert "recent_gaps" in payload


def test_post_mentor_api(client) -> None:
    response = client.post("/mentor", json=SAMPLE_REQUEST.model_dump())
    assert response.status_code == 200
    payload = response.json()
    assert payload["run_id"]
    assert payload["mentor"]["reply"]
    assert payload["mentor"]["context_snapshot"]["validation_count"] >= 0


def test_post_mentor_rejects_empty_message(client) -> None:
    body = SAMPLE_REQUEST.model_dump()
    body["message"] = "   "
    response = client.post("/mentor", json=body)
    assert response.status_code == 422
