"""CAR-136 — model chat follows the Run provider captured on the GraphRun.

Seams:
- ChatOpenAI wire (prefix, base URL, key) for a captured Run provider
- Cost-burn grouping key
- A flip during the run does not change that capture
- diagnosis_interview client follows the provider bound for that turn
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Any
from unittest.mock import patch

import pytest
from sqlalchemy import delete
from sqlalchemy.orm import Session

from career_forge.ai.executor import GraphExecutor
from career_forge.ai.factory import AgentFactory
from career_forge.ai.llm.client import StructuredLlmClient, StructuredToolClient
from career_forge.ai.llm.model_chat import ModelGatewayKeyMissing, bound_run_provider
from career_forge.ai.run import GraphRun, InMemoryGraphRunStore
from career_forge.ai.streaming.langchain_events import (
    LangChainStreamEvent,
    emit_chain_end,
    emit_chain_start,
    new_run_id,
)
from career_forge.ai.tools.tutor_llm import generate_tutor_reply
from career_forge.auth.operator_session import OperatorPrincipal
from career_forge.db.models.operator import Operator
from career_forge.db.models.provider_switch import ProviderSwitch
from career_forge.db.session import SessionLocal
from career_forge.schemas.tutor import TutorContext
from career_forge.services.provider_switch import stamp_run_provider, write_provider_switch

_BARE_MODELS = ("gpt-5.4", "gpt-4.1-nano", "gpt-5.4-mini")
_MODEL_CHAT_GRAPHS = ("roadmap_forge", "tutor", "mock_interview")
_DIRECT_ONLY_GRAPHS = ("diagnosis_interview", "diagnosis", "mentor", "validation")


def _access_operator(session: Session) -> OperatorPrincipal:
    row = Operator(email="car-136-access@borderless.com", desk_roles="access")
    session.add(row)
    session.flush()
    return OperatorPrincipal(email=row.email, operator_id=row.id, desk_roles="access")


@pytest.fixture
def switch_session() -> Session:
    session = SessionLocal()
    session.execute(delete(ProviderSwitch))
    session.execute(delete(Operator).where(Operator.email == "car-136-access@borderless.com"))
    session.commit()
    try:
        yield session
    finally:
        session.execute(delete(ProviderSwitch))
        session.execute(delete(Operator).where(Operator.email == "car-136-access@borderless.com"))
        session.commit()
        session.close()


def _arm(session: Session, principal: OperatorPrincipal, *, on: bool) -> None:
    write_provider_switch(session, principal=principal, on=on)
    session.commit()


@pytest.mark.parametrize("model", _BARE_MODELS)
def test_direct_provider_uses_the_openai_key_and_the_bare_model(
    monkeypatch: pytest.MonkeyPatch,
    model: str,
) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "sk-openai")
    monkeypatch.setenv("OPENROUTER_API_KEY", "sk-or")

    with patch("career_forge.ai.llm.client.ChatOpenAI") as chat:
        client = StructuredToolClient(
            model_env="FORGE_PLANNER_MODEL",
            default_model=model,
            model=model,
        )

    assert client.model == model
    kwargs = chat.call_args.kwargs
    assert kwargs["model"] == model
    assert kwargs["api_key"] == "sk-openai"
    assert "base_url" not in kwargs


@pytest.mark.parametrize("model", _BARE_MODELS)
def test_gateway_prefixes_the_model_on_the_wire_only(
    monkeypatch: pytest.MonkeyPatch,
    model: str,
) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "sk-openai")
    monkeypatch.setenv("OPENROUTER_API_KEY", "sk-or")

    with bound_run_provider("gateway"):
        with patch("career_forge.ai.llm.client.ChatOpenAI") as chat:
            client = StructuredToolClient(
                model_env="FORGE_PLANNER_MODEL",
                default_model=model,
                model=model,
            )

    assert client.model == model
    kwargs = chat.call_args.kwargs
    assert kwargs["model"] == f"openai/{model}"
    assert kwargs["api_key"] == "sk-or"
    assert kwargs["base_url"] == "https://openrouter.ai/api/v1"


def test_missing_gateway_key_does_not_fall_back_to_openai(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    monkeypatch.setenv("OPENAI_API_KEY", "sk-openai")

    with bound_run_provider("gateway"):
        with patch("career_forge.ai.llm.client.ChatOpenAI") as chat:
            with pytest.raises(ModelGatewayKeyMissing):
                StructuredToolClient(
                    model_env="FORGE_PLANNER_MODEL",
                    default_model="gpt-5.4",
                    model="gpt-5.4",
                )

    chat.assert_not_called()


def test_tutor_fails_when_the_captured_gateway_key_is_gone(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    monkeypatch.setenv("OPENAI_API_KEY", "sk-openai")

    with bound_run_provider("gateway"):
        with pytest.raises(ModelGatewayKeyMissing):
            generate_tutor_reply(
                message="What is a chunk?",
                history=[],
                context=TutorContext(node_title="Chunking"),
            )


@pytest.mark.parametrize("graph_name", _MODEL_CHAT_GRAPHS)
def test_model_chat_graph_captures_the_switch_at_creation(
    switch_session: Session,
    monkeypatch: pytest.MonkeyPatch,
    graph_name: str,
) -> None:
    monkeypatch.setenv("OPENROUTER_API_KEY", "sk-or")
    monkeypatch.setenv("OPENAI_API_KEY", "sk-openai")
    principal = _access_operator(switch_session)
    _arm(switch_session, principal, on=True)

    captured = stamp_run_provider(
        GraphRun(graph_name=graph_name, user_id="learner-1", input={}),
        switch_session,
    )

    _arm(switch_session, principal, on=False)
    assert captured.run_provider == "gateway"
    reread = stamp_run_provider(
        GraphRun(graph_name=graph_name, user_id="learner-1", input={}),
        switch_session,
    )
    assert reread.run_provider == "direct"


@pytest.mark.parametrize("graph_name", _MODEL_CHAT_GRAPHS)
@pytest.mark.asyncio
async def test_mid_run_flip_keeps_the_provider_captured_at_creation(
    switch_session: Session,
    monkeypatch: pytest.MonkeyPatch,
    graph_name: str,
) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "sk-openai")
    monkeypatch.setenv("OPENROUTER_API_KEY", "sk-or")
    principal = _access_operator(switch_session)
    _arm(switch_session, principal, on=True)
    run = stamp_run_provider(
        GraphRun(graph_name=graph_name, user_id="learner-1", input={}),
        switch_session,
    )

    class _ChatDuringRun:
        async def astream_events(
            self,
            input_data: dict[str, Any],
            *,
            version: str = "v2",
            config: Any | None = None,
        ) -> AsyncIterator[LangChainStreamEvent]:
            del input_data, version, config
            StructuredToolClient(
                model_env="FORGE_PLANNER_MODEL",
                default_model="gpt-5.4",
                model="gpt-5.4",
            )
            _arm(switch_session, principal, on=False)
            StructuredToolClient(
                model_env="TUTOR_MODEL",
                default_model="gpt-5.4-mini",
                model="gpt-5.4-mini",
            )
            run_id = new_run_id()
            yield emit_chain_start(self.graph_name, run_id)
            yield emit_chain_end(self.graph_name, run_id, output={"ok": True})

    _ChatDuringRun.graph_name = graph_name
    factory = AgentFactory()
    factory.register(graph_name, lambda: _ChatDuringRun())
    executor = GraphExecutor(factory=factory, store=InMemoryGraphRunStore())

    with patch("career_forge.ai.llm.client.ChatOpenAI") as chat:
        await executor.execute(run, stream=False)

    assert chat.call_count == 2
    first, second = (call.kwargs for call in chat.call_args_list)
    assert first["model"] == "openai/gpt-5.4"
    assert first["api_key"] == "sk-or"
    assert first["base_url"] == "https://openrouter.ai/api/v1"
    assert second["model"] == "openai/gpt-5.4-mini"
    assert second["api_key"] == "sk-or"
    assert second["base_url"] == "https://openrouter.ai/api/v1"
    assert run.run_provider == "gateway"


@pytest.mark.parametrize("graph_name", _DIRECT_ONLY_GRAPHS)
def test_diagnosis_mentor_and_rubric_graphs_stay_on_the_direct_provider(
    switch_session: Session,
    monkeypatch: pytest.MonkeyPatch,
    graph_name: str,
) -> None:
    monkeypatch.setenv("OPENROUTER_API_KEY", "sk-or")
    monkeypatch.setenv("OPENAI_API_KEY", "sk-openai")
    principal = _access_operator(switch_session)
    _arm(switch_session, principal, on=True)

    first = stamp_run_provider(
        GraphRun(graph_name=graph_name, user_id="learner-1", input={}),
        switch_session,
    )
    _arm(switch_session, principal, on=False)
    _arm(switch_session, principal, on=True)
    second = stamp_run_provider(
        GraphRun(graph_name=graph_name, user_id="learner-1", input={}),
        switch_session,
    )

    assert first.run_provider == "direct"
    assert second.run_provider == "direct"


def test_diagnosis_interview_client_follows_the_bound_provider(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "sk-openai")
    monkeypatch.setenv("OPENROUTER_API_KEY", "sk-or")

    with bound_run_provider("gateway"):
        with patch("career_forge.ai.llm.client.ChatOpenAI") as chat:
            client = StructuredLlmClient("gpt-5.4")

    assert client.model == "gpt-5.4"
    kwargs = chat.call_args.kwargs
    assert kwargs["model"] == "openai/gpt-5.4"
    assert kwargs["api_key"] == "sk-or"
    assert kwargs["base_url"] == "https://openrouter.ai/api/v1"
