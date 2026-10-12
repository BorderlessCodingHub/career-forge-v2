# ADR-009: Provider switch — OpenRouter behind one Access desk control

| Field | Value |
|-------|-------|
| **Status** | **Accepted** — grill 2026-10-11 |
| **Date** | 2026-10-11 |
| **Deciders** | Pedro Alano |
| **Linear (v2)** | Epic [CAR-134](https://linear.app/one-percent-better/issue/CAR-134) **Done** 2026-10-12 · [CAR-135](https://linear.app/one-percent-better/issue/CAR-135) guard · [CAR-136](https://linear.app/one-percent-better/issue/CAR-136) model chat · [CAR-137](https://linear.app/one-percent-better/issue/CAR-137) diagnosis pin · [CAR-138](https://linear.app/one-percent-better/issue/CAR-138) Forge search · [CAR-139](https://linear.app/one-percent-better/issue/CAR-139) Access desk. Learner error redaction is [CAR-140](https://linear.app/one-percent-better/issue/CAR-140). |
| **Glossary** | [CONTEXT.md](../../CONTEXT.md) — **Direct provider**, **Model gateway**, **Model chat**, **Provider switch**, **Run provider**, **Forge search**, **Forge source** |
| **Does not supersede** | LangChain `ChatOpenAI`, GraphExecutor, LangSmith traces on GraphRuns |

---

## Context

Model chat and Forge search both go through `langchain_openai.ChatOpenAI` and `OPENAI_API_KEY`. Forge search is a separate path: the OpenAI Responses API tool `web_search`. There is no feature-flag system. The Access desk may write operational state and is not a live kill-switch of Entitlement.

The point of the change is a reversible escape to OpenRouter, not a catalog of non-OpenAI models, not per-graph routing, and not automatic failover.

---

## Decision

Career Forge keeps LangChain. A **Provider switch** on the Access desk chooses the **Run provider** for model chat and Forge search: the **Direct provider** (OpenAI) or the **Model gateway** (OpenRouter). One switch for the whole product. No stored choice means the Direct provider.

The Access role writes it, including an Operator who holds both desks. Editor alone does not. The choice is remembered across restarts. The last write records which Operator did it and when. It does not keep a click history. Turning it on requires the Model gateway to be configured. Turning it off requires the Direct provider to be configured. A missing key after that fails the next run. It does not fall back.

A diagnosis session, a forge, and a single-shot model chat each hold one Run provider for their whole life. The switch does not change a life that has already started. The learner never sees which provider served the call. Mentor, rubric validation, and the rule-based diagnosis graph are outside model chat.

### Locked table (grill 2026-10-11)

| Topic | Decision |
|-------|----------|
| Client | Keep `ChatOpenAI`. The gateway is `https://openrouter.ai/api/v1` plus its own key. Do not replace LangChain |
| Default | Direct provider. Labs stays on OpenAI until an Operator arms the switch |
| Grain | One switch. Not per learner, not per graph, not per request |
| Where | Access desk. “Live kill-switch” stays banned for Entitlement |
| Who | Access role only |
| Diagnosis | The session captures the provider at start. Every turn uses it until the session is complete. A new session reads the switch again. An abandoned session keeps its provider if the learner returns to it |
| Forge | Captured when the forge is created. Model chat and Forge search in that forge share it |
| Tutor, mock interview | Captured when that call is created |
| Model id | Configured names stay bare (`gpt-5.4`). The gateway call prefixes `openai/`. Cost burn still groups by the bare name |
| Forge search, direct | OpenAI native `web_search` (Responses API), as today |
| Forge search, gateway | OpenRouter server tool `openrouter:web_search`, engine `auto`. Not the deprecated `:online` plugin |
| Forge source | Title, URL, and snippet. A pass with no URL fails that forge |
| Keys | Arm requires the OpenRouter key. Disarm requires the OpenAI key. A key removed later does not fall back |
| Two Operators | Last write wins. The desk shows that Operator and that time |
| Replicas | They share the stored choice |

---

## Consequences

- Two Forge search mechanisms stay in the product. The Forge source shape does not.
- A diagnosis turn is still its own GraphRun. The session, not the GraphRun, holds the Run provider.
- Cost reports must ignore the `openai/` prefix or the same model splits in two.
- Shipping the switch read on every diagnosis turn before the session pin would mix providers in one transcript. Do not do that.

## Related

- Grill 2026-10-11
- [CONTEXT.md](../../CONTEXT.md) § Model supply
