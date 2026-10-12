"""Forge search follows the Run provider captured on that forge (CAR-138)."""

from __future__ import annotations

import asyncio
import json
import os
from typing import Any

from langchain_openai import ChatOpenAI

from career_forge.ai.llm.model_chat import (
    OPENROUTER_BASE_URL,
    ModelGatewayKeyMissing,
    configured_model_name,
    current_run_provider,
    wire_model_name,
)
from career_forge.ai.tools.openai_web_search import (
    OpenAiNativeWebSearchClient,
    WebSearchClient,
    WebSearchProviderError,
    WebSearchResult,
    WebSearchSource,
)
from career_forge.db.models.provider_switch import GATEWAY_PROVIDER

_NO_URL = "Forge search did not return a URL."


def build_forge_search_client() -> WebSearchClient:
    """Direct provider keeps OpenAI web_search. Gateway uses OpenRouter."""
    if current_run_provider() == GATEWAY_PROVIDER:
        return OpenRouterWebSearchClient()
    return OpenAiNativeWebSearchClient()


class OpenRouterWebSearchClient:
    """OpenRouter server tool ``openrouter:web_search``, engine ``auto``."""

    def __init__(
        self,
        *,
        model: str | None = None,
        api_key: str | None = None,
    ) -> None:
        resolved_key = (
            api_key if api_key is not None else os.getenv("OPENROUTER_API_KEY", "")
        ).strip()
        if not resolved_key:
            raise ModelGatewayKeyMissing()
        configured = model or os.getenv("FORGE_SEARCH_MODEL", "gpt-5.4")
        bare = _without_online_suffix(configured_model_name(configured))
        self._model = wire_model_name(bare, GATEWAY_PROVIDER)
        self._llm = ChatOpenAI(
            model=self._model,
            api_key=resolved_key,
            base_url=OPENROUTER_BASE_URL,
            temperature=0,
        )

    async def search(self, prompt: str) -> WebSearchResult:
        return await asyncio.to_thread(self._search_sync, prompt)

    def _search_sync(self, prompt: str) -> WebSearchResult:
        payload = {
            "model": self._model,
            "messages": [{"role": "user", "content": prompt}],
            "tools": [_gateway_web_search_tool()],
        }
        return parse_gateway_search_body(post_gateway_chat(self._llm, payload))


def post_gateway_chat(llm: ChatOpenAI, payload: dict[str, Any]) -> dict[str, Any]:
    """Chat completions JSON, including citation ``content`` the SDK model drops."""
    raw = llm.client.with_raw_response.create(**payload)
    try:
        body = raw.json()
    except json.JSONDecodeError as exc:
        raise WebSearchProviderError(_NO_URL) from exc
    if not isinstance(body, dict):
        raise WebSearchProviderError(_NO_URL)
    return body


def parse_gateway_search_body(body: dict[str, Any]) -> WebSearchResult:
    """A Forge source is the citation title, URL, and snippet."""
    message = _assistant_message(body)
    text = message.get("content") if isinstance(message.get("content"), str) else ""
    annotations = message.get("annotations")
    sources = _sources_from_annotations(
        annotations if isinstance(annotations, list) else [],
        text,
    )
    if not sources:
        raise WebSearchProviderError(_NO_URL)
    return WebSearchResult(query="", summary=text, sources=sources)


def _assistant_message(body: dict[str, Any]) -> dict[str, Any]:
    choices = body.get("choices")
    if not isinstance(choices, list) or not choices:
        return {}
    message = choices[0].get("message") if isinstance(choices[0], dict) else None
    return message if isinstance(message, dict) else {}


def _sources_from_annotations(
    annotations: list[Any],
    text: str,
) -> list[WebSearchSource]:
    sources: list[WebSearchSource] = []
    seen_urls: set[str] = set()
    for annotation in annotations:
        if not isinstance(annotation, dict):
            continue
        nested = annotation.get("url_citation")
        fields = nested if isinstance(nested, dict) else annotation
        if annotation.get("type") not in {"url_citation", "citation"} and not isinstance(
            nested, dict
        ):
            continue
        url = str(fields.get("url") or "").strip()
        if not url or url in seen_urls:
            continue
        seen_urls.add(url)
        title = str(fields.get("title") or "").strip() or url
        snippet = str(fields.get("content") or "").strip()
        if not snippet:
            snippet = _cited_slice(text, fields)
        sources.append(WebSearchSource(title=title, url=url, snippet=snippet))
    return sources


def _cited_slice(text: str, fields: dict[str, Any]) -> str:
    start = fields.get("start_index")
    end = fields.get("end_index")
    if isinstance(start, int) and isinstance(end, int) and 0 <= start < end <= len(text):
        return text[start:end]
    return ""


def _gateway_web_search_tool() -> dict[str, Any]:
    return {
        "type": "openrouter:web_search",
        "parameters": {"engine": "auto"},
    }


def _without_online_suffix(model: str) -> str:
    if model.endswith(":online"):
        return model[: -len(":online")]
    return model
