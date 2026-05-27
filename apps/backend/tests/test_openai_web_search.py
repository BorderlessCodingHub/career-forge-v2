"""Tests for OpenAI native web_search content block extraction."""

from __future__ import annotations

import pytest

from career_forge.ai.tools.openai_web_search import (
    WebSearchConfigurationError,
    WebSearchProviderError,
    extract_search_calls,
    extract_search_citations,
    parse_web_search_message,
)


class FakeMessage:
    def __init__(self, content_blocks: list[dict]) -> None:
        self.content_blocks = content_blocks


CONTENT_BLOCKS = [
    {
        "type": "server_tool_call",
        "name": "web_search",
        "args": {"queries": ["FastAPI official docs APIs"], "type": "search"},
        "id": "ws_123",
    },
    {
        "type": "server_tool_result",
        "tool_call_id": "ws_123",
        "status": "success",
    },
    {
        "type": "text",
        "text": "Use FastAPI docs for async routes and OpenAI docs for tool calling.",
        "annotations": [
            {
                "type": "citation",
                "title": "FastAPI",
                "url": "https://fastapi.tiangolo.com/",
                "start_index": 4,
                "end_index": 16,
            },
            {
                "type": "url_citation",
                "title": "OpenAI tools",
                "url": "https://platform.openai.com/docs/guides/tools-web-search",
                "start_index": 43,
                "end_index": 54,
            },
        ],
    },
]


def test_extract_search_calls_from_content_blocks() -> None:
    assert extract_search_calls(CONTENT_BLOCKS) == [
        {
            "id": "ws_123",
            "name": "web_search",
            "query": "FastAPI official docs APIs",
        },
    ]


def test_extract_citations_from_text_annotations() -> None:
    citations = extract_search_citations(CONTENT_BLOCKS)
    assert [source.title for source in citations] == ["FastAPI", "OpenAI tools"]
    assert citations[0].snippet == "FastAPI docs"


def test_parse_web_search_message_requires_search_call() -> None:
    with pytest.raises(WebSearchProviderError):
        parse_web_search_message(FakeMessage([CONTENT_BLOCKS[-1]]))


def test_parse_web_search_message_returns_query_summary_and_sources() -> None:
    result = parse_web_search_message(FakeMessage(CONTENT_BLOCKS))
    assert result.query == "FastAPI official docs APIs"
    assert result.summary.startswith("Use FastAPI docs")
    assert len(result.sources) == 2


def test_openai_client_fails_fast_without_api_key(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from career_forge.ai.tools.openai_web_search import OpenAiNativeWebSearchClient

    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    with pytest.raises(WebSearchConfigurationError):
        OpenAiNativeWebSearchClient(api_key="")
