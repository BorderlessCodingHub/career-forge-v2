# CAR-29 — Branch walkthrough

**Issue:** [CAR-29 — Slice 2: /forges UI + optional email + diagnosis profile reuse](https://linear.app/career-forge-v2/issue/CAR-29/slice-2-forges-ui-optional-email-diagnosis-profile-reuse)  
**Branch:** `CAR-29-forges-ui-email-diagnosis-profile`  
**Epic / ADR:** [CAR-22](https://linear.app/career-forge-v2/issue/CAR-22) · ADR-003 (forge recovery + auth scaffold)  
**Depends on:** CAR-27 (share/resume + landing Continue) ✅  
**Status at write time:** working tree changes on branch (not yet committed / merged)

This doc explains **step by step** what this branch adds and why, in implementation order.

---

## Goal in one sentence

Polish forge recovery into **Slice 2**: rich `/forges` management, optional email store (no send), resume **conflict chooser**, and **re-forge from saved diagnosis** without a full re-interview.

---

## Acceptance (from Linear)

| Criterion | How this branch meets it |
|-----------|--------------------------|
| Rich `/forges` UI (revoke share, titles) | Rename via `PATCH /me/forges/{id}`; **Revoke share** button wired to existing revoke endpoint |
| Optional email capture post-forge (store only, no send) | `/forge/complete` email form → `PATCH /me/email`; no SMTP / Borderless send |
| Conflict chooser when resume hits existing local session with forges | `/resume/[token]` compares local `external_id` + forge count vs resume owner before `adoptSession` |
| Reusable diagnosis **result** profile for re-forge | `GET /me/profile` + `hydrateOnboardingFromProfile` → `/onboarding/edit`, or `startForgeRunFromProfile` |

**Out of scope (deferred):** Borderless send email (CAR-28 / Slice 3), mid-flight interview resume.

---

## Step 0 — Context (what already existed)

Before CAR-29, the recovery stack already had:

1. **CAR-23** — anon JWT + Bearer middleware  
2. **CAR-24** — `forge_artifacts` persisted on forge complete  
3. **CAR-25** — `GET /me/forges`, `POST /me/forges/{id}/open` (freeze-before-promote)  
4. **CAR-26** — forge SSE stream ticket  
5. **CAR-27** — share/resume tokens, landing Continue, minimal `/forges`, resume copy-once  
6. **Earlier** — confirmed diagnosis on `profiles`, `startForgeRunFromProfile` (forge from persisted profile)

CAR-29 builds **Slice 2 polish** on top of that surface. CAR-27 explicitly deferred email + conflict chooser here.

---

## Step 1 — Domain errors for email conflicts

**Modified:** `apps/backend/src/career_forge/errors.py`

| Error | Status | Use |
|-------|--------|-----|
| `ConflictError` | 409 | Email already taken by another user |
| `BadRequestError` | 400 | Empty title after strip (service-level guard) |

These sit next to existing `NotFoundError` / `GoneError` so routes stay thin and map cleanly to HTTP.

---

## Step 2 — Profile + email API (`/me/profile`, `/me/email`)

### Schemas — `schemas/me_profile.py` (new)

| Type | Role |
|------|------|
| `MeEmailUpdateRequest` | Normalize email (trim/lower), regex validate, reject `@demo.careerforge.local` |
| `MeEmailUpdateResponse` | `{ email }` |
| `MeProfileResponse` | `external_id`, optional `email`, `has_diagnosis`, `diagnosis`, `intake` |

### Service — `services/me_profile.py` (new)

**`get_me_profile`**

1. Resolve user by Bearer `external_id` (missing user → empty profile, not 404).  
2. Load `Profile` and parse confirmed diagnosis via `parse_profile_diagnosis`.  
3. Return diagnosis + intake when present; hide synthetic demo emails (`_public_email`).

**`update_me_email`**

1. `ensure_user` for the principal.  
2. Unique check → `ConflictError` if another user owns that email.  
3. Persist and return normalized email. **Store only** — no send.

### Routes — `api/me_profile.py` (new)

```text
GET  /me/profile   → MeProfileResponse
PATCH /me/email    → MeEmailUpdateResponse
```

Mounted in `api/router.py` under prefix `/me` (same tag as `me_forges`).

### Tests — `tests/test_me_profile.py` (new)

- Empty profile for fresh anon user  
- Profile with confirmed diagnosis returns `has_diagnosis` + intake  
- Email store + 409 conflict + 422 invalid address  

---

## Step 3 — Rename forge title (`PATCH /me/forges/{public_id}`)

### Schema — `schemas/forge_artifacts.py`

```text
ForgeArtifactUpdateRequest { title: str, min 1, max 200 }
```

### Service — `services/forge_artifacts.py`

**`update_forge_title`**

1. Owner lookup by `external_id` + `public_id`.  
2. Missing → `ForgeArtifactNotFoundError` (404, including other-user case).  
3. Strip title; empty → `BadRequestError`; truncate to 200; commit.

### Route — `api/me_forges.py`

```text
PATCH /me/forges/{public_id} → ForgeArtifactSummary
```

### Tests — `tests/test_me_forges.py`

- Happy path trims whitespace and list reflects new title  
- Other user → 404  

---

## Step 4 — Frontend API + contracts

**`types/contracts.ts`**

| Type | Purpose |
|------|---------|
| `ForgeShareRevokeResponse` | `{ revoked }` |
| `MeEmailUpdateResponse` | `{ email }` |
| `MeProfileResponse` | Profile payload for re-forge CTA |

**`lib/api-client.ts`**

| Helper | Endpoint |
|--------|----------|
| `revokeShareLink` | `POST /me/forges/{id}/share/revoke` (existed on BE since CAR-27) |
| `updateForgeTitle` | `PATCH /me/forges/{id}` |
| `getMyProfile` | `GET /me/profile` |
| `updateMyEmail` | `PATCH /me/email` |

`startForgeRunFromProfile` was already present (pre-CAR-29); this branch **wires it into recovery UX**.

---

## Step 5 — Diagnosis reuse helper

**New:** `apps/frontend/src/lib/profile-reuse.ts`

**`hydrateOnboardingFromProfile(profile)`**

1. Requires `profile.diagnosis`.  
2. Writes diagnosis into sessionStorage (`setStoredDiagnosis`).  
3. If intake has `goal_id` + `motivation` → also sets goal, motivation, years XP, answers.  
4. Returns `true` when edit path is viable → caller navigates to `/onboarding/edit`.  
5. Returns `false` when intake incomplete → caller falls back to `startForgeRunFromProfile()` → `/forge`.

This keeps the FE a thin hydrator; diagnosis logic stays on the backend profile record.

---

## Step 6 — Rich `/forges` UI

**Modified:** `app/(setup)/forges/page.tsx`

On load, parallel fetch:

```text
GET /me/forges  +  GET /me/profile (fail-open → null)
```

### Per-row actions (beyond CAR-27 Open / Copy share / Copy resume)

| Action | Behavior |
|--------|----------|
| **Rename** | Inline edit → `updateForgeTitle` → update list state |
| **Revoke share** | `revokeShareLink` (invalidates active share tokens) |

### Profile CTA

When `has_diagnosis`:

> **Forge again from last diagnosis** → hydrate → `/onboarding/edit`, else forge-from-profile → `/forge`

---

## Step 7 — Optional email on forge complete

**Modified:** `app/(setup)/forge/complete/page.tsx`

Beside the CAR-27 resume copy-once block:

1. Optional email input (`forge-email-input`).  
2. **Save email** → `updateMyEmail`.  
3. Copy states: idle / saving / saved / error.  
4. Explicit UX: “Saved for a future resume delivery. We do not send email yet.”

Prepares identity for CAR-28 (Borderless send) without shipping SMTP now.

---

## Step 8 — Resume conflict chooser

**Modified:** `app/(setup)/resume/[token]/page.tsx`

CAR-27 always consumed + `adoptSession` immediately. CAR-29 inserts a chooser:

```text
1. If local Bearer exists → listForges (best-effort)
2. POST /public/resume/{token}  (still consumes token)
3. Conflict if:
     localHasForges
     AND localExternalId !== session.external_id
4a. Conflict UI:
     Keep local session → /forges (no adopt)
     Switch to resume → adoptSession + open active/newest → /roadmap
4b. No conflict → adopt + open → /roadmap (same as CAR-27)
```

Phase machine:

| Phase | UI |
|-------|----|
| `working` | “Restoring your session…” |
| `conflict` | Keep local / Switch to resume (`data-testid="resume-conflict"`) |
| `done` | Redirect to `/roadmap` |
| `failed` | Link unavailable / switch failed |

**Note:** consume still runs before the chooser (token is single-use). Choosing “Keep local” preserves the local JWT but the resume token is already consumed — intentional tradeoff so the chooser cannot be used to “preview then retry” the same link.

---

## Step 9 — Landing recovery + diagnosis CTA

**Modified:** `components/recovery/LandingRecoveryGate.tsx`

On load, parallel `listForges` + `getMyProfile`.

| State | Behavior |
|-------|----------|
| Empty forges **+** diagnosis | “Welcome back” with **Forge again** / **New from scratch** |
| Empty forges, no diagnosis | `GoalPicker` (unchanged) |
| Ready (has forges) | Continue / View all / New forge + optional **Forge again** when diagnosis exists |
| New forge | `GoalPicker` |

Re-forge uses the same hydrate-or-`startForgeRunFromProfile` path as `/forges`.

---

## Step 10 — Design docs sync (ui-product-sync)

Updated to mark Slice 2 as **code wins**:

| Doc | Update |
|-----|--------|
| `PRODUCT-SOURCE-OF-TRUTH.md` | Flow, screen table, parity row for CAR-29 |
| `SCREEN-INTENT-MAP.md` | Recovery routes + Gate B hooks |
| `SCREEN-INTENT.md` | Must-match for rename/revoke/conflict/email/re-forge |
| `UI-PRINCIPLES.md` | `LandingRecoveryGate`, `profile-reuse.ts`, email store chrome |
| `UX-FLOW.md` | Return visit + resume conflict + email store |

---

## End-to-end flows

### A. Rename + revoke on `/forges`

```text
/forges
  → Rename → PATCH /me/forges/{id} → title updates in list
  → Revoke share → POST …/share/revoke
  → old /share/{token} fails for viewers
```

### B. Optional email after forge

```text
/forge/complete
  → enter email → Save
  → PATCH /me/email
  → GET /me/profile shows email
  → (no email sent)
```

### C. Resume conflict

```text
Browser A: local JWT + ≥1 forge (user X)
Open /resume/{token} owned by user Y
  → conflict chooser
  → Keep local → /forges (still user X)
  OR Switch → adopt Y → /roadmap
```

### D. Re-forge from diagnosis

```text
/ or /forges
  → Forge again from last diagnosis
  → GET /me/profile
  → hydrate → /onboarding/edit  (preferred)
  → or startForgeRunFromProfile → /forge
```

---

## File map (this branch)

### Backend (new)

| File | Purpose |
|------|---------|
| `api/me_profile.py` | `GET /me/profile`, `PATCH /me/email` |
| `schemas/me_profile.py` | Request/response + email validation |
| `services/me_profile.py` | Profile read + email store |
| `tests/test_me_profile.py` | HTTP coverage |

### Backend (modified)

| File | Change |
|------|--------|
| `api/me_forges.py` | `PATCH /me/forges/{public_id}` |
| `api/router.py` | Mount `me_profile` |
| `errors.py` | `ConflictError`, `BadRequestError` |
| `schemas/forge_artifacts.py` | `ForgeArtifactUpdateRequest` |
| `services/forge_artifacts.py` | `update_forge_title` |
| `tests/test_me_forges.py` | Title patch tests |

### Frontend (new)

| File | Purpose |
|------|---------|
| `lib/profile-reuse.ts` | Hydrate onboarding session from profile |

### Frontend (modified)

| File | Change |
|------|--------|
| `app/(setup)/forges/page.tsx` | Rename, revoke, re-forge CTA |
| `app/(setup)/forge/complete/page.tsx` | Optional email store |
| `app/(setup)/resume/[token]/page.tsx` | Conflict chooser |
| `components/recovery/LandingRecoveryGate.tsx` | Diagnosis-aware empty/ready CTAs |
| `lib/api-client.ts` | revoke / title / profile / email helpers |
| `types/contracts.ts` | CAR-29 response types |

### Design docs (modified)

`PRODUCT-SOURCE-OF-TRUTH.md`, `SCREEN-INTENT-MAP.md`, `SCREEN-INTENT.md`, `UI-PRINCIPLES.md`, `UX-FLOW.md`

---

## What this branch deliberately does *not* do

- Send email / magic-link / Borderless delivery (CAR-28)  
- Mid-flight diagnosis interview resume  
- New DB migration (uses existing `users.email` + `profiles.diagnosis`)  
- Changes to GraphExecutor / forge SSE path  
- Full English cutover of all product copy (CAR-16)

---

## Suggested verification before merge

1. Complete a forge → save optional email on `/forge/complete` → confirm `GET /me/profile` shows it  
2. On `/forges`: rename a row; revoke share; confirm old share link fails  
3. With local forges for user A, open a resume link for user B → conflict chooser appears  
4. Keep local → stay on A’s `/forges`; or Switch → land on B’s roadmap  
5. With confirmed diagnosis: landing / forges show **Forge again** → lands on edit or forge stream  

Gates before merge (repo policy): **SHIP + PASS + VERIFIED** then end-task (Linear Done + STATUS/ROADMAP).
```