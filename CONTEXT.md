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
One of four destination paths: RAG engineer, agent engineer, LLM evals, fine-tuning.
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

### Marketing surface

**Welcome** (`/welcome`):
Commercial Premium B landpage (CAR-56): convert with **Start diagnosis** → `/`; pricing / apply / syllabus / strategy = scenery modals; fake proof until CAR-53; waitlist/checkout still not runtime. Welcome-scoped confetti allowed in ApplicationModal; product UI still none.
_Avoid_: treating pricing theater as live checkout; product entry (`/` — GoalPicker / recovery)

**Welcome PLG** (`/welcome/plg`):
EN product-led exploration (Granola rhythm). Same CTA → `/`. Direct URL only — do not replace `/welcome`.
_Avoid_: linking PLG from canonical Welcome as a chooser

**Premium A** (`/welcome/premium-a`):
Unlinked bake-off HTML preview (`noindex`). Not the funnel. Legacy `/welcome/premium-b` redirects → `/welcome`.
_Avoid_: resurrecting Premium B HTML as a second public surface
