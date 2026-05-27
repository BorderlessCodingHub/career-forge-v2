"""OpenAI native web search adapter via LangChain content blocks (HAC-54)."""

from __future__ import annotations

import asyncio
import os
from dataclasses import dataclass, field
from typing import Any, Protocol

from langchain_openai import ChatOpenAI


class WebSearchConfigurationError(RuntimeError):
    """Raised when OpenAI native web search cannot be configured."""


class WebSearchProviderError(RuntimeError):
    """Raised when native web search does not produce usable search output."""


@dataclass(frozen=True)
class WebSearchSource:
    title: str
    url: str
    snippet: str = ""


@dataclass(frozen=True)
class WebSearchResult:
    query: str
    summary: str
    sources: list[WebSearchSource] = field(default_factory=list)


class WebSearchClient(Protocol):
    async def search(self, prompt: str) -> WebSearchResult:
        """Run native search and return normalized citations."""


class OpenAiNativeWebSearchClient:
    """LangChain wrapper around OpenAI server-side `web_search`."""

    def __init__(
        self,
        *,
        model: str | None = None,
        api_key: str | None = None,
    ) -> None:
        resolved_key = (
            api_key if api_key is not None else os.getenv("OPENAI_API_KEY", "")
        ).strip()
        if not resolved_key:
            msg = (
                "OPENAI_API_KEY não configurada. Configure a chave antes de usar "
                "web_search no forge."
            )
            raise WebSearchConfigurationError(
                msg,
            )
        self._model = model or os.getenv("FORGE_SEARCH_MODEL", "gpt-5.4-mini")
        self._llm = ChatOpenAI(
            model=self._model,
            api_key=resolved_key,
            temperature=0,
            use_responses_api=True,
        )

    async def search(self, prompt: str) -> WebSearchResult:
        return await asyncio.to_thread(self._search_sync, prompt)

    def _search_sync(self, prompt: str) -> WebSearchResult:
        model_with_search = self._llm.bind(
            tools=[{"type": "web_search"}],
            tool_choice="required",
        )
        response = model_with_search.invoke(prompt)
        return parse_web_search_message(response)


def parse_web_search_message(message: Any) -> WebSearchResult:
    """Extract query, grounded text, and citations from LangChain content blocks."""
    blocks = _content_blocks(message)
    search_calls = extract_search_calls(blocks)
    if not search_calls:
        raise WebSearchProviderError("OpenAI web_search não foi executado pelo modelo.")

    sources = extract_search_citations(blocks)
    if not sources:
        raise WebSearchProviderError("OpenAI web_search não retornou citações utilizáveis.")

    return WebSearchResult(
        query=search_calls[0].get("query") or "",
        summary=_first_text(blocks),
        sources=sources,
    )


def extract_search_calls(content_blocks: list[dict[str, Any]]) -> list[dict[str, str]]:
    calls: list[dict[str, str]] = []
    for block in content_blocks:
        if block.get("type") != "server_tool_call" or block.get("name") != "web_search":
            continue
        args = block.get("args") if isinstance(block.get("args"), dict) else {}
        query = _query_from_args(args)
        if isinstance(query, str) and query.strip():
            calls.append(
                {
                    "id": str(block.get("id") or ""),
                    "name": "web_search",
                    "query": query.strip(),
                },
            )
    return calls


def _query_from_args(args: dict[str, Any]) -> str | None:
    query = args.get("query")
    if isinstance(query, str):
        return query
    queries = args.get("queries")
    if isinstance(queries, list):
        return " | ".join(str(item) for item in queries if str(item).strip())
    return None


def extract_search_citations(content_blocks: list[dict[str, Any]]) -> list[WebSearchSource]:
    sources: list[WebSearchSource] = []
    seen_urls: set[str] = set()
    for block in content_blocks:
        if block.get("type") != "text":
            continue
        text = block.get("text") if isinstance(block.get("text"), str) else ""
        annotations = block.get("annotations") if isinstance(block.get("annotations"), list) else []
        for annotation in annotations:
            if not isinstance(annotation, dict):
                continue
            if annotation.get("type") not in {"citation", "url_citation"}:
                continue
            url = str(annotation.get("url") or "")
            if not url or url in seen_urls:
                continue
            seen_urls.add(url)
            sources.append(
                WebSearchSource(
                    title=str(annotation.get("title") or url),
                    url=url,
                    snippet=_cited_text(text, annotation),
                ),
            )
    return sources


def build_openai_web_search_client_from_env() -> WebSearchClient:
    return OpenAiNativeWebSearchClient()


def _content_blocks(message: Any) -> list[dict[str, Any]]:
    blocks = getattr(message, "content_blocks", None)
    if blocks is None:
        raise WebSearchProviderError("Resposta LangChain sem content_blocks.")
    return [block for block in blocks if isinstance(block, dict)]


def _first_text(content_blocks: list[dict[str, Any]]) -> str:
    for block in content_blocks:
        if block.get("type") == "text" and isinstance(block.get("text"), str):
            return block["text"]
    return ""


def _cited_text(text: str, annotation: dict[str, Any]) -> str:
    start = annotation.get("start_index")
    end = annotation.get("end_index")
    if isinstance(start, int) and isinstance(end, int) and 0 <= start < end <= len(text):
        return text[start:end]
    return ""
