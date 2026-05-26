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

## 1) Prepare the VPS directory

1. Create the app directory (example):

   ```bash
   sudo mkdir -p /opt/career-forge
   sudo chown -R "$USER":"$USER" /opt/career-forge
   ```

2. Copy the repo (or clone it) into `/opt/career-forge`.

## 2) Create `/opt/career-forge/.env`

```bash
cd /opt/career-forge
cp .env.production.example .env
```

Set at minimum:

- `POSTGRES_PASSWORD` (generate a strong password)
- `APP_DOMAIN` and `API_DOMAIN`
- `CERTBOT_EMAIL`
- `OPENAI_API_KEY` and `LANGSMITH_API_KEY` (required for diagnosis interview / forge)
- `CORS_ORIGINS` must include `https://$APP_DOMAIN`
- `FRONTEND_HOST_PORT` and `BACKEND_HOST_PORT` must be free on the VPS host

Tip: these host ports are only bound to `127.0.0.1`, so they do not need to be exposed publicly.

## 3) Generate nginx server blocks

1. Render configs from the templates using your VPS `.env`:

   ```bash
   cd /opt/career-forge
   ENV_FILE=./.env ./deploy/scripts/render-nginx.sh
   ```

   If `envsubst` is missing, install it:

   ```bash
   sudo apt-get update
   sudo apt-get install -y gettext-base
   ```

2. Install generated configs alongside existing nginx vhosts:

   ```bash
   sudo cp deploy/nginx/generated/*.conf /etc/nginx/sites-available/
   sudo ln -sf /etc/nginx/sites-available/career-forge-*.conf /etc/nginx/sites-enabled/
   ```

3. Validate and reload:

   ```bash
   sudo nginx -t && sudo systemctl reload nginx
   ```

## 4) Get TLS certificates with Certbot

If certbot is not installed yet:

```bash
sudo apt-get update
sudo apt-get install -y certbot python3-certbot-nginx
```

Then run (creates/updates SSL for the new `server_name` blocks):

```bash
sudo certbot --nginx \
  -d "$APP_DOMAIN" \
  -d "$API_DOMAIN" \
  --email "$CERTBOT_EMAIL" \
  --agree-tos
```

Verify renewal:

```bash
sudo certbot renew --dry-run
```

## 5) Start the production stack

### Option A: Build locally on the VPS (no GitHub Secrets required)

```bash
cd /opt/career-forge
docker compose -f docker-compose.prod.yml build
docker compose -f docker-compose.prod.yml up -d
```

### Option B: Pull GHCR images (for automated deploy)

If you use GitHub Actions deploy, you can pull the tagged images and restart:

```bash
cd /opt/career-forge
docker compose -f docker-compose.prod.yml pull
docker compose -f docker-compose.prod.yml up -d --no-build
```

## 6) Smoke tests

### Backend health

If nginx is live with TLS:

```bash
curl -fsS "https://$API_DOMAIN/health"
```

If you want to bypass TLS and test the container directly:

```bash
curl -fsS "http://127.0.0.1:${BACKEND_HOST_PORT}/health"
```

### Forge SSE

Open the frontend and run through the flow that triggers Forge stream.

If you need a direct curl:

```bash
curl -N \
  -H "Accept: text/event-stream" \
  "https://$API_DOMAIN/forge/<run_id>/stream"
```

## 7) Rollback (v1)

Rollback is done by setting `IMAGE_TAG` to the previous working SHA and restarting:

1. Update `.env`:
   - change `IMAGE_TAG` to the last known good tag (v1 assumes tags are SHAs)
2. Restart:
   ```bash
   docker compose -f docker-compose.prod.yml up -d --no-build
   ```

If you prefer a build-based rollback (no registry):

```bash
git checkout <previous-commit>
docker compose -f docker-compose.prod.yml build
docker compose -f docker-compose.prod.yml up -d
```

## Notes / gotchas

- Ensure `CORS_ORIGINS` includes the browser origin `https://$APP_DOMAIN` (not just localhost).
- nginx SSE block disables buffering for `/forge/…` so streams arrive immediately.
- The compose host ports are bound to `127.0.0.1` only; nginx is the public entrypoint.

