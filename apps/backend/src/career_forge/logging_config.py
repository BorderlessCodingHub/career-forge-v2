"""Local-only file logging when DEBUG=true or ENV=local."""

from __future__ import annotations

import logging
import sys
from pathlib import Path

from career_forge.config import settings


def configure_logging() -> None:
    level = logging.DEBUG if settings.debug else logging.INFO
    handlers: list[logging.Handler] = [logging.StreamHandler(sys.stdout)]

    if settings.local_file_logging:
        log_dir = Path(settings.log_dir)
        log_dir.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_dir / "backend.log", encoding="utf-8")
        file_handler.setFormatter(
            logging.Formatter(
                "%(asctime)s %(levelname)s [%(name)s] %(message)s",
                datefmt="%Y-%m-%dT%H:%M:%S",
            )
        )
        handlers.append(file_handler)

    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
        handlers=handlers,
        force=True,
    )
