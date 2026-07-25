# Deploy Career Forge on a VPS (nginx + Docker Compose + Let's Encrypt)

> **Labs path is primary for v2.** Prefer [DEPLOY-LABS-MANUAL.md](../DEPLOY-LABS-MANUAL.md)
> (`labs.borderlesscoding.com/career-forge`). This document remains for alternate
> subdomain / dual-domain nginx setups.

This is a deployment runbook for a VPS where **host nginx** already exists. Docker only runs the apps and Postgres; nginx + Certbot live on the host.

Product-level deployment overview lives in [docs/CHECKPOINT.md](../CHECKPOINT.md) under **Deployment baseline**.

## Assumptions

1. You have an existing `nginx` installation on the VPS **or** you expose the frontend via Cloudflare Tunnel to a path gateway (e.g. `labs.borderlesscoding.com/career-forge`).
2. For the classic nginx+subdomain setup, you have DNS `A` records pointing to this VPS for:
   - `APP_DOMAIN` (frontend)
   - `API_DOMAIN` (backend + SSE)
3. You can SSH into the VPS.

The Next app uses `basePath: /career-forge`. Under labs path routing (gateway + Tunnel), leave `NEXT_PUBLIC_BACKEND_URL` / `NEXT_PUBLIC_API_URL` empty so the browser calls same-origin `/career-forge/…` API prefixes; compose sets `API_INTERNAL_URL=http://backend:8000` for Next rewrites (SSE without browser CORS to `:18000`). Set `CORS_ORIGINS` to include `https://labs.borderlesscoding.com` and/or `https://labs-gateway.yuri-491.workers.dev` on the backend.

## Labs path checklist (gateway + Tunnel)

1. Deploy frontend+backend on VPS (`docker-compose.prod.yml`); frontend listens on `FRONTEND_HOST_PORT` (default `13000`).
2. Cloudflare Tunnel → `http://127.0.0.1:13000` (public origin **without** `/career-forge` path — Next serves under basePath).
3. Set labs-gateway `CAREER_FORGE_ORIGIN` to that tunnel HTTPS origin.
4. Backend `CORS_ORIGINS=https://labs.borderlesscoding.com,https://labs-gateway.yuri-491.workers.dev` (Origin has no path).
5. Leave `NEXT_PUBLIC_BACKEND_URL` / `NEXT_PUBLIC_API_URL` empty in the frontend image build so API calls stay same-origin under `/career-forge`.
6. Smoke: `curl -i https://labs-gateway…/career-forge` and `…/career-forge/health`.

For host-nginx path blocks (`/career-forge` + `/career-forge/api`), see [DEPLOY-LABS-MANUAL.md](../DEPLOY-LABS-MANUAL.md).

## Files in this repo

- Production compose: [`docker-compose.prod.yml`](../../docker-compose.prod.yml)
- VPS env template: [`/.env.production.example`](../../.env.production.example)
- Nginx templates + generator:
  - [`deploy/nginx/*.conf.template`](../../deploy/nginx/)
  - [`deploy/scripts/render-nginx.sh`](../../deploy/scripts/render-nginx.sh)
- CI/CD: [`.github/workflows/deploy.yml`](../../.github/workflows/deploy.yml)

## GitHub Actions setup (one-time)

GHCR image names must be **lowercase**. This project publishes under `ghcr.io/pedroalano/...` (not the org name `ProgramadoresSemPatria`).

### Personal access token (PAT)

1. GitHub profile → **Settings → Developer settings → Personal access tokens**
2. Create a token with **`read:packages`** and **`write:packages`**
3. Store the value as repo secret **`GHCR_TOKEN`**

### Repository secrets

**Settings → Secrets and variables → Actions → Secrets**

| Secret | Value |
|--------|--------|
| `GHCR_TOKEN` | PAT from above |
| `GHCR_USERNAME` | `pedroalano` (optional; workflow uses `pedroalano` explicitly) |
| `VPS_HOST` | VPS IP or hostname |
| `VPS_USER` | SSH user (e.g. `ubuntu`) |
| `VPS_SSH_KEY` | Private SSH key (PEM) for the VPS |

### Repository variables

**Settings → Secrets and variables → Actions → Variables**

| Variable | Example |
|----------|---------|
| `NEXT_PUBLIC_BACKEND_URL` | _(empty for labs same-origin)_ or `https://api.yourdomain.com` |
| `NEXT_PUBLIC_API_URL` | _(empty for labs same-origin)_ or `https://api.yourdomain.com` |

