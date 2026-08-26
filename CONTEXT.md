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

### Roadmap artifact

**Node**:
One skill step on a learner's Roadmap, with status, tasks, and references.
_Avoid_: lesson, card, module, graph vertex (engineering)

**Task**:
A practice item on a Node. Completing it is a checklist act, not opening a URL.
_Avoid_: homework, assignment, reference

**Reference**:
A pointed study source on a Node (title + URL). It is a checklist item. Opening it is not the same act as marking it done. It is not Canonical skill content and not a Forge source.
_Avoid_: resource (forge-internal), link, bookmark, blog post, learn page, forge timeline source

**Reference viewer**:
The dedicated in-product page (`/reference`) that shows **one** Reference, addressed by Node + Reference item — never by the raw external URL. Entry: NodeDrawer or that URL. Not tutor, mentor, or Live Forge timeline. Chrome: Node title, this item's `done` control, and the Node's other References (switching replaces the slot). A CTA returns to that Node on the Roadmap. Opening is not `done`. Embed is best-effort; refused hosts get an Escape hatch. Bad or missing address returns the learner to the Roadmap — no empty viewer.
_Avoid_: iframe (mechanism), in-app browser, overlay as the primary surface, `/learn` (Canonical skill content), `?url=` (generic browser)

**Escape hatch**:
The control that opens the host in a new tab when embed is refused or the learner wants the real site. It does not mark the Reference done and does not replace Career Forge.
_Avoid_: top-level navigate to the host, “open in app browser”

**Forge source**:
A research hit on the Live Roadmap Forge timeline. Not a Reference until it is attached to a Node.
_Avoid_: reference, citation

**Canonical skill content**:
The one published deep-dive per catalog skill (N learners → 1 piece). Not a per-forge article and not a Node Reference.
_Avoid_: reference, forge post, blog (until a public mirror exists)

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
The billing gate for an external learner without entitlement. It blocks **starting** diagnosis and **starting** a forge. It does not lock Welcome, share, resume, choosing a goal, or a Roadmap they already have. Public Labs price for unpaid `external` (Welcome copy): USD $10–15/mo, billed in-loop after Email identity — not on `/welcome`. BASE/PSP remain included (no Stripe).
_Avoid_: OTP, login, calling the identity gate “the paywall”; blocking `/` Continue on an existing artifact; blocking the goal picker; putting Stripe on Welcome

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
Commercial Premium B landpage: convert with **Start diagnosis** into the product loop. BASE/PSP included; unpaid `external` sees USD $10–15/mo on the landpage, billed in-loop (no Stripe/email on Welcome). Apply / Strategy / Syllabus modals removed (CAR-53). Logo wall credits Borderless BASE/PSP employers, not Career Forge alumni. Mentors are Yuri Pereira and Pedro Alano. Unsplash testimonials stay until pilot quotes (CAR-93). No Welcome confetti. Does not require Email identity.
_Avoid_: treating Welcome as the identity gate or the Paywall; treating $10–15 as live checkout on the landpage; putting Stripe on Welcome; product entry (`/` — GoalPicker / recovery) as a public anonymous screen

**Welcome PLG** (`/welcome/plg`):
EN product-led exploration (Granola rhythm). Same CTA → `/`. Direct URL only — do not replace `/welcome`.
_Avoid_: linking PLG from canonical Welcome as a chooser

**Premium A** (`/welcome/premium-a`):
Unlinked bake-off HTML preview (`noindex`). Not the funnel. Legacy `/welcome/premium-b` redirects → `/welcome`.
_Avoid_: resurrecting Premium B HTML as a second public surface
