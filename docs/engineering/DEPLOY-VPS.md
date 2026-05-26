# Deploy Career Forge on a VPS (nginx + Docker Compose + Let's Encrypt)

This is a v1 deployment runbook for a VPS where **host nginx** already exists. Docker only runs the apps and Postgres; nginx + Certbot live on the host.

## Assumptions

1. You have an existing `nginx` installation on the VPS.
2. You have DNS `A` records pointing to this VPS for:
   - `APP_DOMAIN` (frontend)
   - `API_DOMAIN` (backend + SSE)
3. You can SSH into the VPS.

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
| `NEXT_PUBLIC_BACKEND_URL` | `https://api.yourdomain.com` |
| `NEXT_PUBLIC_API_URL` | `https://api.yourdomain.com` |

These are baked into the frontend image at **build** time in CI.

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
- `CORS_ORIGINS` must include `https://$APP_DOMAIN`
- `FRONTEND_HOST_PORT` and `BACKEND_HOST_PORT` must be free on the host (defaults `13000` / `18000`)
- `GHCR_IMAGE_NAMESPACE=ghcr.io/pedroalano`
- `IMAGE_TAG=latest` (must match tags pushed by CI)

Tip: compose binds app ports to `127.0.0.1` only; nginx is the public entrypoint. **Do not** use `docker-compose.yml` (dev) on the VPS — it can publish Postgres on `5432` and conflict with other stacks.

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
| `failed to fetch` in browser | CORS | `CORS_ORIGINS=https://$APP_DOMAIN` and restart backend |

## Notes

- Ensure `CORS_ORIGINS` includes `https://$APP_DOMAIN`.
- nginx SSE block disables buffering for `/forge/…`.
- Frontend public API URLs come from CI build args (`NEXT_PUBLIC_*` variables).
