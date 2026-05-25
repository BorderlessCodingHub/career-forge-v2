# Claude Design Brief — Career OS (Soft Push)

> **Como usar este doc:** cole no chat do Claude Design (`claude.ai/design`).  
> **Estratégia:** gerar **1 tela por prompt** (não peça 6 telas de uma vez). Depois peça navegação entre elas. Exporte como **standalone HTML** e traga de volta para implementação no Next.js.

---

## 0. Contexto do produto (cole no início de TODO prompt)

Design a web app called **Career OS** — an AI-native learning system for people transitioning into tech careers.

**Positioning:** Inspired by [roadmap.sh](https://roadmap.sh) minimalism, but evolved into a **living skill graph** that adapts to each person's dream career and starting point — not a generic static checklist.

**Core philosophy:** *Mastery before progression* (Alpha School). The user cannot mark topics as "done" — they must **prove learning** through an AI interview.

**Audience:** Career changers (18–35), often overwhelmed by huge roadmaps. Secondary audience: Borderless mentors who need learning evidence.

**Visual tone:**
- Minimal, calm, confident — like roadmap.sh
- NOT a generic LMS, NOT flashy gamification
- Feels like "this AI understands who I'm becoming"
- Dark mode preferred (dev-friendly)
- Accent: indigo/violet (#6366F1) + subtle green for mastery, amber for review

**Platform:** Desktop-first web app (1280px). Mobile responsive is nice-to-have, not priority.

**Language:** Portuguese (Brazil) for all UI copy.

---

## 1. Design system tokens (defina antes ou no primeiro prompt)

```
Colors:
- bg: #0B0F19 (deep navy)
- surface: #131825
- surface-elevated: #1A2236
- border: #2A3348
- text-primary: #F1F5F9
- text-secondary: #94A3B8
- accent: #6366F1 (indigo)
- success/mastery: #22C55E
- warning/review: #F59E0B
- locked: #475569
- evidence: #38BDF8

Typography:
- Font: Inter or Geist Sans
- Headings: semibold, tight tracking
- Body: regular, relaxed line-height

Spacing: 4px grid (4, 8, 12, 16, 24, 32, 48)

Radius: 8px cards, 12px modals, full pills for badges

Components to reuse across all screens:
- SkillNodeCard (status variants)
- EvidenceBadge
- ScoreRing (0–100)
- ChatBubble (user / AI)
- MissionBanner
- PrimaryButton, GhostButton
- StatusPill: bloqueado | recomendado | em estudo | validar | aprovado | revisar
```

**Reference:** Attach screenshot of roadmap.sh backend beginner page as layout inspiration — but replace linear checklist feel with a **connected skill graph**.

---

## 2. Telas — prompts individuais para Claude Design

### Tela 1 — Goal Picker (`/`)

**Prompt:**

```
Create screen 1 of 6 for Career OS.

Goal: user selects who they want to become.

Layout:
- Centered hero with headline: "Para onde você quer ir?"
- Subhead: "Antes de te dar um plano, precisamos entender seu sonho."
- 3 large selectable cards (only Backend is fully active; others show "Em breve"):
  1. Backend Developer ✓
  2. Data Engineer (disabled)
  3. Frontend Developer (disabled)
- Below cards: text area "Por que esse caminho?" placeholder: "Quero trabalhar com APIs para space tech..."
- Primary CTA: "Começar diagnóstico →"
- Minimal top nav: logo "Career OS" + tagline "Aprender com validação prática"

Style: dark, roadmap.sh-inspired minimalism, skill-graph product feel.
Desktop 1280px. Portuguese BR copy.
Include realistic microcopy, not lorem ipsum.
```

**Estados a pedir depois (inline comment ou chat):**
- Card selected (indigo border glow)
- Empty motivation validation state
- Hover on disabled cards

---

### Tela 2 — AI Diagnostic Chat (`/onboarding`)

**Prompt:**

```
Create screen 2 of 6: AI diagnostic onboarding chat.

Context: user chose Backend Developer and wrote their motivation.

Layout:
- Split view OR full chat with sticky progress bar (Step 2/3 — Diagnóstico)
- Left/top: small recap card showing goal + motivation
- Main: chat interface, 4–6 AI questions already visible in thread
- AI avatar label: "Career OS"
- User can type free-text answers
- Bottom: input + send button
- After last answer, show inline "Gerando diagnóstico..." skeleton

Sample conversation (render as UI, not plain text):
AI: "Você já usou Git em algum projeto?"
User: "Sim, subi um projeto no GitHub mas não domino branches."
AI: "Consegue explicar a diferença entre frontend e backend?"
...

Style: same design system. Chat should feel focused, not like generic ChatGPT.
Portuguese BR.
```

**Estados:**
- Typing indicator
- Loading diagnosis

---

### Tela 3 — Live Roadmap Forge (`/roadmap/forge`) ⭐ STREAMING WOW

**Prompt (mandar DEPOIS do esboço inicial — complemento):**

```
Create screen 3 of 7: Live Roadmap Forge — AI streaming timeline while building the skill graph.

This is a KEY wow moment. The user just finished onboarding. Now they watch the AI think in real time.

Layout (split view):
- LEFT (40%): vertical live timeline feed, auto-scrolling
  - Items appear one by one with subtle fade-in:
    - 🧠 "Analisando lacunas vs perfil..."
    - 🧠 "Git parece redundante — revisão rápida suficiente"
    - 📎 artifact: "HTTP identificado como blocker para REST"
    - 🧠 "Priorizando métodos HTTP e status codes"
    - ✓ "Iteração 1 concluída"
- RIGHT (60%): empty skill graph skeleton slowly filling
  - Nodes appear partially as timeline progresses (ghost → solid)
  - Dependency lines draw in with animation
  - Center text while loading: "Forjando sua trilha..."

Top: progress indicator "Construindo skill graph — passo 2 de 3"

Style: feels like watching an AI agent work — NOT a generic spinner.
Calm, minimal, dark theme. Portuguese BR.
Inspired by roadmap.sh graph but alive and personalized.
Do NOT show final polished graph yet — this is the "in progress" state.
```

**Estados finais desta tela (pedir em follow-up):**
- Mid-stream (timeline half full)
- Almost done (all nodes ghost-visible)

---

### Tela 3b — Graph Reveal (`/roadmap/forge/complete`)

**Prompt:**

```
Create the REVEAL moment after streaming completes.

Transition: timeline collapses to a small summary chip; skill graph expands full width with a satisfying "boom" feel.

- All 7 nodes now solid with status colors:
  Git ✓ aprovado 78% | HTTP ! recomendado 42% | REST 🔒 bloqueado ...
- MissionBanner animates in: "Próxima missão: HTTP básico"
- Primary CTA: "Explorar minha trilha →"
- Small text: "Trilha forjada com base no seu diagnóstico"

Celebratory but minimal — no confetti, no gamification. Premium dev-tool aesthetic.
Portuguese BR. Dark theme.
```

---

### Tela 4 — Diagnosis Result (`/onboarding/result`)

**Prompt:**

```
Create screen 4 of 7: Diagnosis result card (shown briefly before forge, or as recap sidebar).

After onboarding chat, show structured AI diagnosis:

Header: "Seu diagnóstico"
Profile badge: "Iniciante com base em JavaScript"

3 columns or stacked sections:
1. Pontos fortes (green bullets)
   - Já entende lógica básica
   - Já usou GitHub superficialmente
2. Lacunas (amber bullets)
   - HTTP e APIs REST
   - Autenticação
   - Banco relacional
3. Recomendação
   - "Comece por HTTP antes de APIs REST"

Footer CTA: "Ver minha trilha →"

Include subtle "evidência" language — this system tracks learning evidence, not just completion.
Minimal, confident, not celebratory/confetti.
Portuguese BR. Dark theme.
```

---

### Tela 5 — Skill Graph Dashboard (`/roadmap`) ⭐ HERO SCREEN

**Prompt:**

```
Create screen 5 of 7: the hero Skill Graph dashboard (steady state after forge reveal).

This is the most important screen. Inspired by roadmap.sh node layout, but personalized and alive.

Layout:
- Top MissionBanner: "Próxima missão: HTTP básico — métodos e status codes (30 min)"
- Main area: visual skill graph with 7 nodes connected by dependency lines:

Nodes (show status visually):
[✓ aprovado] Git e GitHub — 78%
[! recomendado] HTTP básico — 42%  ← highlighted as current focus
[🔒 bloqueado] APIs REST
[🔒 bloqueado] Autenticação JWT
[! recomendado] Banco relacional — 35%
[🔒 bloqueado] Projeto final: API CRUD

- Right sidebar:
  - Progress summary: "2/7 domínios validados"
  - Recent evidence list (2 items)
  - Button: "Falar com mentor" (secondary)

- Clicking a node opens detail (show REST node preview in a slide-over panel):
  Title: APIs REST
  Status: bloqueado — prerequisite: HTTP básico
  Outcomes list
  CTA: "Validar com IA" (disabled until unlocked)

Use color-coded StatusPills. Locked nodes are dimmed.
Graph should feel like a living map, not a todo list.
Portuguese BR. Dark minimal dev aesthetic.
```

**Variações a pedir:**
- Node hover state
- "revisar" state (amber pulse on REST after failed validation)

---

### Tela 6 — Mastery Validation Interview (`/validate/[topic]`) ⭐ WOW SCREEN #2

**Prompt:**

```
Create screen 6 of 7: AI Mastery Validation interview.

This is the WOW feature. Headline at top:
"Pronto para validar seu aprendizado?"
Subhead: "A IA vai te entrevistar antes de liberar o próximo tópico."

Layout:
- Topic header: "APIs REST" + progress "Pergunta 2 de 3"
- Large AI question card:
  "Explique com suas palavras o que é uma API REST e dê um exemplo de endpoint para criar um usuário."
- Textarea for user answer (show partial answer typed)
- Buttons: "Enviar resposta" + "Desistir"

- Small sidebar or footer note:
  "Avaliação baseada em evidência — não basta marcar como concluído."

Style: focused, exam-like but supportive — not intimidating.
Same dark design system.
Portuguese BR.
```

**Depois pedir Tela 5b — Resultado:**

```
Create the validation RESULT state for the same screen (or separate frame):

Score ring: 48/100
Status pill: REVISAR (amber)

Sections:
✓ Você acertou:
- Entendeu comunicação entre sistemas
- Citou endpoints e JSON

⚠ Precisa melhorar:
- Confundiu método HTTP com rota
- Não explicou status codes

Próximo passo:
"Revise GET, POST, PUT, PATCH, DELETE e tente novamente."

CTAs: "Refazer validação" | "Voltar à trilha"

Include mentor_summary collapsed accordion:
"Para o mentor: aluno confunde API com acesso direto ao banco..."
```

---

### Tela 7 — Adaptive Reaction + Mentor (`/roadmap` updated state)

**Prompt:**

```
Create screen 7 of 7: Skill Graph AFTER failed validation + contextual mentor drawer.

Show the same skill graph dashboard but UPDATED:
- APIs REST node now shows "revisar" (amber) instead of bloqueado
- HTTP básico bumped to top priority with pulsing highlight
- MissionBanner updated: "Foque em HTTP — sua validação em REST mostrou gaps"

Open right drawer: Contextual Mentor chat
User message: "Tenho 40 minutos hoje. O que estudo?"
AI response with numbered 40-min plan referencing the failed REST validation specifically.

This screen proves the system adapts — it's not static.
Portuguese BR. Dark theme.
```

---

## 3. Fluxo de navegação (pedir depois das 6 telas)

**Prompt final de ligação:**

```
Connect all 7 Career OS screens into a clickable prototype flow:

/ → /onboarding → /roadmap/forge → /roadmap/forge/complete → /roadmap → /validate/rest → /roadmap (updated)

Add simple nav dots or breadcrumb: Objetivo → Diagnóstico → Trilha → Validação
Keep all screens visually consistent with the same design system.
Export-ready HTML structure with semantic sections and data attributes:
data-screen="goal-picker|diagnostic|diagnosis-result|skill-graph|validation|adaptive-state"
```

---

## 4. O que NÃO pedir ao Claude Design

- Lógica real de IA (só UI/mock states)
- Auth screens
- Admin dashboard completo
- Gamificação (badges, ranking, streaks)
- Múltiplas trilhas funcionais
- Mobile app native layout

---

## 5. Checklist pós-export (quando voltar com HTML)

Quando trouxer o HTML de volta para implementação:

- [ ] Extrair tokens CSS → `tailwind.config.ts`
- [ ] Mapear componentes → `components/ui/` + domain components
- [ ] `data-screen` → rotas Next.js App Router
- [ ] StatusPill variants → enum do skill graph
- [ ] Mock copy → i18n constants
- [ ] ScoreRing → componente com props `score`, `status`

---

## 6. Prompt meta (opcional — peça feedback ao Claude Design)

```
Review this Career OS prototype for:
1. Information hierarchy on the skill graph screen
2. Accessibility contrast on dark theme
3. Whether the validation flow feels like the hero moment
4. What feels too much like roadmap.sh clone vs uniquely "adaptive skill graph"

Suggest 2 improvements before export.
```
