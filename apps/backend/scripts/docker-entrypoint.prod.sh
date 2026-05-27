#!/usr/bin/env bash
# Prod entrypoint: migrate DB, seed skill catalog, optional demo Ana, then start API.
set -euo pipefail

cd /app

echo "Running Alembic migrations..."
alembic upgrade head

echo "Seeding skill catalog (skill_nodes from ROADMAP_JSON_PATH)..."
python -m scripts.seed

if [ "${SEED_DEMO_ANA:-false}" = "true" ]; then
  echo "Seeding demo user Ana..."
  python -m scripts.seed --demo-ana
fi

echo "Starting API..."
exec uvicorn career_forge.main:app --host 0.0.0.0 --port 8000

