# Deploy Manual — labs.borderlesscoding.com/career-forge

Step-by-step for Pedro. These are the **manual** steps only.  
Code changes (Next.js basePath, 4 tracks, forge cap, GHCR namespace) are delivered as a single PR — merge that first, then follow this guide.

**Target URL:** `https://labs.borderlesscoding.com/career-forge`  
**API (preferred):** same-origin under basePath — browser calls `/career-forge/diagnosis/…`, `/career-forge/health`, etc.; Next rewrites to the backend via `API_INTERNAL_URL`.  
**API (alternate nginx split):** `https://labs.borderlesscoding.com/career-forge/api` → backend `:18000` (set `NEXT_PUBLIC_*` to that origin).  
**VPS ports (localhost only):** frontend `13000`, backend `18000`

---

## 0. Pre-flight checklist

Before touching the VPS, confirm:

- [ ] PR merged to `main` (4 tracks + basePath + forge cap + GHCR namespace)
- [ ] You have SSH access to the VPS
- [ ] You have a GHCR PAT from `pedroalano` account (read:packages + write:packages)
- [ ] `OPENAI_API_KEY` in hand
- [ ] `LANGSMITH_API_KEY` in hand (optional but recommended)

---

## 1. GitHub — fork + secrets + variables

### 1.1 Fork/transfer repo

Fork (or transfer) this repo to `borderlesscodinghub` as a **private** repo.  
All steps below refer to the **new** org repo.

### 1.2 Create a GHCR token (conta `pedroalano`)

Images são publicadas em `ghcr.io/pedroalano/career-forge-{backend,frontend}` — sem dependência de acesso admin na org `borderlesscodinghub`.

**Criar o PAT:**

1. Acesse: github.com → avatar → **Settings → Developer settings → Personal access tokens → Tokens (classic)**
2. Clique **Generate new token (classic)**
3. Nome sugerido: `career-forge-labs-ghcr`
4. Expiration: 90 dias (ou No expiration)
5. Marque os scopes: `write:packages` + `read:packages` (isso já inclui `repo` implicitamente para packages)
6. Clique **Generate token** e **copie o valor imediatamente** — ele não aparece novamente

Você vai usar esse token em dois lugares:
- **Passo 1.3** → secret `GHCR_TOKEN` no repo da org (usado pelo CI para push)
- **Passo 4** → `docker login ghcr.io -u pedroalano` no VPS (para pull)

### 1.3 Add repository secrets

**Org repo → Settings → Secrets and variables → Actions → Secrets**

| Secret | Value |
|--------|-------|
| `GHCR_TOKEN` | PAT from step 1.2 |
| `VPS_HOST` | VPS IP or hostname |
| `VPS_USER` | SSH user (e.g. `ubuntu`) |
| `VPS_SSH_KEY` | Full private key PEM (the one whose public key is in `~/.ssh/authorized_keys` on the VPS) |
| `OPENAI_API_KEY` | OpenAI key |
| `LANGSMITH_API_KEY` | LangSmith key (leave empty string if skipping) |
| `POSTGRES_PASSWORD` | Strong password — min 16 chars, no special chars that break shell |

### 1.4 Add repository variables

**Org repo → Settings → Secrets and variables → Actions → Variables**

**Preferred (labs-gateway / Tunnel / same-origin rewrites):** leave both empty (or unset the GitHub variables) so the browser uses `/career-forge/…` and Next rewrites to `API_INTERNAL_URL`.

| Variable | Value |
|----------|-------|
| `NEXT_PUBLIC_BACKEND_URL` | _(empty)_ |
| `NEXT_PUBLIC_API_URL` | _(empty)_ |

**Alternate (host nginx `/career-forge/api` split from §3):** set both to `https://labs.borderlesscoding.com/career-forge/api`.

These are baked into the frontend image at **build time** — if you change them later, you must rebuild + redeploy the frontend.

### 1.5 Set package visibility (after first successful push)

After the first workflow run pushes images:

1. Go to `github.com/pedroalano?tab=packages`
2. For `career-forge-backend` and `career-forge-frontend`:
   - If keeping private: ensure the VPS `docker login` token has `read:packages` (already set in 1.2)
   - If making public: change visibility to Public (simpler, no VPS login needed at step 4)

---

## 2. VPS — directory + .env

### 2.1 SSH into the VPS

```bash
ssh ubuntu@<VPS_HOST>
```

### 2.2 Create deploy directory

```bash
mkdir -p /home/ubuntu/career-forge
cd /home/ubuntu/career-forge
```

### 2.3 Clone the org repo

