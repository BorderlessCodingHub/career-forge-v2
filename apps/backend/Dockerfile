FROM python:3.12-slim AS base

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app/src

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY alembic.ini .
COPY alembic ./alembic
COPY src ./src
COPY scripts ./scripts
RUN chmod +x scripts/docker-entrypoint.sh scripts/docker-entrypoint.prod.sh

EXPOSE 8000

FROM base AS production
CMD ["bash", "scripts/docker-entrypoint.prod.sh"]

FROM base AS dev
CMD ["bash", "scripts/docker-entrypoint.sh"]
