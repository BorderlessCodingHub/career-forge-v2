# ADR-010: Fundamentals — one reading per Goal, off the Roadmap

| Field | Value |
|-------|-------|
| **Status** | **Accepted** — grill 2026-11-22 |
| **Date** | 2026-11-22 |
| **Deciders** | Pedro Alano |
| **Glossary** | [CONTEXT.md](../../CONTEXT.md) — **Fundamentals** |
| **Supersedes** | [ADR-004](./ADR-004-canonical-skill-content.md) content unit (one piece per skill) and node attach. N:1 reuse, editorial authoring, and “not a post per forge” still stand. |

---

## Context

ADR-004 kept personalization in the roadmap and reuse in a library: one deep-dive per catalog skill, linked only when that node was in focus. The learner-facing need is different. A learner with an account should be able to read a general guide for a Goal, update after update, including a YouTube video in the body. That reading is not the roadmap she generated.

## Decision

**Fundamentals** is one published reading per LLM track / goal. Every learner of that goal gets the same text. It replaces Canonical skill content.

She opens it from the top of a screen she has already entered, with Email identity alone. A subscription is not required. It is not public, and a Node does not link to it. The page is a long article: published Goals on the left, in catalog order; the guide in the center; that guide’s sections on the right. Inside a Roadmap, the open guide is that Roadmap’s Goal. Anywhere else, it is the first published guide. Opening another Goal does not change her Roadmap.

The guide follows the locale she already chose, English or pt-BR. The two editions are the same guide; the video may differ. A missing edition shows the other language. A Goal with no edition is absent.

The text is editorial and live. A forge does not write it.

## Considered options

- Keep the per-skill lesson and add a guide beside it. Rejected: the guide replaces that lesson.
- Show only the Goal she chose. Rejected: every published Goal stays in the list.
- English only. Rejected: both product locales.
- Require a subscription. Rejected: an account is enough.
- Attach the reading to the focus Node. Rejected: the reading is not the Roadmap.

## Consequences

- The skill lesson and its link from the Node leave the product.
- Mastery checks stay on the Roadmap. This page is reading.
- A Goal written in only one locale still appears, in that locale.
