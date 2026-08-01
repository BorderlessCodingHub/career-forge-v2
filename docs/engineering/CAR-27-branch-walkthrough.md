# CAR-27 — Branch walkthrough

**Issue:** [CAR-27 — Share + resume tokens + landing Continue](https://linear.app/career-forge-v2/issue/CAR-27/share-resume-tokens-landing-continue)  
**Branch:** `CAR-27-share-resume-tokens-landing-continue`  
**Epic / ADR:** [CAR-22](https://linear.app/career-forge-v2/issue/CAR-22) · ADR-003 (forge recovery + auth scaffold)  
**Depends on:** CAR-25 (list/open forges + freeze-before-promote) ✅  
**Status at write time:** working tree changes on branch (not yet merged)

This doc explains **step by step** what this branch adds and why, in implementation order.

---

## Goal in one sentence

Let returning users **continue** a saved forge, and recover via **share** (read-only, no session steal) or **resume** (single-use deep-link that adopts the owner JWT).

---

## Acceptance (from Linear)

| Criterion | How this branch meets it |
|-----------|--------------------------|
| Share opens roadmap read-only without adopting `user_id` | `GET /public/share/{token}` → snapshot only; FE never calls `adoptSession` |
| Resume sets JWT/session to owner; second use fails | `POST /public/resume/{token}` mints owner JWT + sets `consumed_at`; reuse → `410 Gone` |
| Landing Continue works after tab close (same browser + JWT) | `/` → `LandingRecoveryGate` → `GET /me/forges` → open active/newest |
| Resume link recovers after clear if user saved link | Resume consume writes owner JWT to localStorage, then opens forge |

**Out of scope (deferred to CAR-29):** email capture, polished conflict chooser.

---

## Step 0 — Context (what already existed)

Before CAR-27, the recovery stack already had:

1. **CAR-23** — anon JWT + Bearer middleware  
2. **CAR-24** — `forge_artifacts` persisted on forge complete  
3. **CAR-25** — `GET /me/forges`, `POST /me/forges/{id}/open` (freeze-before-promote)  
4. **CAR-26** — forge SSE stream ticket (Bearer → query ticket)

CAR-27 builds **tokens + landing UX** on top of that list/open surface.

---

## Step 1 — Persist access tokens in Postgres

**New migration:** `apps/backend/alembic/versions/009_forge_access_tokens.py`

Creates table `forge_access_tokens`:

| Column | Role |
|--------|------|
| `artifact_id` | FK → `forge_artifacts.id` (CASCADE delete) |
| `role` | `'share'` or `'resume'` (check constraint) |
| `token_hash` | SHA-256 of the raw URL token (raw token never stored) |
| `expires_at` | set for resume (~7d); `NULL` for share |
| `consumed_at` | set when resume is used once |
| `revoked_at` | set when share links are revoked |

Indexes on `(artifact_id, role)` and `token_hash` (unique).

**New model:** `db/models/forge_access_token.py` (`ForgeAccessToken`)  
**Wired:** `db/models/__init__.py` + relationship on `ForgeArtifact.access_tokens`.

---

## Step 2 — Token service (mint / resolve / consume / revoke)

**New:** `services/forge_access_tokens.py`

### Share

1. Owner authenticates (Bearer).  
2. `create_share_token` generates `secrets.token_urlsafe(32)`, stores **hash only**, `expires_at=None`.  
3. Returns `{ token, path: "/share/{token}" }`.  
4. `resolve_share` looks up hash + role `share`, rejects if revoked → builds read-only roadmap from artifact snapshot.  
5. `revoke_share_tokens` stamps `revoked_at` on all active share rows for that artifact.

### Resume

1. `create_resume_token` same mint flow, but `expires_at = now + jwt_resume_ttl_days` (default **7**, from `config.py`).  
2. `consume_resume`:
   - missing/revoked → 404  
   - already `consumed_at` → **410 Gone**  
   - past `expires_at` → **410 Gone**  
   - else mark consumed, mint anon JWT for **owner** `external_id`, return `{ access_token, token_type, external_id }`.

### Security notes

- URL carries the **raw** token; DB stores **hash** only.  
- Share never returns or writes owner identity.  
- Resume is intentionally single-use + TTL.

---

## Step 3 — Read-only roadmap from snapshot (no promote)

**Changed:** `services/forge_artifacts.py` → new `roadmap_from_snapshot(artifact)`

Builds a `RoadmapResponse` from `artifact.snapshot` + catalog track metadata.

Used by share resolution so viewers see the saved graph **without** calling freeze-before-promote / mutating the owner’s active graph.

---

## Step 4 — HTTP API surface

### Authenticated mint (Bearer) — extends `api/me_forges.py`

| Method | Path | Purpose |
|--------|------|---------|
| `POST` | `/me/forges/{public_id}/share` | Mint share link |
| `POST` | `/me/forges/{public_id}/resume` | Mint resume link |
| `POST` | `/me/forges/{public_id}/share/revoke` | Revoke all share tokens for artifact |

### Public deep-links — new `api/forge_links.py`

| Method | Path | Purpose |
|--------|------|---------|
| `GET` | `/public/share/{token}` | Read-only roadmap |
| `POST` | `/public/resume/{token}` | Consume resume → owner JWT |

**Why `/public/...`?** Comment in `forge_links.py`: on Labs same-origin, Next filesystem routes own `/share` and `/resume`. API uses `/public/*` so Next rewrites do not collide with app pages. Frontend still shows user-facing paths `/share/[token]` and `/resume/[token]`.

**Router:** `api/router.py` mounts `forge_links` under tags `forge-links`.

### Auth middleware — `auth/middleware.py`

Adds public path regexes:

- `/public/share/{token}`
- `/public/resume/{token}`

Token validity is enforced in handlers (same pattern as forge SSE ticket exemption in CAR-26).

### Errors — `errors.py`

New `GoneError` → HTTP **410** (consumed / expired resume).

### Schemas — `schemas/forge_access_tokens.py`

- `ForgeLinkMintResponse` (`token`, `path`)  
- `ForgeShareRevokeResponse` (`revoked`)  
- `ResumeConsumeResponse` (`access_token`, `token_type`, `external_id`)

### Config — `config.py`

```text
jwt_resume_ttl_days: int = 7
```

---

## Step 5 — Backend tests

**New:** `apps/backend/tests/test_forge_access_tokens.py`

Covers mint/resolve/consume/revoke behaviors and the single-use / expiry failure modes expected by acceptance.

---

## Step 6 — Frontend API client + session adopt

**Changed:** `apps/frontend/src/lib/api-client.ts`

| Helper | Calls |
|--------|-------|
| `listForges` | `GET /me/forges` |
| `openForge` | `POST /me/forges/{id}/open` |
| `mintShareLink` / `mintResumeLink` | Bearer mint endpoints |
| `fetchSharedForge` | `GET /public/share/{token}` (no auth required) |
| `consumeResumeLink` | `POST /public/resume/{token}` |
| `absoluteAppUrl` | Builds copyable URLs with `NEXT_PUBLIC_BASE_PATH` |

**Changed:** `user-session.ts` → `adoptSession(accessToken, externalId)` overwrites local JWT (used only by resume flow).

**Changed:** `types/contracts.ts` — `ForgeArtifactSummary`, list/mint/resume response types.

**Changed:** `next.config.mjs` — rewrite prefixes include `auth`, `me`, `public` so browser can hit those API paths through the Next proxy.

---

## Step 7 — Landing recovery gate

**New:** `components/recovery/LandingRecoveryGate.tsx`  
**Changed:** `(setup)/page.tsx` — `/` renders the gate instead of bare `GoalPicker`.

Flow:

```text
/ → GET /me/forges
  ├─ 0 items     → GoalPicker (unchanged happy path)
  ├─ ≥1 items    → "Welcome back" · Continue / View all / New forge
  └─ API error   → fail-open message + "Start new forge" → GoalPicker
```

- **Continue** → pick `is_active` else newest → `openForge` → `/roadmap`  
- **View all** → `/forges`  
- **New forge** → local state flips to GoalPicker without leaving `/`

`data-screen="landing-recovery"` for product/QA hooks.

---

## Step 8 — Minimal `/forges` list

**New:** `(setup)/forges/page.tsx` · `data-screen="forges-list"`

Per artifact row:

- **Open** → freeze-before-promote + navigate `/roadmap`  
- **Copy share** → mint + clipboard absolute URL  
- **Copy resume** → mint + clipboard absolute URL  

MVP chrome only; polish deferred to CAR-29.

---

## Step 9 — Share page (read-only)

**New:** `(artifact)/share/[token]/page.tsx` · `data-screen="share-readonly"`

1. `fetchSharedForge(token)`  
2. Render node list from snapshot  
3. Explicit copy: does **not** adopt owner session  
4. Link home to start own forge  

No `adoptSession`. No Bearer required for the public GET.

---

## Step 10 — Resume page (session reattach)

**New:** `(setup)/resume/[token]/page.tsx` · `data-screen="resume-consume"`

1. `consumeResumeLink(token)`  
2. `adoptSession(access_token, external_id)`  
3. `listForges` + `openForge` (active/newest)  
4. `router.replace("/roadmap")`  
5. On failure (reuse/expiry/missing) → clear error UI + home CTA  

Second visit with same token fails at the API (410) after first successful consume.

---

## Step 11 — Post-forge complete: resume link once

**Changed:** `(setup)/forge/complete/page.tsx`

After graph reveal finishes:

1. Mint resume for active/newest artifact **once** (`resumeMintedRef`)  
2. Show absolute URL + copy button  
3. Copy explains single-use + ~7d TTL (“you will not see this link again on this screen”)

Satisfies: “Post-forge complete: show resume link copy once.”

---

## Step 12 — Product / design docs sync

Updated to document recovery surfaces (CAR-27):

- `claude-design-docs/PRODUCT-SOURCE-OF-TRUTH.md` — implementation note row  
- `claude-design-docs/SCREEN-INTENT-MAP.md` — routes 1b–1d  
- `claude-design-docs/SCREEN-INTENT.md` — recovery constraints  
- `claude-design-docs/UX-FLOW.md` — return visit + deep-links + forge complete resume copy  

---

## End-to-end flows (mental model)

### A. Same browser, JWT still present

```text
Forge complete → artifact saved (CAR-24)
  → user closes tab
  → opens /
  → LandingRecoveryGate sees ≥1 forge
  → Continue → openForge → /roadmap
```

### B. Cleared storage, but user saved resume URL

```text
/resume/{token}
  → POST /public/resume/{token}
  → adopt owner JWT
  → open forge → /roadmap
  → second open of same URL → 410
```

### C. Share with someone else

```text
Owner: Copy share on /forges
Viewer: /share/{token}
  → read-only snapshot
  → viewer’s local JWT unchanged
```

---

## File map (this branch)

### Backend (new)

| File | Purpose |
|------|---------|
| `alembic/versions/009_forge_access_tokens.py` | Schema |
| `db/models/forge_access_token.py` | ORM |
| `schemas/forge_access_tokens.py` | Pydantic |
| `services/forge_access_tokens.py` | Mint / resolve / consume / revoke |
| `api/forge_links.py` | Public share/resume routes |
| `tests/test_forge_access_tokens.py` | Coverage |

### Backend (modified)

| File | Change |
|------|--------|
| `api/me_forges.py` | Mint + revoke endpoints |
| `api/router.py` | Mount forge_links |
| `auth/middleware.py` | Public `/public/share|resume` |
| `config.py` | `jwt_resume_ttl_days` |
| `db/models/__init__.py` | Export model |
| `db/models/forge_artifact.py` | `access_tokens` relationship |
| `errors.py` | `GoneError` (410) |
| `services/forge_artifacts.py` | `roadmap_from_snapshot` |

### Frontend (new)

| File | Purpose |
|------|---------|
| `components/recovery/LandingRecoveryGate.tsx` | Landing Continue gate |
| `components/recovery/index.ts` | Barrel |
| `app/(setup)/forges/page.tsx` | List + copy links |
| `app/(artifact)/share/[token]/page.tsx` | Read-only share |
| `app/(setup)/resume/[token]/page.tsx` | Consume resume |

### Frontend (modified)

| File | Change |
|------|--------|
| `app/(setup)/page.tsx` | Use recovery gate |
| `app/(setup)/forge/complete/page.tsx` | Resume copy-once |
| `lib/api-client.ts` | Forge + link helpers |
| `lib/user-session.ts` | `adoptSession` |
| `types/contracts.ts` | CAR-27 types |
| `next.config.mjs` | Rewrite `auth` / `me` / `public` |

### Design docs (modified)

`PRODUCT-SOURCE-OF-TRUTH.md`, `SCREEN-INTENT-MAP.md`, `SCREEN-INTENT.md`, `UX-FLOW.md`

---

## What this branch deliberately does *not* do

- Email capture / magic-link identity (CAR-29)  
- Polished multi-session conflict chooser (CAR-29)  
- Rich share UI beyond a functional node list  
- Changing forge SSE / GraphExecutor paths (those stay CAR-26 / AI layer)

---

## Suggested verification after merge

1. Complete a forge → copy resume link from `/forge/complete`  
2. Clear site data → open resume URL → land on `/roadmap` as owner  
3. Reopen same resume URL → expect failure (410 / “already used”)  
4. Mint share → open in private window → read-only, no session adopt  
5. Reload `/` with existing JWT + artifacts → Continue / View all / New forge  

Gates before merge (repo policy): **SHIP + PASS + VERIFIED** then end-task (Linear Done + STATUS/ROADMAP).
