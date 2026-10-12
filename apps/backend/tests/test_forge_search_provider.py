"""CAR-138 — Forge search follows the Run provider captured on the forge.

Seams:
- A gateway citation with a url, a title, and a snippet is a Forge source
- A citation with no URL fails that forge (WebSearchProviderError)
- Switch off keeps today's OpenAI web_search path
- A flip after the GraphRun exists does not change that forge's search
"""

from __future__ import annotations

import asyncio
from typing import Any
from unittest.mock import MagicMock, patch

import pytest
from sqlalchemy import delete
from sqlalchemy.orm import Session

from career_forge.ai.executor import GraphExecutor
from career_forge.ai.factory import AgentFactory
from career_forge.ai.graphs.roadmap_forge import RoadmapForgeGraphRunnable
from career_forge.ai.llm.model_chat import ModelGatewayKeyMissing, bound_run_provider
from career_forge.ai.run import GraphRun, InMemoryGraphRunStore
from career_forge.ai.tools.forge_search import build_forge_search_client, post_gateway_chat
from career_forge.ai.tools.openai_web_search import (
    WebSearchProviderError,
    WebSearchSource,
)
from career_forge.auth.operator_session import OperatorPrincipal
from career_forge.db.models.operator import Operator
from career_forge.db.models.provider_switch import ProviderSwitch
from career_forge.db.session import SessionLocal
from career_forge.schemas.diagnosis import DiagnosisProfile, DiagnosisResponse
from career_forge.schemas.study_plan import (
    StudyPlan,
    StudyPlanEvaluation,
    StudyPlanNode,
    StudyPlanTask,
)
from career_forge.services.provider_switch import stamp_run_provider, write_provider_switch

from tests.test_openai_web_search import CONTENT_BLOCKS, FakeMessage

_GATEWAY_SNIPPET = "FastAPI is a modern web framework for building APIs."


def _gateway_body() -> dict[str, Any]:
    return {
        "choices": [
            {
                "message": {
                    "role": "assistant",
                    "content": "Use the official docs.",
                    "annotations": [
                        {
                            "type": "url_citation",
                            "url_citation": {
                                "url": "https://fastapi.tiangolo.com/",
                                "title": "FastAPI",
                                "content": _GATEWAY_SNIPPET,
                                "start_index": 0,
                                "end_index": 4,
                            },
                        }
                    ],
                }
            }
        ]
    }


def test_gateway_citation_is_a_forge_source(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "sk-openai")
    monkeypatch.setenv("OPENROUTER_API_KEY", "sk-or")
    monkeypatch.setenv("FORGE_SEARCH_MODEL", "gpt-5.4")
    captured: dict[str, Any] = {}

    def post_gateway_chat(llm: Any, payload: dict[str, Any]) -> dict[str, Any]:
        del llm
        captured["payload"] = payload
        return _gateway_body()

    with bound_run_provider("gateway"):
        with patch("career_forge.ai.tools.forge_search.ChatOpenAI") as chat:
            with patch(
                "career_forge.ai.tools.forge_search.post_gateway_chat",
                post_gateway_chat,
            ):
                client = build_forge_search_client()
                result = asyncio.run(client.search("Find the FastAPI docs"))

    payload = captured["payload"]
    assert payload["tools"] == [
        {"type": "openrouter:web_search", "parameters": {"engine": "auto"}},
    ]
    assert payload["model"] == "openai/gpt-5.4"
    assert "plugins" not in payload
    kwargs = chat.call_args.kwargs
    assert kwargs["model"] == "openai/gpt-5.4"
    assert kwargs["api_key"] == "sk-or"
    assert kwargs["base_url"] == "https://openrouter.ai/api/v1"
    assert "plugins" not in kwargs
    assert result.sources == [
        WebSearchSource(
            title="FastAPI",
            url="https://fastapi.tiangolo.com/",
            snippet=_GATEWAY_SNIPPET,
        ),
    ]


