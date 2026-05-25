FROM python:3.12-slim

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

EXPOSE 8000

CMD ["uvicorn", "career_forge.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
