# CAR-112 — Sentry topology for Labs `/career-forge`

**Question:** For Labs under `/career-forge`, what is the **Sentry topology** for Career Forge frontend + backend?

**Snapshot (origin/main):** Next.js `14.2.x` App Router in `apps/frontend` with hardcoded `basePath: "/career-forge"` (`next.config.mjs`); FastAPI backend in `apps/backend`; Labs compose `docker-compose.prod.yml` (frontend `:13000`, backend `:18000`); preferred public surface `https://labs.borderlesscoding.com/career-forge` with same-origin Next rewrites → `API_INTERNAL_URL` (empty `NEXT_PUBLIC_*`). Alternate nginx split `/career-forge/api/` → `:18000`. No Sentry SDK in the repo today. HITL provision: [CAR-118](https://linear.app/career-forge-v2/issue/CAR-118) (“engineer-only alerting; no learner UI”).

---

## Answer

**Use two Sentry projects (Next.js + Python/FastAPI), two DSNs, one shared Labs `environment`, aligned git-SHA `release`, PII-off by default with explicit Email scrubbing, optional fixed `tunnelRoute` under the existing basePath — and engineer-only alerts in Sentry/Slack/email, never a learner-facing widget.**

Sentry’s org guidance and DSN docs treat a monolith with distinct frontend and backend languages as **two projects**, each with its own DSN. That matches this repo: Next client/server/edge vs FastAPI. One project is allowed but is not the documented best practice for FE+BE.

Labs path prefix `/career-forge` is already owned by Next `basePath`. It does **not** require a special nginx location for Sentry ingest. Optional ad-blocker tunneling is a Next rewrite (`tunnelRoute: "/sentry-tunnel"`); with `basePath`, the browser hits `/career-forge/sentry-tunnel`. Do not put the tunnel under the API rewrite prefixes or the alternate `/career-forge/api/` nginx block.

“Engineer-only” (CAR-118) means: Issues + Alerts notified to engineers (email/Slack/PagerDuty). Do **not** ship Sentry User Feedback (or similar) in the learner UI. Session Replay, if enabled later, lives in the Sentry product UI for engineers — it is not a learner surface.

---

## 1. One project vs two

### Verdict: **two projects**

| Claim | Source |
|---|---|
| Separate projects for API vs frontend client | [Projects](https://docs.sentry.io/product/projects/) — “you might have separate projects for your API server and frontend client” |
| Monolith: separate backend and frontend projects; one language per project | [Set Up Your Organization — How Many Projects Should I Create?](https://docs.sentry.io/organization/getting-started/) |
| React FE + Express BE tutorial creates **two** projects / two DSNs (monorepo or not) | [DSN explainer — One DSN Per Project](https://docs.sentry.io/concepts/key-terms/dsn-explainer/), [Create Frontend and Backend Sentry Projects](https://docs.sentry.io/product/sentry-basics/distributed-tracing/create-new-project/) |

**Recommended provision names (CAR-118):** e.g. `career-forge-frontend` (platform Next.js) and `career-forge-backend` (platform Python / FastAPI). One org, one team.

**Why not one project:** Allowed by Sentry, but mixes Next and Python issue streams, watermarks, and ownership. Distributed tracing still works across **projects**; it does not require a single project.

**Environments are not projects.** Use one `environment` tag (e.g. `labs`) on both projects so Issues can be filtered to Labs without merging FE/BE.

Source: [Projects](https://docs.sentry.io/product/projects/) — projects ≠ environments.

---

## 2. DSN env shape

### 2.1 Per project

Each project gets its own Client Key (DSN). Shape:

```
https://<PUBLIC_KEY>@o<ORG_ID>.ingest.sentry.io/<PROJECT_ID>
```

Sources: [DSN explainer](https://docs.sentry.io/concepts/key-terms/dsn-explainer/), Next/Python init snippets.

DSNs are safe to expose in client bundles (submit-only). Still keep them out of git; put Labs values in VPS `.env` / CI secrets (CAR-118: “Record DSN location for Labs env (not git)”).

### 2.2 Frontend (`@sentry/nextjs`)

Official Next manual setup: put the DSN in init files **or** use a public env var such as `NEXT_PUBLIC_SENTRY_DSN`.

Source: [Manual Setup — Initialize Sentry SDKs](https://docs.sentry.io/platforms/javascript/guides/nextjs/manual-setup/)

Labs implication (this repo):

| Variable | Where | Notes |
|---|---|---|
| `NEXT_PUBLIC_SENTRY_DSN` | Frontend **build args** (like `NEXT_PUBLIC_BACKEND_URL`) **and/or** runtime if only server reads it | Client bundle needs a public DSN; compose today bakes `NEXT_PUBLIC_*` at image build (`docker-compose.prod.yml` build `args`) |
| `SENTRY_AUTH_TOKEN` | CI only | Source map upload via `withSentryConfig` — never in the image or learner browser |
| `SENTRY_ORG` / `SENTRY_PROJECT` (or `org`/`project` in `withSentryConfig`) | CI build | Points at the **frontend** project |

This repo’s Next is **14.2 + Webpack** (not Turbopack-default Next 15+). Follow [Webpack Setup](https://docs.sentry.io/platforms/javascript/guides/nextjs/manual-setup/webpack-setup/) differences after the main manual setup; `tunnelRoute` works the same.

### 2.3 Backend (`sentry-sdk` + FastAPI)

Python SDK reads **`SENTRY_DSN`** automatically if `dsn=` is omitted. Also auto-reads `SENTRY_ENVIRONMENT`, `SENTRY_RELEASE`.

Source: [Python Options](https://docs.sentry.io/platforms/python/configuration/options/) — “Options that can be read from an environment variable (`SENTRY_DSN`, `SENTRY_ENVIRONMENT`, `SENTRY_RELEASE`) are read automatically.”

FastAPI: install `sentry-sdk`; with `fastapi` installed, FastAPI integration enables on `sentry_sdk.init(...)`.

Source: [FastAPI \| Sentry for Python](https://docs.sentry.io/platforms/python/integrations/fastapi/)

Labs implication: add `SENTRY_DSN` (backend project) to VPS `.env` and pass it through `docker-compose.prod.yml` `backend.environment` (same pattern as `LANGSMITH_API_KEY`). No `NEXT_PUBLIC_` prefix.

### 2.4 Suggested Labs env map (research recommendation)

```env
# Frontend project DSN — bake into Next image if client reporting is required
NEXT_PUBLIC_SENTRY_DSN=https://…@o….ingest.sentry.io/<fe-project-id>

# Backend project DSN — runtime only
SENTRY_DSN=https://…@o….ingest.sentry.io/<be-project-id>

# Shared triage tags (both services)
SENTRY_ENVIRONMENT=labs
SENTRY_RELEASE=<git-sha>   # align with IMAGE_TAG / BUILD_SHA / NEXT_PUBLIC_BUILD_SHA
```

Do **not** reuse one DSN for both services if following the two-project topology.

---

## 3. PII / Email identity scrubbing

Career Forge identity is email-centric (OTP / Borderless password — ADR-005 / CAR-57 / CAR-101). Topology must assume **emails must not land in Sentry by default**.

### 3.1 Python / FastAPI

- Default: SDK does **not** send PII (user ids, usernames, cookies, authorization headers, IPs) unless `send_default_pii=True`.
- FastAPI docs’ sample often shows `send_default_pii=True` for rich context — **do not copy that for Labs** if Email must stay out.
- Keep `send_default_pii=False` (or unset). Use default `EventScrubber`; extend `pii_denylist` / `denylist` for app-specific keys (`email`, `mail`, OTP fields).
- Prefer `set_user({"id": "<uuid>"})` over email; Python sensitive-data docs show hashing or internal id instead of email.
- Use `before_send` to strip `event.user.email` and scrub request bodies that carry identity payloads (`/auth/*`, OTP).

Sources:

- [FastAPI — Capturing Errors](https://docs.sentry.io/platforms/python/integrations/fastapi/) (PII excluded unless `send_default_pii`)
- [Scrubbing Sensitive Data \| Python](https://docs.sentry.io/platforms/python/data-management/sensitive-data/)
- [Data Collected \| Python](https://docs.sentry.io/platforms/python/data-management/data-collected/)

Request JSON/form is attached by FastAPI integration (excluding raw multipart uploads). Auth routes can still put emails in `request.data` → scrub with `before_send` / recursive scrubber even when `send_default_pii` is false.

### 3.2 Next.js

- Without `dataCollection` and with `sendDefaultPii` unset/`false`: conservative defaults — user identity **not** sent automatically.
- `sendDefaultPii` is **deprecated** (removal targeted at v11); prefer leaving it false, or if using `dataCollection`, explicitly set `userInfo: false` (and tighten `httpBodies` / cookies / query params).
- Official filtering example deletes `event.user.email` in `beforeSend`.
- Do **not** enable User Feedback integration if that would collect learner email in-product (see §6).

Sources:

- [Data Collected \| Next.js](https://docs.sentry.io/platforms/javascript/guides/nextjs/data-management/data-collected/)
- [Options — sendDefaultPii / dataCollection](https://docs.sentry.io/platforms/javascript/guides/nextjs/configuration/options/)
- [Filtering — beforeSend email example](https://docs.sentry.io/platforms/javascript/guides/nextjs/configuration/filtering/)
- [Scrubbing Sensitive Data \| Next.js](https://docs.sentry.io/platforms/javascript/guides/nextjs/data-management/sensitive-data/)

### 3.3 Server-side scrubbing (second layer)

Sentry UI inbound / server-side scrubbing can drop emails org-wide after ingest. SDK-side scrubbing is still required so PII never leaves the VPS when policy demands it.

Source: [Scrubbing Sensitive Data \| Python](https://docs.sentry.io/platforms/python/data-management/sensitive-data/) (SDK vs server-side vs Relay).

---

## 4. Release / environment naming

### 4.1 Environment

| Constraint | Source |
|---|---|
| Freeform string; Python default `production` | [Python Options — environment](https://docs.sentry.io/platforms/python/configuration/options/) |
| Next: defaults to `development` / `production` from packaging; set explicitly | [Next.js Options — environment](https://docs.sentry.io/platforms/javascript/guides/nextjs/configuration/options/) |
| Case-sensitive; **no spaces, newlines, or forward slashes**; max 64 chars; cannot be `"None"` | Same Next options page |
| Use environments to filter Issues / alerts | [Org setup — Define Environments](https://docs.sentry.io/organization/getting-started/) |

**Labs recommendation:** `SENTRY_ENVIRONMENT=labs` on **both** FE and BE.

Do **not** use `labs/career-forge` (slash illegal). Path prefix is deploy topology, not an environment name. App’s `ENV=production` in `.env.production.example` / compose is the **app** debug flag — keep Sentry’s tag as `labs` so Labs noise does not mix with a future dedicated prod host.

### 4.2 Release

| Platform | Mechanism |
|---|---|
| Python | `SENTRY_RELEASE` or `release=` in `init`; prefer explicit over auto-git inside Docker |
| Next | `release` in `Sentry.init` / build `release.name` in `withSentryConfig`; server also reads `SENTRY_RELEASE` |

This repo already stamps deploys with git SHA:

- CI: `NEXT_PUBLIC_BUILD_SHA=${{ github.sha }}` (`.github/workflows/deploy.yml`)
- Compose build arg → deploy badge (`docker-compose.prod.yml`)
- Rollback pins `IMAGE_TAG=<sha>` ([DEPLOY-LABS-MANUAL](../DEPLOY-LABS-MANUAL.md))

**Recommendation:** set `SENTRY_RELEASE` (and Next `release`) to the **same git SHA** as `BUILD_SHA` / `IMAGE_TAG` so FE, BE, GHCR tags, and the deploy badge correlate. Optional prefix `career-forge@<sha>` if you want human-readable package style; keep both projects identical.

Sources: [Python Options — release](https://docs.sentry.io/platforms/python/configuration/options/), [Next build — release.\*](https://docs.sentry.io/platforms/javascript/guides/nextjs/configuration/build/), [Next Options — release](https://docs.sentry.io/platforms/javascript/guides/nextjs/configuration/options/).

---

## 5. Path prefix `/career-forge` — tunnel / rewrite?

### 5.1 What Labs already does

From [DEPLOY-LABS-MANUAL](../DEPLOY-LABS-MANUAL.md) + `apps/frontend/next.config.mjs`:

| Layer | Behavior |
|---|---|
| Next `basePath` | `"/career-forge"` — all app routes and asset URLs |
| Preferred API | Browser calls `/career-forge/<api-prefix>/…`; Next `rewrites` → `http://backend:8000/…` (`API_INTERNAL_URL`) |
| nginx frontend | `location /career-forge` → `:13000` **without** stripping the prefix |
| Alternate API | `location /career-forge/api/` → `:18000/` **with** prefix strip |
| CORS | Origin is scheme+host only — path `/career-forge` never appears in `Origin` |

`API_PREFIXES` in `next.config.mjs` list product API roots (`auth`, `forge`, `diagnosis`, …) — **not** a Sentry tunnel path.

### 5.2 Does `/career-forge` need a special Sentry tunnel?

**No required tunnel for the path prefix itself.** Browser → Sentry ingest is third-party HTTPS to `*.ingest.sentry.io`. Path-based hosting does not change DSN routing.

**Optional tunnel** (ad-blocker bypass) is a Next feature:

```js
withSentryConfig(nextConfig, {
  tunnelRoute: "/sentry-tunnel", // fixed string recommended
});
```

Sources:

- [Manual Setup — Tunneling](https://docs.sentry.io/platforms/javascript/guides/nextjs/manual-setup/)
- [Build Options — tunnelRoute](https://docs.sentry.io/platforms/javascript/guides/nextjs/configuration/build/) (Next.js 11+; not for self-hosted Sentry)
- [Webpack Setup — Tunneling](https://docs.sentry.io/platforms/javascript/guides/nextjs/manual-setup/webpack-setup/) (same options; this repo’s bundler)

**With `basePath: "/career-forge"`:** configure `tunnelRoute` as `/sentry-tunnel` **without** manually prefixing `/career-forge`. Next’s rewrite `source` is basePath-aware (same rule this repo documents for API rewrites). The public URL becomes `https://labs.borderlesscoding.com/career-forge/sentry-tunnel`, served by the **frontend** container under the existing nginx `location /career-forge` block.

Do **not**:

- Add `/sentry-tunnel` to `API_PREFIXES` (that would proxy envelopes to FastAPI).
- Put the tunnel under `/career-forge/api/` (nginx strips to backend).
- Invent a second tunnel on the FastAPI service for browser events.

Backend Python SDK talks **directly** to ingest (server-side); no browser tunnel.

### 5.3 Middleware

This repo has **no** Next `middleware.ts` today. If one is added later, exclude the tunnel route from the matcher (official docs show a negative lookahead for `sentry-tunnel`).

Source: [Manual Setup — Tunneling + proxy/middleware](https://docs.sentry.io/platforms/javascript/guides/nextjs/manual-setup/)

---

## 6. Engineer-only alerting (no learner UI)

CAR-118: “Engineer-only alerting; no learner UI.”

| Surface | Learner-facing? | Labs stance |
|---|---|---|
| Sentry Issues UI | No (engineers login to sentry.io) | ✅ Use |
| Email / Slack / PagerDuty **Alerts** | No (notify engineers) | ✅ Use — [Org setup — Alert Notifications](https://docs.sentry.io/organization/getting-started/) |
| `feedbackIntegration()` User Feedback widget | **Yes** — embeddable in the app | ❌ Do not enable |
| Session Replay | No learner chrome (viewed in Sentry) | Optional later; privacy via Replay masking defaults — not required for topology |
| In-app “report a bug” Career Forge UI | Learner | Out of scope for Sentry topology; not required by CAR-112 |

Official User Feedback is explicitly an **embeddable widget** in the Next manual setup. Skipping that integration satisfies “no learner UI.” Alerts remain engineer-only.

Source: [Manual Setup — User Feedback](https://docs.sentry.io/platforms/javascript/guides/nextjs/manual-setup/)

---

## 7. Topology diagram (Labs)

```
Browser ──► https://labs.borderlesscoding.com/career-forge/*
              │
              ├─ Next (:13000)  ── Sentry FE project DSN ──► ingest.sentry.io
              │     │                (optional tunnelRoute /sentry-tunnel)
              │     └─ rewrites API_PREFIXES + /health ──► backend:8000
              │
              └─ (alternate) /career-forge/api/* ──nginx──► backend:18000

backend (:18000) ── Sentry BE project DSN ──► ingest.sentry.io

Both SDKs: environment=labs, release=<git-sha>
Alerts: Slack/email → engineers only
```

---

## Implementation notes (out of scope for CAR-112)

Research only — do **not** implement here. When an implementation issue lands:

1. CAR-118: create two projects; store DSNs in Labs env / secrets, not git.
2. Frontend: `@sentry/nextjs` + Webpack path for Next 14; `withSentryConfig`; optional `tunnelRoute: "/sentry-tunnel"`.
3. Backend: `sentry-sdk` early in FastAPI lifespan; `SENTRY_DSN` from compose.
4. PII: `send_default_pii=False` / no permissive `dataCollection` without explicit opt-outs; `before_send` strips email; never `set_user({email})`.
5. Align `SENTRY_RELEASE` with `BUILD_SHA` / deploy badge.
6. Skip User Feedback widget; configure engineer Alerts in Sentry UI.

---

## Sources (primary only)

| Doc | URL |
|---|---|
| Next.js manual setup (App Router, DSN, tunnel, feedback) | https://docs.sentry.io/platforms/javascript/guides/nextjs/manual-setup/ |
| Next.js Webpack setup (Next 14 path) | https://docs.sentry.io/platforms/javascript/guides/nextjs/manual-setup/webpack-setup/ |
| Next.js build options (`tunnelRoute`, release) | https://docs.sentry.io/platforms/javascript/guides/nextjs/configuration/build/ |
| Next.js SDK options (environment, release, sendDefaultPii/dataCollection) | https://docs.sentry.io/platforms/javascript/guides/nextjs/configuration/options/ |
| Next.js data collected | https://docs.sentry.io/platforms/javascript/guides/nextjs/data-management/data-collected/ |
| Next.js scrubbing / filtering | https://docs.sentry.io/platforms/javascript/guides/nextjs/data-management/sensitive-data/ · https://docs.sentry.io/platforms/javascript/guides/nextjs/configuration/filtering/ |
| Python FastAPI integration | https://docs.sentry.io/platforms/python/integrations/fastapi/ |
| Python options (`SENTRY_DSN` / `ENVIRONMENT` / `RELEASE`) | https://docs.sentry.io/platforms/python/configuration/options/ |
| Python sensitive data / scrubbing | https://docs.sentry.io/platforms/python/data-management/sensitive-data/ |
| DSN explainer (one DSN per project) | https://docs.sentry.io/concepts/key-terms/dsn-explainer/ |
| Org setup (how many projects, environments, alerts) | https://docs.sentry.io/organization/getting-started/ |
| Projects product overview | https://docs.sentry.io/product/projects/ |
| Create FE+BE projects (distributed tracing tutorial) | https://docs.sentry.io/product/sentry-basics/distributed-tracing/create-new-project/ |
| Labs deploy path + nginx | [docs/DEPLOY-LABS-MANUAL.md](../DEPLOY-LABS-MANUAL.md) |
| Next basePath + rewrites | `apps/frontend/next.config.mjs` |
| Prod compose ports / build SHA | `docker-compose.prod.yml`, `.github/workflows/deploy.yml` |
