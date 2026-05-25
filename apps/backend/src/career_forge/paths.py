"""Shared filesystem paths — local dev and Docker."""

from __future__ import annotations

import os
from pathlib import Path


def roadmap_json_path() -> Path:
    """Resolve roadmap seed JSON for monorepo root or Docker volume."""
    env_path = os.environ.get("ROADMAP_JSON_PATH")
    if env_path:
        return Path(env_path)

    start = Path(__file__).resolve().parent
    for parent in (start, *start.parents):
        candidate = parent / "data" / "roadmap.json"
        if candidate.is_file():
            return candidate

    raise FileNotFoundError("roadmap.json not found — set ROADMAP_JSON_PATH or mount ./data")
