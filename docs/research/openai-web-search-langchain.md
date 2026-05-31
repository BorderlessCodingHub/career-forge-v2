# Research — OpenAI Native Web Search with LangChain

> Context: HAC-54 (`research_enrich`) must use OpenAI native web search, not Tavily or a hand-rolled search API adapter.

## Decision

Use OpenAI's native `web_search` server-side tool through LangChain's `ChatOpenAI` / `init_chat_model` integration. Do not implement a custom HTTP client for third-party search providers unless the team explicitly decides to change provider.

Before adding external tooling, ask:

1. Which provider should own search?
2. Should search be mandatory (`tool_choice` required) or optional (`auto`)?
3. Which model should run search?
4. Do we need live web access or cache/offline mode?
5. What exact source shape should the frontend render?

## Sources Read

- OpenAI Responses API migration guide: `https://developers.openai.com/api/docs/guides/migrate-to-responses`
- OpenAI web search guide: `https://developers.openai.com/api/docs/guides/tools-web-search?api-mode=chat`
- LangChain Python `ChatOpenAI` integration: `https://docs.langchain.com/oss/python/integrations/chat/openai`
- LangChain model server-side tool use: `https://docs.langchain.com/oss/python/langchain/models#server-side-tool-use`
- LangChain docs search result: `ContentBlock.Tools.ServerToolResult`, `Standard content blocks`, and `Server-side tool use`

## Current OpenAI Shape

OpenAI recommends Responses API `tools=[{"type": "web_search"}]` for new integrations. Legacy `web_search_preview` exists, and LangChain docs still show it in some OpenAI integration examples, but LangChain model docs also show `{"type": "web_search"}` as the provider-agnostic server-side tool path.

Important behavior:

- The model executes web search server-side in a single turn.
- There are no `ToolMessage`s to manually feed back, unlike client-side tool calling.
- LangChain exposes provider-normalized results via `AIMessage.content_blocks`.
- The response includes:
  - `server_tool_call` blocks, including the query the model executed.
  - `server_tool_result` blocks, including status.
  - `text` blocks, including grounded text and `annotations`.

LangChain example shape:

```python
[
    {
        "type": "server_tool_call",
        "name": "web_search",
        "args": {"query": "positive news stories today", "type": "search"},
        "id": "ws_abc123",
    },
    {
        "type": "server_tool_result",
        "tool_call_id": "ws_abc123",
        "status": "success",
    },
    {
        "type": "text",
        "text": "Here are some positive news stories from today...",
        "annotations": [
            {
                "type": "citation",
                "title": "article title",
                "url": "...",
                "start_index": 337,
                "end_index": 410,
            }
        ],
    },
]
```

OpenAI Responses raw shape uses `url_citation` annotations on `output_text` blocks. LangChain normalizes these into `citation` annotations in `content_blocks`.

## Extraction Strategy

Do not assume provider-specific fields outside the documented content blocks. Use small parsing helpers over `response.content_blocks`:

```python
def extract_search_calls(content_blocks: list[dict]) -> list[dict]:
    return [
        {
            "id": block.get("id"),
            "query": (block.get("args") or {}).get("query"),
            "name": block.get("name"),
        }
        for block in content_blocks
        if block.get("type") == "server_tool_call"
        and block.get("name") == "web_search"
    ]


def extract_search_citations(content_blocks: list[dict]) -> list[dict]:
    citations = []
    for block in content_blocks:
        if block.get("type") != "text":
            continue
        text = block.get("text") or ""
        for annotation in block.get("annotations") or []:
            if annotation.get("type") not in {"citation", "url_citation"}:
                continue
            start = annotation.get("start_index")
            end = annotation.get("end_index")
            cited_text = text[start:end] if isinstance(start, int) and isinstance(end, int) else ""
            citations.append(
                {
                    "title": annotation.get("title") or annotation.get("url") or "Fonte",
                    "url": annotation.get("url") or "",
                    "snippet": cited_text,
                },
            )
    return citations
```

Use `response.text` only for the grounded answer summary, not for source extraction.

## Proposed HAC-54 Runtime Contract

Keep the existing Forge SSE timeline, but make `research_enrich` emit native-search artifacts:

```ts
type ResearchSource = {
  title: string;
  url: string;
  snippet?: string;
};

type RoadmapForgeEvent =
  | { type: "reasoning_delta"; step: "research_enrich"; text: string }
  | {
      type: "artifact_found";
      label: string;
      detail: string;
      sources?: ResearchSource[];
    };
```

Mapping:

- `server_tool_call.args.query` or `server_tool_call.args.queries[]` → internal research state for planner context, not a UI field
- Citation annotations → `artifact_found.sources[]`
- `text` block summary → `artifact_found.detail` or a preceding/following `reasoning_delta`

## Suggested Implementation Plan

1. Add `career_forge/ai/tools/openai_web_search.py`.
2. Use `langchain_openai.ChatOpenAI` with `model=os.getenv("FORGE_SEARCH_MODEL", "gpt-5.4")`.
3. Pass `tools=[{"type": "web_search"}]` as LangChain invocation parameters (or `bind(..., tools=[...])`), with `tool_choice="required"` for mandatory search.
4. Invoke with a prompt that asks for study sources for the selected goal, gaps, and first priorities.
5. Parse only `AIMessage.content_blocks`.
6. Convert citations into `artifact_found.sources`.
7. Fail fast if `OPENAI_API_KEY` is absent.
8. Tests should fake an `AIMessage`-like object with `content_blocks`, not mock HTTP response fields.

## UX Notes

Render search as "Live search" rows in the forge timeline:

- Show 2-3 source cards with title, URL hostname, and snippet/cited span.
- Keep raw queries out of the UI unless explicitly debugging.
- Avoid displaying raw tool result JSON.
- Keep graph hidden until `graph_ready`.

This gives the demo the "AI is researching now" moment without leaking implementation details.

## Follow-up Research — Looping and Streaming

OpenAI Responses `web_search` is model-directed. With `tool_choice="required"` the model must use a tool, and with reasoning models it can perform `search`, plus deeper `open_page` / `find_in_page` actions when supported. For long-running multi-search tasks, OpenAI documents background/WebSocket/`previous_response_id` patterns.

For this hackathon UX, use an application-level loop first:

1. Generate 2-3 focused research prompts from `LearnerForgeContext`.
2. Call `ChatOpenAI(..., use_responses_api=True)` with `tools=[{"type": "web_search"}]`, `tool_choice="required"` for each focus.
3. Emit one `artifact_found` per completed search result immediately.
4. Build a structured `StudyPlan`.
5. Run a mini evaluator (`FORGE_EVALUATOR_MODEL`) over the plan.
6. If evaluator returns `revise`, pass `previous_plan + evaluator_feedback + research_state + learner_context` back into the planner and retry up to a small iteration cap.
7. Keep sources stream-only for HAC-54; persist final plan/graph in HAC-55.

This produces visible live feedback now without adopting WebSocket mode or background polling.

## Open Questions Before Coding

- Should search be forced? If yes, use `tool_choice`/model invocation settings that require the web tool, rather than hoping the model chooses it.
- Should we use `web_search` now and ignore older `web_search_preview`, or pin to the exact LangChain version's supported built-in tool list?
- Which domains should be preferred for learning references (official docs, MDN, FastAPI, OpenAI, roadmap.sh, etc.)?
- Should sources be persisted with the generated graph in HAC-55, or only streamed in HAC-54?
