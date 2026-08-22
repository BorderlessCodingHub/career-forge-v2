#!/usr/bin/env bash
# Rebuild Vite single-file HTML for /welcome/premium-a only (CAR-56 / CAR-52).
# Premium B is App Router `/welcome` — frozen Vite source under
# claude-design-docs/premium-landings/b/ is not built.
# Output is committed under apps/frontend/public/premium-landings/ — the
# frontend Docker image does not run this (no Vite in that image).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUT="$ROOT/apps/frontend/public/premium-landings"
SRC_ROOT="$ROOT/claude-design-docs/premium-landings"

mkdir -p "$OUT"

build_one() {
  local name="$1"
  local src="$SRC_ROOT/$name"
  echo "== Building premium landing ${name} =="
  if [[ ! -f "$src/package.json" ]]; then
    echo "FAIL: missing $src/package.json" >&2
    exit 1
  fi
  (
    cd "$src"
    if [[ -f package-lock.json ]]; then
      npm ci
    else
      npm install
    fi
    npm run build
  )
  local built="$src/dist/index.html"
  if [[ ! -f "$built" ]]; then
    echo "FAIL: expected single-file output at $built" >&2
    exit 1
  fi
  cp "$built" "$OUT/${name}.html"
  echo "Wrote $OUT/${name}.html ($(wc -c < "$built") bytes)"
}

build_one a
echo "premium-landings: OK (A only)"