These are baked into the frontend image at **build** time in CI. For labs path + Tunnel/gateway, prefer empty so the client uses `/career-forge/…` with Next rewrites.

### Package visibility

After the first successful workflow run, open [github.com/pedroalano?tab=packages](https://github.com/pedroalano?tab=packages) and set `career-forge-backend` / `career-forge-frontend` to **public**, or keep private and ensure the VPS `docker login` token can **read** packages.

## 1) Prepare the VPS directory

Example path used by the deploy workflow:

```bash
# clone or sync repo
cd /home/ubuntu/soft-push
```

If you use a different path, update `APP_DIR` in [`.github/workflows/deploy.yml`](../../.github/workflows/deploy.yml).

## 2) Create `/home/ubuntu/soft-push/.env`

```bash
cd /home/ubuntu/soft-push
cp .env.production.example .env
nano .env
```

Set at minimum:

- `POSTGRES_PASSWORD` (strong, non-empty)
- `APP_DOMAIN` and `API_DOMAIN`
- `CERTBOT_EMAIL`
- `OPENAI_API_KEY` and `LANGSMITH_API_KEY`
- `CORS_ORIGINS` must include the browser origin (`https://$APP_DOMAIN`, or `https://labs.borderlesscoding.com` when the app is served under `/career-forge` — Origin has no path)
- `FRONTEND_HOST_PORT` and `BACKEND_HOST_PORT` must be free on the host (defaults `13000` / `18000`)
- `GHCR_IMAGE_NAMESPACE=ghcr.io/pedroalano`
- `IMAGE_TAG=latest` (must match tags pushed by CI)

Tip: compose binds app ports to `127.0.0.1` only; nginx is the public entrypoint. **Do not** use `docker-compose.yml` (dev) on the VPS — it can publish Postgres on `5432` and conflict with other stacks.

### Skill catalog data (`data/roadmap.json`)

Production compose mounts the repo `data/` directory read-only into the backend container as `/data` (see [`docker-compose.prod.yml`](../../docker-compose.prod.yml)). The backend uses `ROADMAP_JSON_PATH=/data/roadmap.json` (default in compose).

**Required on the VPS:** keep `data/roadmap.json` in the deploy directory (same tree as `git pull` / CI sync). Without it, backend startup seed fails and forge/roadmap flows have no `skill_nodes`.

On every backend container start, the prod entrypoint runs `python -m scripts.seed` after migrations. That upserts the skill catalog idempotently. `SEED_DEMO_ANA=true` (optional) runs a second seed pass with `--demo-ana` for the pitch demo user only; production should leave `SEED_DEMO_ANA=false` (see [`.env.production.example`](../../.env.production.example)).

**Persistence stores:** set `DIAGNOSIS_SESSION_STORE=postgres` and `GRAPH_RUN_STORE=postgres` (defaults in compose when `ENV=production`) so interview sessions and forge `GraphRun` records survive container restarts.

## 3) Generate nginx server blocks

`render-nginx.sh` uses **restricted** `envsubst` so nginx variables like `$host` are not stripped.

```bash
cd /home/ubuntu/soft-push
ENV_FILE=./.env ./deploy/scripts/render-nginx.sh
```

If `envsubst` is missing:

```bash
sudo apt-get update
sudo apt-get install -y gettext-base
```

Install generated configs:

```bash
sudo cp deploy/nginx/generated/*.conf /etc/nginx/sites-available/
sudo ln -sf /etc/nginx/sites-available/career-forge-*.conf /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
```

## 4) Get TLS certificates with Certbot

```bash
set -a && source .env && set +a
sudo apt-get install -y certbot python3-certbot-nginx
sudo certbot --nginx \
  -d "$APP_DOMAIN" \
  -d "$API_DOMAIN" \
  --email "$CERTBOT_EMAIL" \
  --agree-tos
sudo certbot renew --dry-run
```

## 5) Start the production stack

### Option A: Pull from GHCR (recommended)

```bash
cd /home/ubuntu/soft-push
set -a && source .env && set +a

echo "$GHCR_TOKEN" | docker login ghcr.io -u pedroalano --password-stdin
docker compose -f docker-compose.prod.yml pull
docker compose -f docker-compose.prod.yml up -d --no-build
```

Or trigger **Actions → Deploy production (VPS)** on `main` (requires `VPS_*` secrets). The deploy job verifies `https://$API_DOMAIN/health` with `curl` (no Python required on the VPS).

Always **`pull`** before **`up`** when using `IMAGE_TAG=latest`.

### Option B: Build on the VPS (no GHCR)

```bash
cd /home/ubuntu/soft-push
docker compose -f docker-compose.prod.yml build
docker compose -f docker-compose.prod.yml up -d
```

## 6) Smoke tests

```bash
curl -fsS "http://127.0.0.1:${BACKEND_HOST_PORT}/health"
curl -fsS "https://$API_DOMAIN/health"
```

Forge SSE (through nginx):

```bash
curl -N -H "Accept: text/event-stream" "https://$API_DOMAIN/forge/<run_id>/stream"
```

## 7) Rollback

If CI also pushed `:${{ github.sha }}`, pin VPS `.env`:

```env
IMAGE_TAG=<previous-commit-sha>
```

Then:

```bash
docker compose -f docker-compose.prod.yml pull
docker compose -f docker-compose.prod.yml up -d --no-build
```

Build-based rollback on VPS:

```bash
git checkout <previous-commit>
docker compose -f docker-compose.prod.yml build
docker compose -f docker-compose.prod.yml up -d
```

## Troubleshooting

| Symptom | Cause | Fix |
|---------|--------|-----|
| `repository name must be lowercase` | GHCR tag used `ProgramadoresSemPatria` | Use `ghcr.io/pedroalano/...` (see workflow) |
| `manifest unknown` on pull | `IMAGE_TAG` mismatch | Set `IMAGE_TAG=latest` or the SHA CI pushed; run `docker compose pull` |
| Postgres exits immediately | Empty `POSTGRES_PASSWORD` in `.env` | Set password; if volume was initialized with another password, `docker compose down -v` (data loss) |
| `Bind for 0.0.0.0:5432 failed` | Wrong compose file (dev) | Use `docker-compose.prod.yml` only |
| `invalid number of arguments in proxy_set_header` | Bare `envsubst` wiped `$host` | Use updated `render-nginx.sh` (restricted substitution) |
| `python: command not found` in deploy job | SSH health check used Python | Fixed in workflow: uses `curl -fsS https://$API_DOMAIN/health` |
| `failed to fetch` in browser | CORS | `CORS_ORIGINS` must match browser Origin (`https://$APP_DOMAIN` or `https://labs.borderlesscoding.com`); restart backend |
| Onboarding SSE 404 on `/diagnosis/interview/.../stream` | Missing rewrite / wrong path | Same-origin client calls `/career-forge/diagnosis/...` (basePath). Ensure `API_INTERNAL_URL` is set on the frontend container and image includes current `next.config.mjs`. Optional: set GitHub vars `NEXT_PUBLIC_BACKEND_URL=https://$API_DOMAIN` for separate API origin |
| Forge/roadmap empty or 500 after deploy | Missing catalog seed / `roadmap.json` | Ensure `data/roadmap.json` exists on VPS; check backend logs for seed errors; restart backend after fixing mount |

## Deploy badge (frontend footer)

After each production frontend image build, CI bakes:

- `NEXT_PUBLIC_BUILD_SHA` — git commit (`github.sha`)
- `NEXT_PUBLIC_BUILD_TIME` — commit timestamp

The app shows a fixed bottom strip on every page: **deploy {shortSha} · {time}** plus a live **API health** dot (`GET /health`).

| Environment | What you should see |
|-------------|---------------------|
| **Production** (post-deploy) | Short SHA matching latest `main` commit; green dot when API is healthy |
| **Local** (`make up`) | `local dev` label when build vars are unset |

To verify a deploy landed: open `https://$APP_DOMAIN`, compare footer SHA with `git log -1 --oneline` on the VPS after `git pull`, and confirm the health dot is green.

## Notes

- Ensure `CORS_ORIGINS` includes `https://$APP_DOMAIN` (or `https://labs.borderlesscoding.com` for the labs path gateway).
- Frontend uses Next `basePath: /career-forge`. Same-origin API calls go to `/career-forge/diagnosis/…`, `/career-forge/forge/…`, etc.; Next rewrites them to `API_INTERNAL_URL` (compose sets `http://backend:8000`). Leave `NEXT_PUBLIC_BACKEND_URL` / `NEXT_PUBLIC_API_URL` empty for that mode so SSE stays same-origin.
- nginx SSE block disables buffering for `/forge/…` (subdomain nginx templates). Under labs+Tunnel, the gateway hits the Next port directly — rewrites handle SSE.
- Optional cross-origin API: CI build args `NEXT_PUBLIC_*` pointing at a public API origin (or nginx `/career-forge/api`).
