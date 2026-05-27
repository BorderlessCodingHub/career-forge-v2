# Career Forge

**Aprender com validação prática** — skill graph adaptativo que diagnostica, forja trilha ao vivo, valida mastery e gera evidências para mentores.

Hackathon Borderless BASE 01/2026 · repositório `HB01-2026_soft-push` (Soft Push)

| Camada | Tecnologia |
|--------|------------|
| Frontend | Next.js + TypeScript + Tailwind |
| Backend | FastAPI + Pydantic + SQLAlchemy |
| Banco | PostgreSQL |
| IA | LangGraph + LangChain + LangSmith |
| Deploy (produção) | GHCR + VPS (nginx + Docker Compose) |

---

## O que é

Career Forge é um sistema de aprendizado **nativo de IA** para quem está em transição de carreira para tech (muitas vezes começando do zero). Sem IA, o fluxo principal para.

**Problema:** roadmaps genéricos não sabem de onde você parte e não validam se você realmente aprendeu.

**Solução:** trilha personalizada inspirada em [roadmap.sh](https://roadmap.sh), com motor de IA em cada etapa crítica — diagnóstico, forge ao vivo, validação por entrevista e adaptação da trilha.

Visão completa do produto e da arquitetura: [docs/CHECKPOINT.md](./docs/CHECKPOINT.md).

---

## O que o app faz (fluxo)

1. **Objetivo** — escolha de meta e motivação (+ CV em PDF opcional).
2. **Entrevista de diagnóstico (CTRR)** — IA faz até 2 perguntas por rodada, com rubrica adaptativa.
3. **Diagnóstico editável** — você ajusta lacunas e pontos fortes antes de gerar a trilha.
4. **Live Roadmap Forge** — streaming em **timeline only** (sem preview de grafo durante a geração).
5. **Trilha vertical (artifact mode)** — steady state pós-forge, estilo roadmap vertical.
6. **Validar com IA** — entrevista de mastery; trilha reage ao resultado.
7. **Mentor contextual + relatório** — chat com contexto do progresso e evidências para mentores Borderless.

---

## Arquitetura (resumo)

```
apps/frontend/     Next.js (App Router: setup + artifact)
apps/backend/      FastAPI (career_forge)
data/roadmap.json  Catálogo estático de skills
PostgreSQL         Perfis, trilha, sessões de diagnóstico, graph_runs
```

Estrutura detalhada: [docs/engineering/REPO-STRUCTURE.md](./docs/engineering/REPO-STRUCTURE.md).

---

## Quick start (recomendado)

### Pré-requisitos

- [Docker](https://docs.docker.com/get-docker/) + Docker Compose
- Chave OpenAI (obrigatória para diagnóstico, forge e validação)

### Subir a stack

```bash
git clone https://github.com/ProgramadoresSemPatria/HB01-2026_soft-push.git
cd HB01-2026_soft-push

cp .env.example .env
# Edite .env e defina OPENAI_API_KEY=sk-...

make up
make status   # mostra URLs reais (porta do frontend vem de WEB_HOST_PORT no .env)
make smoke    # valida harness + health checks
```

| Serviço | URL típica |
|---------|------------|
| Frontend | `http://localhost:<WEB_HOST_PORT>` (padrão no `.env.example`: **3300**) |
| Backend (OpenAPI) | http://localhost:8000/docs |
| Health | http://localhost:8000/health |

Parar tudo: `make down`

> **Porta do frontend:** o valor vem de `WEB_HOST_PORT` no seu `.env`. O `make status` imprime a URL correta. Se 3300 estiver ocupada, use outra porta (ex.: `WEB_HOST_PORT=3000`) e inclua a origem em `CORS_ORIGINS`.

> **Conflito na 5432:** se outro Postgres já usa a porta 5432 no host, pare o outro serviço ou ajuste o mapeamento em `docker-compose.yml` antes de `make up`.

---

## Variáveis de ambiente essenciais

Copie [.env.example](./.env.example) para `.env` e preencha pelo menos:

| Variável | Obrigatória | Uso |
|----------|-------------|-----|
| `OPENAI_API_KEY` | **Sim** (IA) | Diagnóstico, forge, validação, mock interview |
| `DATABASE_URL` | Sim (Docker preenche) | Postgres |
| `CORS_ORIGINS` | Sim | Deve incluir a URL do frontend (`http://localhost:3300`, etc.) |
| `NEXT_PUBLIC_BACKEND_URL` | Sim | Frontend → API |
| `NEXT_PUBLIC_API_URL` | Sim | Idem |
| `WEB_HOST_PORT` | Sim (local) | Porta publicada do Next.js no host |
| `LANGSMITH_API_KEY` | Não | Observabilidade de traces LLM |
| `LANGSMITH_PROJECT` | Não | Projeto LangSmith (ex.: `career-forge`) |

Produção VPS: [.env.production.example](./.env.production.example) e [docs/engineering/DEPLOY-VPS.md](./docs/engineering/DEPLOY-VPS.md).

---

## Fluxo demo rápido (~5 min)

Com a stack no ar (`make up`):

1. Abra o frontend (`make status` → URL).
2. Defina objetivo e motivação; opcionalmente anexe CV.
3. Complete a entrevista de diagnóstico (pills/texto da API).
4. Em **diagnóstico editável**, ajuste lacunas e clique **Gerar roadmap**.
5. Assista o **Forge** (timeline SSE) até o reveal → trilha vertical.
6. Abra um nó → **Validar com IA** → veja score e trilha reagindo.
7. (Opcional) Mentor / relatório na trilha.

Roteiro alinhado a [docs/CHECKPOINT.md](./docs/CHECKPOINT.md) § Demo script.

---

## Comandos úteis

| Comando | Descrição |
|---------|-----------|
| `make up` | Sobe postgres + backend + frontend (build se necessário) |
| `make down` | Para a stack |
| `make status` | Status do compose + URLs |
| `make smoke` | Harness + health checks |
| `make test` | Bootstrap Postgres + Alembic upgrade + pytest do backend |
| `make seed` | Seed do catálogo + usuária demo Ana |
| `make agent-verify` | Gate C de estrutura + `/health` opcional |

---

## Desenvolvimento sem Docker (opcional)

Útil para debug fino de backend ou frontend isolado.

```bash
# Terminal 1 — só Postgres
docker compose up -d postgres

# Terminal 2 — Backend
cd apps/backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export DATABASE_URL=postgresql+psycopg://careerforge:careerforge@localhost:5432/careerforge
export OPENAI_API_KEY=sk-...
PYTHONPATH=src uvicorn career_forge.main:app --reload --port 8000

# Terminal 3 — Frontend (na raiz do repo, com .env da raiz)
cd apps/frontend
pnpm install && pnpm dev
```

Garanta que `CORS_ORIGINS` e `NEXT_PUBLIC_*` no `.env` da raiz apontem para a porta em que o Next sobe.

---

## Deploy (produção)

| Ambiente | Como |
|----------|------|
| **Produção atual** | Imagens em `ghcr.io/pedroalano/career-forge-{backend,frontend}` · VPS + nginx + `docker-compose.prod.yml` |
| CI/CD | [`.github/workflows/deploy.yml`](./.github/workflows/deploy.yml) (build/push + SSH deploy) |

Runbook completo: [docs/engineering/DEPLOY-VPS.md](./docs/engineering/DEPLOY-VPS.md).

---

## Documentação

| Para quem | Onde começar |
|-----------|----------------|
| **Novos no projeto** | [docs/CHECKPOINT.md](./docs/CHECKPOINT.md) — overview completo |
| **Índice de docs** | [docs/README.md](./docs/README.md) |
| **Agentes / contribuição** | [AGENTS.md](./AGENTS.md) · [docs/ROADMAP.md](./docs/ROADMAP.md) · [docs/STATUS.md](./docs/STATUS.md) |
| **IA / LangGraph** | [docs/engineering/EXECUTION-FLOW.md](./docs/engineering/EXECUTION-FLOW.md) |
| **Diagnóstico CTRR** | [docs/product/DIAGNOSIS-INTERVIEW.md](./docs/product/DIAGNOSIS-INTERVIEW.md) |
| **Design / UI** | [claude-design-docs/](./claude-design-docs/) (protótipo + tokens) |

### Protótipo UI (referência visual)

Não é o app de produção — serve para tokens e componentes:

```bash
cd claude-design-docs/prototype
python3 -m http.server 8765
# http://localhost:8765/
```

---

## Problemas comuns

| Sintoma | Causa provável | O que fazer |
|---------|----------------|-------------|
| `failed to fetch` no browser | CORS ou backend parado | Confira `CORS_ORIGINS` inclui a URL do frontend; `docker compose logs backend` |
| Diagnóstico/forge não responde | `OPENAI_API_KEY` vazio | Preencha em `.env` e `make down && make up` |
| Postgres não sobe | Porta 5432 ocupada | Libere a porta ou ajuste `docker-compose.yml` |
| Frontend em porta errada | `WEB_HOST_PORT` | Use `make status` e abra a URL exibida |
| Backend tests falham com `connection refused` em `localhost:5432` | Postgres não estava ativo antes do pytest | Use `make test` (agora sobe `postgres`, espera readiness e roda `alembic upgrade head`) |

Mais receitas: [.cursor/skills/local-debug/SKILL.md](./.cursor/skills/local-debug/SKILL.md).

---

## Equipe

**Programadores Sem Pátria** — Hackathon BASE 2026

- [Matheus Oliveira](https://github.com/MatheusOliveiraSilva)
- [Pedro Alano](https://github.com/pedroalano)
- [Arthur Araujo](https://github.com/Tute24)

## Créditos

Projeto desenvolvido no **HB01-2026** (Mentoria BASE).