def test_gateway_post_reads_the_citation_json() -> None:
    raw = MagicMock()
    raw.json.return_value = _gateway_body()
    llm = MagicMock()
    llm.client.with_raw_response.create.return_value = raw

    body = post_gateway_chat(llm, {"model": "openai/gpt-5.4"})

    citation = body["choices"][0]["message"]["annotations"][0]["url_citation"]
    assert citation["content"] == _GATEWAY_SNIPPET
    assert citation["url"] == "https://fastapi.tiangolo.com/"
    raw.json.assert_called_once()


def _body_without_url() -> dict[str, Any]:
    body = _gateway_body()
    body["choices"][0]["message"]["annotations"][0]["url_citation"]["url"] = ""
    return body


def _diagnosis() -> dict[str, Any]:
    return DiagnosisResponse(
        profile=DiagnosisProfile(
            label="Beginner",
            track_id="rag-engineer-beginner",
            persona_slug="beginner",
        ),
        strengths=["Clear goal"],
        gaps=["Little practice"],
        starting_priorities=["rag-embeddings"],
        estimated_mastery={"rag-embeddings": 10},
    ).model_dump()


def _forge_input() -> dict[str, Any]:
    return {
        "user_id": "learner-1",
        "goal_id": "rag-engineer",
        "motivation": "Ship grounded answers.",
        "diagnosis": _diagnosis(),
    }


def _executor() -> GraphExecutor:
    factory = AgentFactory()
    factory.register(
        "roadmap_forge",
        lambda: RoadmapForgeGraphRunnable(
            planner=_Planner(),
            evaluator=_Evaluator(),
        ),
    )
    return GraphExecutor(factory=factory, store=InMemoryGraphRunStore())


class _Evaluator:
    async def evaluate(self, plan: StudyPlan, trace: Any = None) -> StudyPlanEvaluation:
        del plan, trace
        return StudyPlanEvaluation(verdict="ship", strengths=["clear sequence"])


class _Planner:
    async def create_plan(
        self,
        *,
        context: Any,
        research_events: list[dict],
        trace: Any = None,
    ) -> StudyPlan:
        del context, research_events, trace
        return _plan()

    async def revise_plan(self, **kwargs: Any) -> StudyPlan:
        del kwargs
        return _plan()


def _plan() -> StudyPlan:
    return StudyPlan(
        goal="rag-engineer",
        learner_context_summary="summary",
        strategy="Start with embeddings.",
        nodes=[
            StudyPlanNode(
                node_id="rag-embeddings",
                title="Embeddings",
                why_now="Ground the answers.",
                tasks=[
                    StudyPlanTask(
                        title="Read the docs",
                        outcome="Explain a vector.",
                        evidence_prompt="Name the library.",
                    ),
                ],
            ),
        ],
    )