```bash
git clone https://github.com/borderlesscodinghub/career-forge-v2.git .
# if private, use a deploy key or HTTPS with PAT:
# git clone https://<PAT>@github.com/borderlesscodinghub/career-forge-v2.git .
```

### 2.4 Create `.env`

```bash
cp .env.production.example .env
nano .env
```

Fill in the values below. Lines marked `# CHANGE` require your input.

```env
# --- Postgres ---
POSTGRES_USER=careerforge
POSTGRES_PASSWORD=<strong-password>            # CHANGE
POSTGRES_DB=careerforge

# --- Ports (keep defaults unless conflicting) ---
FRONTEND_HOST_PORT=13000
BACKEND_HOST_PORT=18000

# --- Not used in path-based setup — leave as placeholders ---
APP_DOMAIN=labs.borderlesscoding.com
API_DOMAIN=labs.borderlesscoding.com
CERTBOT_EMAIL=                                 # not needed, TLS managed externally

# --- CORS (browser origin — scheme+host, no path) ---
# Include workers.dev while labs DNS/gateway cutover is pending.
CORS_ORIGINS=https://labs.borderlesscoding.com,https://labs-gateway.yuri-491.workers.dev

# --- Frontend URLs (baked at build time via CI) ---
# Preferred: leave empty → same-origin /career-forge/… + Next rewrites.
# Alternate nginx /api split: https://labs.borderlesscoding.com/career-forge/api
NEXT_PUBLIC_BACKEND_URL=
NEXT_PUBLIC_API_URL=

# --- Backend behavior ---
ENV=production
DEBUG=false
SEED_DEMO_ANA=false
ROADMAP_JSON_PATH=/data/roadmap.json
DIAGNOSIS_SESSION_STORE=postgres
GRAPH_RUN_STORE=postgres
DIAGNOSIS_INTERVIEW_MODEL=gpt-4.1-nano

# --- AI providers ---
OPENAI_API_KEY=<your-key>                      # CHANGE
FORGE_SEARCH_MODEL=gpt-5.4
FORGE_PLANNER_MODEL=gpt-5.4
FORGE_EVALUATOR_MODEL=gpt-5.4-mini
FORGE_STREAM_DELAY_SEC=1.5
LANGSMITH_API_KEY=<your-key>                   # CHANGE (or leave empty)
LANGSMITH_PROJECT=career-forge

# --- GHCR images ---
GHCR_IMAGE_NAMESPACE=ghcr.io/pedroalano
IMAGE_TAG=latest
```

---

## 3. VPS — nginx config

The TLS certificate for `labs.borderlesscoding.com` is already managed elsewhere.  
You only need to add **location blocks** inside the existing server block for that domain.

### 3.1 Find the existing server config

```bash
grep -r "labs.borderlesscoding.com" /etc/nginx/ --include="*.conf" -l
```

Open that file:

```bash
sudo nano /etc/nginx/sites-available/<filename>.conf
```

### 3.2 Add Career Forge location blocks

Inside the `server` block that handles `labs.borderlesscoding.com` (after any existing `location` blocks, before the closing `}`), add:

```nginx
    # ── Career Forge API ────────────────────────────────────────────────────
    # SSE buffering is off for the whole API block — diagnosis and forge need it.
    location /career-forge/api/ {
        proxy_pass http://127.0.0.1:18000/;
        proxy_http_version 1.1;

        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        proxy_buffering off;
        proxy_cache off;
        proxy_read_timeout 3600s;
        proxy_send_timeout 3600s;
        proxy_set_header Accept-Encoding "";
        proxy_set_header Connection "";
        add_header Cache-Control "no-cache" always;
    }

    # ── Career Forge Frontend ────────────────────────────────────────────────
    # Next.js is built with basePath=/career-forge — pass full path, no stripping.
    location /career-forge {
        proxy_pass http://127.0.0.1:13000;
        proxy_http_version 1.1;

        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
```

> **Why two blocks and not one?**  
> The API block uses `proxy_pass http://...18000/;` with a trailing slash — this strips the `/career-forge/api/` prefix so FastAPI sees clean paths (e.g. `/health`, `/forge/...`).  
> The frontend block has no trailing slash — Next.js needs the full `/career-forge/...` path because it was compiled with `basePath: '/career-forge'`.

### 3.3 Test and reload nginx

```bash
sudo nginx -t
sudo systemctl reload nginx
```

---

## 4. VPS — docker login

```bash
echo "<GHCR_TOKEN>" | docker login ghcr.io -u pedroalano --password-stdin
```

If images are public, skip this step.

---

## 5. First deploy

### Option A — trigger CI (recommended)

