# Sync Arthur — Career Forge scope & sprint decisions

**Date:** 2026-05-25  
**Meeting:** sync (Granola id `c0d6bcc2-4e2e-48b8-b0ad-fd006ba106e7`)  
**Participants:** Matheus Oliveira Silva, Arthur (sync call)

> Source: Granola meeting summary — [sync, 25 May 2026](granola://meeting/c0d6bcc2-4e2e-48b8-b0ad-fd006ba106e7)

---

## Context

Alinhamento de escopo, stack, divisão de time e meta de MVP antes da semana de hackathon. Demonstração do conceito Career Forge para Arthur.

---

## Decisions — FIT (in scope)

| Decision | Detail | Linear mapping |
|----------|--------|----------------|
| **Foco backend especializado** | Trilha para devs backend com objetivo específico (ex.: APIs para space tech) | HAC-8, HAC-6 |
| **Diagnóstico contextual** | IA faz perguntas baseadas no objetivo; gera pontos fortes, gaps, recomendações | HAC-8 |
| **Live Roadmap Forge** | Trilha gerada em tempo real com streaming da IA (+ pesquisa web enriquecida) | HAC-18 |
| **Validação por mock interview** | Após cada tópico, IA entrevista antes de liberar progresso | HAC-10, HAC-14 |
| **Trilha adaptativa** | Falha na avaliação → nova ramificação / repriorização | HAC-11 |
| **Chat integrado contextual** | Pedir referências ou esclarecer dúvidas com memória do progresso | HAC-13 |
| **Diferencial vs roadmap genérico** | Personalização por objetivo + currículo; IA proprietária conhece progresso individual | HAC-8, HAC-18, CHECKPOINT |
| **Stack fechada** | Frontend TypeScript (Arthur) · Backend Python FastAPI + LangChain | HAC-5 |
| **Token OpenAI compartilhado** | $10 crédito dev compartilhado no time | HAC-5 (env setup) |
| **Desenvolvimento paralelo** | Issues Linear por funcionalidade; batches P quando possível | SPRINT-BOARD Sprint 1, 5 |
| **MVP até quinta-feira** | Meta funcional ~2026-05-29 (não domingo) — margem para polish | Milestones Sprint 1–4 |
| **Deploy** | Vercel (web) + VPS/Railway (api) após dev local | HAC-5 |
| **Pitch 7 min** | Demo ao vivo do fluxo completo; foco em validação mock interview | HAC-12 (demo mode) |

---

## Decisions — NO FIT / deferred (won't do this week)

| Item | Reason | Linear |
|------|--------|--------|
| Tracking diário estilo GitHub contributions | Gamificação — não motor do produto | HAC-28 (Cancelled) |
| Sistema de níveis/títulos (aprendiz → global) | Gamificação — polish pós-MVP | HAC-28 |
| Posts automáticos de progresso na plataforma | Social/feed — fora do demo core | HAC-29 (Cancelled) |
| Onboarding com horas/dia para quebrar trilha | Nice-to-have pacing — defer pós-quinta | HAC-30 (Cancelled) |
| Múltiplas trilhas completas (fullstack, data, frontend) | Escopo — uma trilha backend bem feita | CHECKPOINT out-of-scope |
| Auth enterprise / multi-tenant | Demo com user fake ou login simples | CHECKPOINT |
| Web scraping agressivo de conteúdo | Risco técnico; MVP usa LLM + catálogo JSON | HAC-18 (research_enrich simplificado) |
| CV from evidence (P2) | Stretch — só se P0 impecável | HAC-16 (Backlog P2) |

---

## Team split

| Person | Ownership |
|--------|-----------|
| **Arthur** | Frontend TypeScript / Next.js |
| **Matheus** | Harness, backend bootstrap, coordenação agentes, mock das 2 telas principais (até 25/05 noite) |
| **Backend Python** | FastAPI + LangGraph (shared) |

> Participação Arthur pendente confirmação formal (nota da call).

---

## Action items → Linear

| Action | Owner | Issue |
|--------|-------|-------|
| Bootstrap frontend + mock 2 telas principais | Matheus | HAC-5 (partial), HAC-8 |
| Setup Cursor para dev acelerado | Matheus | HAC-19 ✅ |
| Sprint roadmap + agent lifecycle docs | Matheus | HAC-30 |
| Confirmar participação Arthur | Matheus → Arthur | — |
| MVP funcional até quinta | Time | Milestones Sprint 1–4 |
| Pitch 7 min ensaiado | Time | HAC-12 |

---

## Technical direction (confirmed)

```
Onboarding diagnóstico → Live Forge (SSE) → Vertical roadmap artifact
  → Validar com IA (mock interview) → Trilha reage → Mentor contextual (P1)
```

Narrativa de pitch: *"Roadmap que não aceita check manual — a IA diagnostica, forja ao vivo, entrevista e adapta."*

---

*Next review: after Sprint 1 Foundation merge (HAC-5/6/7)*

---

## Historical note (post-MVP evolution)

The deploy decision above reflects the 2026-05-25 meeting context. Current production baseline evolved to GHCR + VPS (host nginx + `docker-compose.prod.yml`) documented in [docs/engineering/DEPLOY-VPS.md](../engineering/DEPLOY-VPS.md).
