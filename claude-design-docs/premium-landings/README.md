# Premium landings

| Variant | Role | Source | Artifact |
|---------|------|--------|----------|
| **B → `/welcome`** | Canonical marketing Welcome (CAR-56) | Living SoT: `apps/frontend/src/components/marketing/welcome/` | App Router page (indexed) |
| **A** | Bake-off preview only | [`a/`](./a/) | `apps/frontend/public/premium-landings/a.html` |
| **B (frozen Vite)** | History / visual diff only — **not built** | [`b/`](./b/) | — (superseded by `/welcome`) |

Labs: `/career-forge/welcome` (canonical B) · `/career-forge/welcome/premium-a` (A preview) · `/career-forge/welcome/premium-b` **redirects → `/welcome`**.

## Contract (CAR-56 / CAR-52)

- **Welcome** is commercial Premium B in Next: Start diagnosis → `/`; BASE/PSP included + External $10–15/mo copy (no Stripe on Welcome); no apply/strategy/syllabus modals; logo wall + real mentors; Unsplash testimonials until CAR-93.
- **Premium A** remains an unlinked `noindex` HTML rewrite (CAR-41 pipeline unchanged).
- Vite `b/` stays frozen for history. Do not edit it for product changes — edit Next `marketing/welcome/` (CAR-92 honesty pass is Next only).
- No Welcome confetti. Product UI still has no confetti.

## Regenerate (A only)

```bash
make premium-landings
```

Commits overwritten HTML under `apps/frontend/public/premium-landings/a.html`.
