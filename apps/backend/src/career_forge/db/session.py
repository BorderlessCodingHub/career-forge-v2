"""Single DB entry point — engine, session factory, health check."""

from __future__ import annotations

import os
from collections.abc import Generator

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

from career_forge.db.base import Base

DEFAULT_DATABASE_URL = (
    "postgresql+psycopg://careerforge:careerforge@localhost:5432/careerforge"
)

DATABASE_URL = os.getenv("DATABASE_URL", DEFAULT_DATABASE_URL)

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def check_database_connection() -> bool:
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False


__all__ = [
    "Base",
    "DATABASE_URL",
    "SessionLocal",
    "check_database_connection",
    "engine",
    "get_db",
]
