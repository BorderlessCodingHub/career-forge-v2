# Product Vision — Career Forge

> North star for UI and demo narrative. Authority: [PRODUCT-SOURCE-OF-TRUTH](./PRODUCT-SOURCE-OF-TRUTH.md) · [CHECKPOINT](../docs/CHECKPOINT.md)

---

## One sentence

**Career Forge** modela continuamente a evolução profissional de quem está virando dev — diagnóstico, trilha viva, validação de mastery e evidências para mentores.

---

## Positioning

| They | We |
|------|-----|
| roadmap.sh — caminho genérico igual para todos | Trilha **personalizada** pelo objetivo e ponto de partida |
| Checklist manual / "marque concluído" | **Mastery before progression** — entrevista IA antes de avançar |
| AI tutor genérico no canto | IA como **sistema operacional** da jornada |
| Sem evidência para mentor | **Learning evidence** — scores, lacunas, recomendações estruturadas |

Sub-eixo oficial: **Aprender com validação prática** (Alpha School: domínio demonstrado > conteúdo visto).

---

## Five pillars (demo must show)

### 1. Career Forge — identity engine

Usuário declara **quem quer ser** e **por quê** (motivação). Objetivo alimenta diagnóstico, forge e priorização — não é dropdown decorativo.

- MVP: uma trilha ativa (Backend Developer)
- Outras trilhas: "Em breve" no UI

### 2. Skill graph — cérebro adaptativo

Grafo de dependências personalizado com estados e mastery % — trilha viva, não checklist estático.

- Catálogo base: `data/roadmap.json` (tópicos + prerequisites + rubric)
- Estado dinâmico: status por nó + evidências acumuladas
- **Steady state UI:** layout vertical roadmap.sh-style (spine + categorias + nós left/right)
- Status: `bloqueado | recomendado | em_estudo | validar | aprovado | revisar`

### 3. Live Roadmap Forge — wow #1

Após diagnóstico **editável**, usuário clica **"Gerar roadmap"** e **assiste** a IA forjar a trilha:

- Timeline ao vivo — passos numerados 1, 2, 3, 4… (reasoning, artifacts, decisions)
- **Sem grafo visível durante stream** — foco total no pensamento da IA
- Animação reveal — items voam para layout vertical
- Trilha pronta + próxima missão

Reação esperada: *"Tô vendo a IA pensar e montar MINHA trilha."*

Spec técnica: [stack-and-roadmap-forge.md](../docs/stack-and-roadmap-forge.md) · Flow: [UX-FLOW.md](./UX-FLOW.md)

### 4. Mastery validation — wow #2

Botão **Validar com IA** — entrevista curta, score 0–100, feedback acionável.

- Não aprova respostas vagas
- Gera `mentor_summary` para Borderless
- Reação: *"Não deixa eu mentir que aprendi."*

### 5. Borderless mentor value

Embaixadores julgam utilidade interna. O produto deve mostrar:

- Onde o aluno travou (lacunas da validação)
- Evidências objetivas (não auto-relato)
- Próximo passo recomendado (P1: mentor contextual; P1: relatório simples)

Frase para jurados: *"Reduz trabalho manual do mentor — lacunas e evidências já estruturadas."*

---

## Adaptive loop (P0 narrative)

```
Objetivo → Diagnóstico → Forge → Grafo → Validar → Grafo reage → (mentor contextual)
```

Cena demo obrigatória: validação **ruim** em REST → HTTP sobe prioridade → missão atualizada.

---

## Out of scope (hackathon)

Do not build UI for these in MVP (see [CHECKPOINT](../docs/CHECKPOINT.md)):

- Múltiplas trilhas completas
- Auth enterprise / turmas
- Gamificação (badges, ranking, streaks)
- GitHub integration
- Mock interview loop (P1 stretch)
- CV from evidence (P2)

---

## Success metrics (qualitative, demo)

| Moment | Pass |
|--------|------|
| Editable diagnosis | User adjusts item, clicks "Gerar roadmap" |
| Forge | Timeline-only stream with numbered steps < 60s in demo |
| Reveal | Items animate into vertical roadmap layout |
| Validation | Score + lacunas + próximo passo in one screen |
| Adaptive | Roadmap visibly changes after failed validation |
| Mentor (P1) | Answer references last validation, not generic tips |

---

## References

- [UX-FLOW.md](./UX-FLOW.md) — canonical flow (HAC-21)
- [brief-v1.md](./brief-v1.md) — screen prompts used in Claude Design
- [handoff_chat_gpt.txt](../docs/handoff_chat_gpt.txt) — team debate + judge reframing
- [prototype/](./prototype/) — tokens/components (flow may lag docs)
- [references/roadmap-sh-vertical-ai-tutor.png](./references/roadmap-sh-vertical-ai-tutor.png) — steady-state layout