@pytest.mark.asyncio
async def test_empty_gateway_citation_fails_the_forge(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("FORGE_STREAM_DELAY_SEC", "0")
    monkeypatch.setenv("OPENROUTER_API_KEY", "sk-or")
    monkeypatch.setenv("OPENAI_API_KEY", "sk-openai")

    def post_gateway_chat(llm: Any, payload: dict[str, Any]) -> dict[str, Any]:
        del llm, payload
        return _body_without_url()

    run = GraphRun(
        graph_name="roadmap_forge",
        user_id="learner-1",
        input=_forge_input(),
        run_provider="gateway",
    )
    with patch(
        "career_forge.ai.tools.forge_search.post_gateway_chat",
        post_gateway_chat,
    ):
        with pytest.raises(WebSearchProviderError):
            await _executor().execute(run, stream=False)

    assert run.status == "failed"


def test_missing_gateway_key_does_not_search_with_openai(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    monkeypatch.setenv("OPENAI_API_KEY", "sk-openai")

    with bound_run_provider("gateway"):
        with patch("career_forge.ai.tools.forge_search.ChatOpenAI") as chat:
            with pytest.raises(ModelGatewayKeyMissing):
                build_forge_search_client()

    chat.assert_not_called()


@pytest.mark.asyncio
async def test_switch_off_keeps_the_openai_web_search_path(
    switch_session: Session,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("FORGE_STREAM_DELAY_SEC", "0")
    monkeypatch.setenv("OPENAI_API_KEY", "sk-openai")
    monkeypatch.setenv("OPENROUTER_API_KEY", "sk-or")
    monkeypatch.setenv("FORGE_SEARCH_MODEL", "gpt-5.4")
    principal = _access_operator(switch_session)
    run = stamp_run_provider(
        GraphRun(
            graph_name="roadmap_forge",
            user_id="learner-1",
            input=_forge_input(),
        ),
        switch_session,
    )
    _arm(switch_session, principal, on=True)
    llm = _openai_llm()

    with patch("career_forge.ai.tools.openai_web_search.ChatOpenAI", return_value=llm):
        with patch("career_forge.ai.tools.forge_search.post_gateway_chat") as gateway:
            await _executor().execute(run, stream=False)

    gateway.assert_not_called()
    tools = [call.kwargs["tools"] for call in llm.bind.call_args_list]
    assert tools
    assert all(tool == [{"type": "web_search"}] for tool in tools)
    assert run.run_provider == "direct"
    assert run.status == "completed"


def _openai_llm() -> Any:
    llm = MagicMock()
    bound = MagicMock()
    llm.bind.return_value = bound
    bound.invoke.return_value = FakeMessage(CONTENT_BLOCKS)
    return llm


_OPERATOR_EMAIL = "car-138-access@borderless.com"


@pytest.fixture
def switch_session() -> Session:
    session = SessionLocal()
    session.execute(delete(ProviderSwitch))
    session.execute(delete(Operator).where(Operator.email == _OPERATOR_EMAIL))
    session.commit()
    try:
        yield session
    finally:
        session.execute(delete(ProviderSwitch))
        session.execute(delete(Operator).where(Operator.email == _OPERATOR_EMAIL))
        session.commit()
        session.close()


def _arm(session: Session, principal: OperatorPrincipal, *, on: bool) -> None:
    write_provider_switch(session, principal=principal, on=on)
    session.commit()


def _access_operator(session: Session) -> OperatorPrincipal:
    row = Operator(email=_OPERATOR_EMAIL, desk_roles="access")
    session.add(row)
    session.flush()
    return OperatorPrincipal(email=row.email, operator_id=row.id, desk_roles="access")


@pytest.mark.asyncio
async def test_flip_after_the_forge_exists_keeps_gateway_search(
    switch_session: Session,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("FORGE_STREAM_DELAY_SEC", "0")
    monkeypatch.setenv("OPENAI_API_KEY", "sk-openai")
    monkeypatch.setenv("OPENROUTER_API_KEY", "sk-or")
    monkeypatch.setenv("FORGE_SEARCH_MODEL", "gpt-5.4")
    principal = _access_operator(switch_session)
    _arm(switch_session, principal, on=True)
    run = stamp_run_provider(
        GraphRun(
            graph_name="roadmap_forge",
            user_id="learner-1",
            input=_forge_input(),
        ),
        switch_session,
    )
    _arm(switch_session, principal, on=False)
    payloads: list[dict[str, Any]] = []

    def post_gateway_chat(llm: Any, payload: dict[str, Any]) -> dict[str, Any]:
        del llm
        payloads.append(payload)
        return _gateway_body()

    with patch(
        "career_forge.ai.tools.forge_search.post_gateway_chat",
        post_gateway_chat,
    ):
        result = await _executor().execute(run, stream=False)

    assert run.run_provider == "gateway"
    assert payloads
    assert all(
        payload["tools"] == [
            {"type": "openrouter:web_search", "parameters": {"engine": "auto"}},
        ]
        and ":online" not in payload["model"]
        and "plugins" not in payload
        for payload in payloads
    )
    sources = [
        source
        for event in result.events
        if event.get("type") == "artifact_found"
        for source in event.get("sources") or []
    ]
    assert sources[0] == {
        "title": "FastAPI",
        "url": "https://fastapi.tiangolo.com/",
        "snippet": _GATEWAY_SNIPPET,
    }
