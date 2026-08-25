# ADR-007: Reference viewer (`/reference`), not overlay and not `/learn`

| Field | Value |
|-------|-------|
| **Status** | **Accepted** — grill 2026-08-24 |
| **Date** | 2026-08-24 |
| **Deciders** | Pedro Alano |
| **Linear (v2)** | [CAR-85](https://linear.app/career-forge-v2/issue/CAR-85) |
| **Glossary** | [CONTEXT.md](../../CONTEXT.md) — **Reference**, **Reference viewer**, **Escape hatch**, **Forge source** |
| **Related** | [ADR-004](./ADR-004-canonical-skill-content.md) — Canonical skill content / `/learn` |

---

## Context

Node **References** (checklist title + URL) today open the host in a new tab (`NodeDrawer`). That throws the learner out of Career Forge and makes it easy to lose the Node and the `done` checkbox.

Iframe-always is a lie: many hosts (MDN, GitHub, OpenAI docs) refuse framing. Overlay-on-roadmap was the lighter alternative. `/learn` already means Canonical skill content (ADR-004), not a third-party URL.

---

## Decision

### 1. Object and job

| Concern | Decision |
|---------|----------|
| Object | **Reference** on a Node only — not Canonical skill content, not Forge sources |
| Job | Stay in Career Forge; do not use the host as primary navigation |
| Open vs done | Distinct acts. Opening never sets `done`. `done` remains a checklist command (available on the viewer) |
| Opened | Not a domain fact — do not persist clicks |

### 2. Surface

| Concern | Decision |
|---------|----------|
| Where | Dedicated page **`/reference`**, not overlay, not split, not `/learn` |
| Address | Node + Reference item (`node` + `item` query). Never `?url=` |
| Slot | One document. Switching another Reference on the same Node **replaces** the slot |
| Chrome | Node title, this item’s `done` control, list of the Node’s other References |
| Return | Explicit CTA to that Node on the Roadmap (restore drawer). Browser back is extra |
| Entry | NodeDrawer + this URL. Tutor/mentor/Forge timeline stay out of this cut |
| Invalid address | Return to Roadmap — no empty viewer, no product 404 |

### 3. Embed policy

| Concern | Decision |
|---------|----------|
| Embed | Allowlist-only. A host adapter is added only after successful embed behavior is proven; the initial allowlist is empty |
| Default | Honest source card with Reference title, hostname, available `outcome`, and a primary **Open original** action |
| Refusal | The source card replaces the preview slot instead of leaving a blank iframe. The host opens in a **new tab** |
| Proxy | **No** — do not fetch third-party HTML through Career Forge origin |
| `/learn` | Forever a different route: Canonical skill content, not this viewer |

### 4. Explicit non-goals (this ADR)

- In-product browser for arbitrary URLs
- Turning Live Forge `artifact_found` sources into the viewer
- Persist “opened” for mentor/analytics
- Overlay as the primary surface
- Unifying `/learn` and `/reference`

---

## Consequences

- Routing and identity-gate apply like the rest of the product loop; the Roadmap screen is left, the product is not.
- Browsers do not expose `X-Frame-Options`/`frame-ancestors` refusal reliably to page JavaScript. Unknown hosts therefore never enter an iframe: they render the source card. Allowlisted embeds retain the always-visible Escape hatch.
- The allowlist matches an exact domain or its subdomains. Host-specific URL rewrites belong to the corresponding proven adapter, not generic fallback logic.
- ADR-004 `/learn` stays the canônico; this page must not grow into a CMS viewer.

### Amendment — CAR-86 (2026-08-24)

CAR-86 replaces the universal best-effort iframe with allowlist-only embeds and a
source card default. It does not add backend probes, proxying, scraping,
extraction, or Reference ingestion for RAG.

---

## Related

- [CONTEXT.md](../../CONTEXT.md)
- [ADR-004](./ADR-004-canonical-skill-content.md)
