# Career Forge

Adaptive learning context for Borderless BASE & PSP learners: diagnose starting point, forge a live roadmap, validate mastery before progression.

## Language

### Product & audience

**Career Forge**:
The product — an adaptive learning system that diagnoses, forges a live roadmap, and validates mastery.
_Avoid_: LMS, course catalog, bootcamp, career coach app

**BASE & PSP learner**:
The only intended audience: Borderless BASE and PSP students across the experience spectrum.
_Avoid_: career changer (generic), general public, “anyone learning AI”

**LLM track / goal**:
One of four destination paths: RAG engineer, agent engineer, LLM evals, fine-tuning. Choosing a track requires Email identity, not Entitlement.
_Avoid_: Backend / Frontend / Data (legacy prototype goals)

### Loop

**Diagnosis**:
The multi-turn interview that maps where the learner is before any roadmap is forged.
_Avoid_: onboarding quiz, static form, CTRR (internal rubric name — ban from marketing)

**Live Roadmap Forge**:
The named P0 feature: watching the roadmap take shape in real time for this learner.
_Avoid_: syllabus generator, PDF plan, “AI curriculum”

**Forge** (verb):
To generate that live roadmap for a chosen goal.
_Avoid_: build course, generate syllabus

**Roadmap**:
The adaptive skill path artifact the learner follows and that reacts to evidence.
_Avoid_: trail (except metaphor inside Live Roadmap Forge copy), skill graph (engineering), SSE

**Validate mastery** / **mastery validation**:
AI-backed checks that confirm what the learner can do; passage depends on evidence, not XP years.
_Avoid_: quiz for grades, certificate exam, job guarantee

**Product loop**:
Goal → diagnosis → forge → roadmap → validate → report. Requires Email identity. Not Welcome, share, or resume.
_Avoid_: calling Welcome part of the loop; “the app” as if marketing were inside it

### Identity

**Anonymous session**:
A learner presence without Email identity. It cannot enter the product loop.
_Avoid_: unauthenticated, logged out, guest, “no auth”

**Email identity**:
Proof that the learner owns an email address, established by Career Forge OTP. This is what “authenticate” means in product talk.
_Avoid_: authenticate (overloaded), login (generic), Borderless account, membership, Operator OTP

**Sign out** (UI: *Sair*):
Ends Email identity on this browser. Clears all client state and revokes the access JWT server-side. Returns the learner to the Identity gate — not “logged out of Borderless.”
_Avoid_: logged out, logout (generic), deauthenticate, Borderless sign-out

**Identity gate**:
The rule that the product loop requires Email identity before any step in it. Welcome, share, and resume stay outside. Not billing.
_Avoid_: paywall, post-forge upgrade, Welcome login, entry-gate on marketing

**Membership**:
Soft label of the learner as BASE, PSP, or external to Borderless. Not identity and not entitlement.
_Avoid_: login, account type, “authenticated as BASE”

**Entitlement**:
The right to start diagnosis and to forge. Entitled BASE/PSP membership grants it without billing. External requires billing first — there is no free forge and no unpaid diagnosis. An existing Roadmap is not withheld for lack of entitlement.
_Avoid_: authentication, one free forge, ransoming artifacts

**Paywall**:
The billing gate for an external learner without entitlement. It blocks **starting** diagnosis and **starting** a forge. It does not lock Welcome, share, resume, choosing a goal, or a Roadmap they already have.
_Avoid_: OTP, login, calling the identity gate “the paywall”; blocking `/` Continue on an existing artifact; blocking the goal picker

### Operator console

**Operator**:
A Borderless person who uses the Operator console. Not a learner and not a mentor.
_Avoid_: admin, staff (diagnosis XP persona), editor (that is a role)

**Operator identity**:
Proof the Operator belongs on the Operator console, established by Operator OTP. Distinct from Email identity even when the email is the same — two identities, never one session. Not Membership and not Entitlement.
_Avoid_: login, admin password, “authenticate as staff”, learner OTP plus allowlist

**Operator OTP**:
The Career Forge OTP namespace that proves Operator identity. Separate from the OTP that proves Email identity.
_Avoid_: learner OTP, magic link, shared secret

**Operator console**:
Staff-only surface outside the product loop: Access desk + Content desk, one Operator identity.
_Avoid_: admin panel, dashboard OPS, Staff console

**Access desk**:
The Operator console desk that writes pilot access (Membership stub and billing entitlement) and shows cost burn read-only, plus Access cards.
_Avoid_: user admin, impersonation, live kill-switch

**Content desk**:
The Operator console desk for canonical skill metadata (published, title, URL) in Postgres. Markdown body stays in git. Not a CMS.
_Avoid_: admin editor, NocoDB, Postgres CMS

**Access card**:
Read-only lookup of a learner by email: Email identity, Membership, Entitlement, forge count this month. Not a Roadmap or diagnosis.
_Avoid_: learner file, user admin, mentor view

**Editor**:
The Operator console role that may use the Content desk. An Operator may hold Access, Editor, or both.
_Avoid_: CMS author, admin

### Marketing surface

**Welcome** (`/welcome`):
Commercial Premium B landpage (CAR-56): convert with **Start diagnosis** into the product loop; pricing / apply / syllabus / strategy = scenery modals; fake proof until CAR-53; waitlist/checkout still not runtime on Welcome. Welcome-scoped confetti allowed in ApplicationModal; product UI still none. Does not require Email identity. Runtime Paywall lives in the product loop; Welcome may contradict it until the landpage is made honest — that dissonance is accepted.
_Avoid_: treating Welcome as the identity gate or the Paywall; treating pricing theater as live checkout; putting Stripe on Welcome; product entry (`/` — GoalPicker / recovery) as a public anonymous screen

**Welcome PLG** (`/welcome/plg`):
EN product-led exploration (Granola rhythm). Same CTA → `/`. Direct URL only — do not replace `/welcome`.
_Avoid_: linking PLG from canonical Welcome as a chooser

**Premium A** (`/welcome/premium-a`):
Unlinked bake-off HTML preview (`noindex`). Not the funnel. Legacy `/welcome/premium-b` redirects → `/welcome`.
_Avoid_: resurrecting Premium B HTML as a second public surface
