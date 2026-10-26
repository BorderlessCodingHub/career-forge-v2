"""Shared LangChain structured-output client for Career Forge LLM calls."""

from __future__ import annotations

import logging
import os
from typing import Literal, TypeVar

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.runnables import RunnableConfig
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, ValidationError

from career_forge.ai.llm.errors import LlmError, RETRY_MESSAGE
from career_forge.ai.llm.model_chat import (
    OPENROUTER_BASE_URL,
    ModelGatewayKeyMissing,
    configured_model_name,
    current_run_provider,
    wire_model_name,
)
from career_forge.ai.tracing import LlmTraceContext, trace_config_for_invoke
from career_forge.db.models.provider_switch import DIRECT_PROVIDER, GATEWAY_PROVIDER

logger = logging.getLogger(__name__)

TSchema = TypeVar("TSchema", bound=BaseModel)
StructuredMethod = Literal["json_schema", "function_calling"]

DEFAULT_KEY_ERROR = "OPENAI_API_KEY is not configured"


class StructuredLlmClient:
    """Typed wrapper around ChatOpenAI.with_structured_output."""

    def __init__(
        self,
        model: str,
        *,
        temperature: float | None = 0.2,
        reasoning_effort: str | None = None,
        max_tokens: int | None = None,
        method: StructuredMethod = "json_schema",
    ) -> None:
        cleaned = model.strip()
        if not cleaned:
            msg = "LLM model name must be non-empty"
            raise ValueError(msg)
        self._model = configured_model_name(cleaned)
        self._temperature = temperature
        self._reasoning_effort = reasoning_effort
        self._max_tokens = max_tokens
        self._method = method
        self._chat = self._build_chat()

    def _chat_kwargs(self, *, model: str, api_key: str, base_url: str | None = None) -> dict:
        """Sampling params are omitted when unset. Luna rejects a non-default temperature.

        An unset completion cap lets the gateway reserve the model maximum
        (65536 for Luna) and refuse the call when the key cannot cover it.
        """
        kwargs: dict = {"model": model, "api_key": api_key}
        if base_url is not None:
            kwargs["base_url"] = base_url
        if self._temperature is not None:
            kwargs["temperature"] = self._temperature
        if self._reasoning_effort is not None:
            kwargs["reasoning_effort"] = self._reasoning_effort
        if self._max_tokens is not None:
            kwargs["max_tokens"] = self._max_tokens
        return kwargs

    def _build_chat(self) -> ChatOpenAI:
        """Wire follows the provider bound for this turn. No fallback."""
        provider = current_run_provider()
        if provider == GATEWAY_PROVIDER:
            gateway_key = os.getenv("OPENROUTER_API_KEY", "").strip()
            if not gateway_key:
                raise ModelGatewayKeyMissing()
            return ChatOpenAI(
                **self._chat_kwargs(
                    model=wire_model_name(self._model, GATEWAY_PROVIDER),
                    api_key=gateway_key,
                    base_url=OPENROUTER_BASE_URL,
                )
            )
        direct_key = os.getenv("OPENAI_API_KEY", "").strip()
        if not direct_key:
            raise RuntimeError(DEFAULT_KEY_ERROR)
        return ChatOpenAI(
            **self._chat_kwargs(
                model=wire_model_name(self._model, DIRECT_PROVIDER),
                api_key=direct_key,
            )
        )

    @property
    def model(self) -> str:
        return self._model

    def _structured_runnable(self, schema: type[TSchema]):
        return self._chat.with_structured_output(
            schema,
            method=self._method,
            include_raw=False,
        )

    async def invoke(
        self,
        *,
        system: str,
        user: str,
        schema: type[TSchema],
        error_type: type[LlmError] = LlmError,
    ) -> TSchema:
        structured = self._structured_runnable(schema)
        messages = [SystemMessage(content=system), HumanMessage(content=user)]
        try:
            result = await structured.ainvoke(messages)
            return schema.model_validate(result)
        except ValidationError as exc:
            logger.exception("Structured output validation failed for %s", schema.__name__)
            raise error_type(RETRY_MESSAGE) from exc
        except LlmError:
            raise
        except Exception as exc:
            logger.exception("Structured LLM call failed for %s", schema.__name__)
            raise error_type(RETRY_MESSAGE) from exc


class StructuredToolClient:
    """Synchronous structured-output client for fire-and-forget / sync tools.

    Consolidates the boilerplate shared by the gap/tutor/mcq/planner tools:
    key check, env-based model resolution, `ChatOpenAI` construction and
    `with_structured_output(...).invoke(...)`. Raises ``RuntimeError`` when the
    Direct provider key is missing so callers fall back deterministically.
    A missing Model gateway key raises ``ModelGatewayKeyMissing`` instead.
    """

    def __init__(
        self,
        *,
        model_env: str,
        default_model: str,
        temperature: float = 0.2,
        method: StructuredMethod | None = "json_schema",
        key_error: str = DEFAULT_KEY_ERROR,
        model: str | None = None,
        api_key: str | None = None,
    ) -> None:
        configured = model or os.getenv(model_env, default_model)
        self._model = configured_model_name(configured)
        self._method = method
        provider = current_run_provider()
        if provider == GATEWAY_PROVIDER:
            gateway_key = os.getenv("OPENROUTER_API_KEY", "").strip()
            if not gateway_key:
                raise ModelGatewayKeyMissing()
            self._chat = ChatOpenAI(
                model=wire_model_name(self._model, GATEWAY_PROVIDER),
                api_key=gateway_key,
                base_url=OPENROUTER_BASE_URL,
                temperature=temperature,
            )
            return
        resolved_key = (api_key if api_key is not None else os.getenv("OPENAI_API_KEY", "")).strip()
        if not resolved_key:
            raise RuntimeError(key_error)
        self._chat = ChatOpenAI(
            model=wire_model_name(self._model, DIRECT_PROVIDER),
            api_key=resolved_key,
            temperature=temperature,
        )

    @property
    def model(self) -> str:
        return self._model

    def invoke(
        self,
        *,
        system: str,
        user: str,
        schema: type[TSchema],
        config: RunnableConfig | None = None,
        trace: LlmTraceContext | None = None,
        operation: str | None = None,
    ) -> TSchema:
        """Run a single sync structured-output call and validate into ``schema``."""
        resolved = config or trace_config_for_invoke(trace, operation=operation)
        if self._method is None:
            structured = self._chat.with_structured_output(schema)
        else:
            structured = self._chat.with_structured_output(schema, method=self._method)
        result = structured.invoke([("system", system), ("human", user)], config=resolved)
        return schema.model_validate(result)
