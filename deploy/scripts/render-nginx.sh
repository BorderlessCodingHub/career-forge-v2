#!/usr/bin/env bash
set -euo pipefail

# Render nginx templates using the VPS `.env` file and restricted `envsubst`.
# Only Career Forge env vars are substituted; nginx $host, $remote_addr, etc. are preserved.
#
# Usage:
#   cd /home/ubuntu/soft-push
#   ENV_FILE=./.env ./deploy/scripts/render-nginx.sh

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

ENV_FILE="${ENV_FILE:-${1:-./.env}}"
NGINX_DIR="$ROOT_DIR/deploy/nginx"
OUT_DIR="$NGINX_DIR/generated"

if [ ! -f "$ENV_FILE" ]; then
  echo "render-nginx.sh: env file not found: $ENV_FILE" >&2
  exit 1
fi

cd "$ROOT_DIR"

set -a
# shellcheck disable=SC1090
source "$ENV_FILE"
set +a

mkdir -p "$OUT_DIR"

envsubst '${APP_DOMAIN} ${FRONTEND_HOST_PORT}' \
  < "$NGINX_DIR/career-forge-app.conf.template" \
  > "$OUT_DIR/career-forge-app.conf"

envsubst '${API_DOMAIN} ${BACKEND_HOST_PORT}' \
  < "$NGINX_DIR/career-forge-api.conf.template" \
  > "$OUT_DIR/career-forge-api.conf"

echo "nginx config rendered into: $OUT_DIR"
