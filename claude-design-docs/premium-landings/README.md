# Premium landings

| Variant | Role | Source | Artifact |
|---------|------|--------|----------|
| **B → `/welcome`** | Canonical marketing Welcome (CAR-56) | Living SoT: `apps/frontend/src/components/marketing/welcome/` | App Router page (indexed) |
| **A** | Bake-off preview only | [`a/`](./a/) | `apps/frontend/public/premium-landings/a.html` |
| **B (frozen Vite)** | History / visual diff only — **not built** | [`b/`](./b/) | — (superseded by `/welcome`) |

Labs: `/career-forge/welcome` (canonical B) · `/career-forge/welcome/premium-a` (A preview) · `/career-forge/welcome/premium-b` **redirects → `/welcome`**.

## Contract (CAR-56 / CAR-52)

- **Welcome** is commercial Premium B in Next: Start diagnosis → `/`; pricing/apply/syllabus/strategy = scenery modals; fake proof until CAR-53; waitlist/checkout still not runtime.
- **Premium A** remains an unlinked `noindex` HTML rewrite (CAR-41 pipeline unchanged).
- Vite `b/` stays frozen for history. Do not edit it for product changes — edit Next `marketing/welcome/` (CAR-53 honesty pass edits Next only).
- Welcome-scoped confetti allowed in ApplicationModal only. Product UI still has no confetti.

## Regenerate (A only)

```bash
make premium-landings
```

Commits overwritten HTML under `apps/frontend/public/premium-landings/a.html`.
