# Career Forge Frontend

Domain-oriented Next.js 14 App Router under `src/`.

## Layers

| Layer | Path | Responsibility |
|-------|------|----------------|
| **app** | `src/app/` | Routes — `(setup)` goal/onboarding/forge, `(artifact)` roadmap |
| **components/ui** | primitives | Button, Card, Pill, Drawer |
| **components/layout** | shells | AppShell, ArtifactShell, BorderlessShell |
| **components/roadmap** | artifact UI | VerticalSpine, SkillNode, NodeDrawer |
| **components/forge** | streaming UI | ForgeTimeline, ForgeStep, StreamReveal |
| **components/diagnosis** | onboarding | PillRound, EditableDiagnosis |
| **components/streaming** | hooks | useForgeStream, StreamEventList |
| **lib** | API + SSE | `api-client.ts`, `sse.ts` |
| **types** | contracts | Mirror of backend HAC-7 schemas |

## Run locally

```bash
cd apps/frontend
pnpm install
pnpm dev
```

Vercel project root: `apps/frontend` (see repo `vercel.json`).

Design tokens: Borderless palette in `tailwind.config.ts` + `globals.css` (from `claude-design-docs/design-tokens.md`).