Push any commit to `main` on the org repo, or go to:  
**Actions → Deploy production (VPS) → Run workflow**

CI will build images, push to GHCR, SSH into the VPS, pull, and run `docker compose up -d`.

### Option B — manual pull on the VPS

```bash
cd /home/ubuntu/career-forge
set -a && source .env && set +a

docker compose -f docker-compose.prod.yml pull
docker compose -f docker-compose.prod.yml up -d --no-build
```

---

## 6. Seed + smoke test

### 6.1 Run catalog seed (if not auto-seeded)

The backend container runs seed automatically on startup. Verify:

```bash
docker compose -f docker-compose.prod.yml logs backend | grep -i seed
```

Expected: `Seeded X skill nodes` with 4 tracks visible.

Force a manual seed if needed:

```bash
docker compose -f docker-compose.prod.yml exec backend python -m scripts.seed
```

### 6.2 Smoke tests

```bash
# API health (internal)
curl -fsS http://127.0.0.1:18000/health

# Same-origin health via Next rewrite (preferred empty NEXT_PUBLIC_* mode)
curl -fsS https://labs.borderlesscoding.com/career-forge/health

# API health through nginx /api split (only if using alternate NEXT_PUBLIC_* = …/career-forge/api)
curl -fsS https://labs.borderlesscoding.com/career-forge/api/health

# Frontend
curl -fsS -o /dev/null -w "%{http_code}" https://labs.borderlesscoding.com/career-forge
# Expected: 200

# SSE probe — same-origin rewrite mode (Ctrl+C to stop)
curl -N -H "Accept: text/event-stream" \
  https://labs.borderlesscoding.com/career-forge/forge/<any-run-id>/stream
```

Health response must be:

```json
{"service": "career-forge-api", "status": "ok", "database": "connected"}
```

### 6.3 Gate acceptance

- [ ] `/health` returns `"database":"connected"`
- [ ] `make seed` / backend logs show 4 tracks without errors
- [ ] 11th forge for same user_id → HTTP 429
- [ ] Frontend loads at `https://labs.borderlesscoding.com/career-forge`

---

## 7. Rollback

```bash
cd /home/ubuntu/career-forge
set -a && source .env && set +a

# Pin to previous image tag (find SHA in GitHub Actions run history)
sed -i 's/^IMAGE_TAG=.*/IMAGE_TAG=<previous-sha>/' .env

docker compose -f docker-compose.prod.yml pull
docker compose -f docker-compose.prod.yml up -d --no-build
```

---

## Troubleshooting

| Symptom | Likely cause | Fix |
|---------|-------------|-----|
| `502 Bad Gateway` on `/career-forge` | Frontend container not running | `docker compose -f docker-compose.prod.yml ps` → check status |
| `502 Bad Gateway` on `/career-forge/api/` | Backend not healthy yet | Wait for healthcheck: `docker compose -f docker-compose.prod.yml logs -f backend` |
| Frontend loads but API calls fail (`failed to fetch`) | `CORS_ORIGINS` missing / wrong | Ensure `CORS_ORIGINS` includes browser Origin (`https://labs.borderlesscoding.com` and/or `https://labs-gateway.yuri-491.workers.dev`); restart backend |
| Assets 404 (`/_next/static/...`) | Next.js built without `basePath` | Ensure image includes `basePath: '/career-forge'` and rebuild |
| API 404 on `/career-forge/diagnosis/…` with empty `NEXT_PUBLIC_*` | Missing Next rewrite / `API_INTERNAL_URL` | Confirm frontend container has `API_INTERNAL_URL=http://backend:8000` and current `next.config.mjs` (includes `knowledge-gaps`, `tutor`, `/health`) |
| `/career-forge/health` returns Next.js 404 HTML; badge **API unreachable**; `:18000/health` OK | Rewrites baked at **build** without `API_INTERNAL_URL` | Rebuild frontend with `API_INTERNAL_URL=http://backend:8000` build-arg (CAR-19); runtime-only env is too late |
| SSE stream closes immediately / no events | nginx buffering on | Confirm `proxy_buffering off` is in the API location block (nginx `/api` mode) |
| Forge routes return 404 from API | nginx stripping prefix wrong | Check trailing slash on `proxy_pass http://127.0.0.1:18000/;` in API block |
| `manifest unknown` on docker pull | `IMAGE_TAG` mismatch or images not pushed yet | Check GitHub Actions — wait for push job to succeed |
| Seed fails: no skill_nodes | `data/roadmap.json` missing on VPS | `ls data/roadmap.json` in deploy dir — must exist after `git clone` |
