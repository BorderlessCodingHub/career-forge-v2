#!/usr/bin/env bash
set -euo pipefail

# Render nginx templates using the VPS `.env` file and `envsubst`.
#
# Usage:
#   cd /opt/career-forge
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

for tpl in "$NGINX_DIR"/career-forge-*.conf.template; do
  base="$(basename "$tpl" .template)"
  envsubst < "$tpl" > "$OUT_DIR/$base"
done

echo "nginx config rendered into: $OUT_DIR"

