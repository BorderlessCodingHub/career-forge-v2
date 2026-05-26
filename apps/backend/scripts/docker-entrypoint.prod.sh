#!/usr/bin/env bash
# Prod entrypoint: migrate DB + optional demo seed, then start API without auto-reload.
set -euo pipefail

cd /app

echo "Running Alembic migrations..."
alembic upgrade head

if [ "${SEED_DEMO_ANA:-false}" = "true" ]; then
  echo "Seeding skill catalog + demo user Ana..."
  python -m scripts.seed --demo-ana
fi

echo "Starting API..."
exec uvicorn career_forge.main:app --host 0.0.0.0 --port 8000

