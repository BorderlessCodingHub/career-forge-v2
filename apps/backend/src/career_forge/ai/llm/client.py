"""Shared LangChain structured-output client for Career Forge LLM calls."""

from __future__ import annotations

import logging
import os
from typing import Literal, TypeVar

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, ValidationError

from career_forge.ai.llm.errors import LlmError, RETRY_MESSAGE

logger = logging.getLogger(__name__)

TSchema = TypeVar("TSchema", bound=BaseModel)
StructuredMethod = Literal["json_schema", "function_calling"]

DEFAULT_KEY_ERROR = "OPENAI_API_KEY não configurada"


class StructuredLlmClient:
    """Typed wrapper around ChatOpenAI.with_structured_output."""

    def __init__(
        self,
        model: str,
        *,
        temperature: float = 0.2,
        method: StructuredMethod = "json_schema",
    ) -> None:
        cleaned = model.strip()
        if not cleaned:
            msg = "LLM model name must be non-empty"
            raise ValueError(msg)
        self._model = cleaned
        self._temperature = temperature
        self._method = method
        self._chat = ChatOpenAI(model=self._model, temperature=self._temperature)

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
    OpenAI key check, env-based model resolution, `ChatOpenAI` construction and
    `with_structured_output(...).invoke(...)`. Raises ``RuntimeError`` when the
    key is missing so callers fall back deterministically (tests / offline).
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
        resolved_key = (api_key if api_key is not None else os.getenv("OPENAI_API_KEY", "")).strip()
        if not resolved_key:
            raise RuntimeError(key_error)
        self._model = model or os.getenv(model_env, default_model)
        self._method = method
        self._chat = ChatOpenAI(model=self._model, api_key=resolved_key, temperature=temperature)

    @property
    def model(self) -> str:
        return self._model

    def invoke(self, *, system: str, user: str, schema: type[TSchema]) -> TSchema:
        """Run a single sync structured-output call and validate into ``schema``."""
        if self._method is None:
            structured = self._chat.with_structured_output(schema)
        else:
            structured = self._chat.with_structured_output(schema, method=self._method)
        result = structured.invoke([("system", system), ("human", user)])
        return schema.model_validate(result)
