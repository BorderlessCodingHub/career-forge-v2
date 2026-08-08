# ADR-004: Canonical skill content (forge references, not per-run posts)

| Field | Value |
|-------|-------|
| **Status** | **Accepted** — grill 2026-08-07 (Founder Engineer); reply to Yuri on reuse / SEO |
| **Date** | 2026-08-07 |
| **Deciders** | Pedro Alano |
| **Linear (v2)** | Product decision — implement when scheduled (not F2 blocker) |
| **Related ask** | Yuri: forge-specific detail → blog/platform; reuse vs infinite indexable posts |

---

## Context

Forge outputs are **student-specific**: three learners on `rag-engineer` can get different graphs (diagnosis, gaps, order, emphasis). That detail is valuable as teaching material, which led to a proposal to use a `teach` skill / LLM to write deep content and surface it on roadmap nodes.

Yuri’s question: if each forge is unique, do we create **infinite blog posts** (hurts platform indexation, maybe helps Google)? Is the relation **1 forge → N contents**? How do we do it?

Unconstrained “generate a post per forge run” would explode cost, QA, and URL sprawl. We need a model that keeps personalization in the **graph** and reuse in the **content library**.

---

## Decision

### 1. Content unit = catalog skill, not forge run

| Concern | Decision |
|---------|----------|
| Canonical identity | **One** published piece per `skill_id` (1:1 in the pilot) |
| Publish cardinality | **N students → 1 content** (N:1), not 1 forge → N posts |
| Student forge variance | Different graphs / node sets / priorities — **not** different permanent articles |
| Blog / SEO | Index **stable skill URLs** only; never index per-run forge artifacts as posts |

### 2. Authoring is offline / editorial

| Concern | Decision |
|---------|----------|
| Demand signal | Run **synthetic forges** for the four LLM goals; humans pick which skills deserve a deep-dive |
| Generation | Manual (optionally drafted with Cursor/`teach` **outside** the product) |
| Student path | Real-student forge **does not** create or publish content |
| Missing content | **Silence** — no placeholder, no block on forge |

### 3. Attach policy on the student graph (pilot)

| Concern | Decision |
|---------|----------|
| When to link | **Deterministic:** node is **focus** (must-have **or** diagnosis gap) **and** a canonical exists for that `skill_id` |
| LLM role | Forge still builds the graph; link attach is **rule + lookup**, not free-form “should we blog this?” |
| Later option | Optional LLM only for short “why this for you” copy — not for creating new canônicos |
| Persistence | Store **ref only** (`skill_id` / content key); UI resolves live title/URL |

### 4. Inventory and surfaces

| Concern | Decision |
|---------|----------|
| Storage (pilot) | Repo inventory, e.g. `data/canonical/{skill_id}.md` (+ frontmatter); seed → in-memory/`skill_id` lookup |
| Product surface | In-app learn page / viewer first (`/learn/{skill_id}` or equivalent) |
| Blog | **Later:** same markdown mirrored to public CMS — one source, two channels |
| `teach` skill | Authoring aid **outside** Career Forge runtime; not a forge graph or API feature in the pilot |

### 5. Explicit non-goals (this ADR)

- Generating a unique blog post (or CMS page) per forge run
- Soft-publishing draft canônicos into the public index from the student path
- Requiring 100% must-have coverage before forge works
- Postgres CMS / admin editor (revisit if non-dev editors become mandatory)

---

## Consequences

### Positive

- Answers Yuri: reuse is intentional; SEO stays bounded by the skill catalog.
- Cost and QA stay editorial, not O(students × nodes).
- Forge remains graph-first; content library grows on purpose.
- Blog can adopt the same canônicos without changing the N:1 model.

### Negative / risks

- Focus nodes without a canônico get no Borderless deep-dive until editorial catches up.
- Deterministic attach may feel less “smart” than a free LLM chooser — acceptable for pilot predictability and goldens.
- Repo-based inventory is dev-centric until a CMS is justified.

### Implementation note

This ADR is a **product/architecture lock**. Shipping inventory + attach is a **separate scheduled issue**, not an F2 gate and not required for current synthetic cost/must-have work.

---

## Related

- [V2-PLAN.md](../V2-PLAN.md) — four LLM goals; must-have coverage
- [docs/product/must-haves/](../product/must-haves/) — priority skills per goal
- Grill notes → Notion paste: [2026-08-07-canonical-content-notion.pt-BR.md](../reports/2026-08-07-canonical-content-notion.pt-BR.md)
