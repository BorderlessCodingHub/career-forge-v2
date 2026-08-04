"""Shared filesystem paths — local dev and Docker."""

from __future__ import annotations

import os
from pathlib import Path

DEFAULT_TRACK_ID = "rag-engineer-beginner"

# Goal slugs (onboarding) → catalog file stems under data/catalog/
GOAL_TO_CATALOG_TRACK: dict[str, str] = {
    "rag-engineer": "rag-engineer-beginner",
    "agent-engineer": "agent-engineer-beginner",
    "llm-evals": "llm-evals-beginner",
    "fine-tuning": "fine-tuning-beginner",
    # Legacy hackathon goal ids → default LLM track
    "backend": "rag-engineer-beginner",
    "data": "rag-engineer-beginner",
    "frontend": "rag-engineer-beginner",
}


def normalize_catalog_track_id(track_or_goal: str | None) -> str:
    """Map goal slug or LLM drift to an on-disk catalog track id.

    Finalize prompts ask for ``rag-engineer→rag-engineer-beginner``, but the LLM
    sometimes returns the bare goal slug. Without this, forge crashes looking for
    ``data/catalog/rag-engineer.json``.
    """
    if not track_or_goal or not track_or_goal.strip():
        return DEFAULT_TRACK_ID

    raw = track_or_goal.strip()
    mapped = GOAL_TO_CATALOG_TRACK.get(raw)
    if mapped is not None:
        return mapped

    try:
        directory = catalog_dir()
    except FileNotFoundError:
        return raw

    if (directory / f"{raw}.json").is_file():
        return raw

    beginner = f"{raw}-beginner"
    if (directory / f"{beginner}.json").is_file():
        return beginner

    return raw


def _find_data_root() -> Path:
    start = Path(__file__).resolve().parent
    for parent in (start, *start.parents):
        candidate = parent / "data"
        if candidate.is_dir() and (
            (candidate / "catalog").is_dir() or (candidate / "roadmap.json").is_file()
        ):
            return candidate
    raise FileNotFoundError("data/ not found — set CATALOG_DIR or ROADMAP_JSON_PATH or mount ./data")


def catalog_dir() -> Path:
    """Resolve multi-track catalog directory (`data/catalog/`)."""
    env_path = os.environ.get("CATALOG_DIR")
    if env_path:
        return Path(env_path)

    data_root = _find_data_root()
    catalog = data_root / "catalog"
    if catalog.is_dir():
        return catalog

    raise FileNotFoundError("data/catalog/ not found — set CATALOG_DIR or mount ./data")


def must_haves_dir() -> Path:
    """Resolve machine-readable must-have id lists (`data/must-haves/`, CAR-15)."""
    env_path = os.environ.get("MUST_HAVES_DIR")
    if env_path:
        return Path(env_path)

    data_root = _find_data_root()
    directory = data_root / "must-haves"
    if directory.is_dir():
        return directory

    raise FileNotFoundError(
        "data/must-haves/ not found — set MUST_HAVES_DIR or mount ./data",
    )


def roadmap_json_path(track_id: str | None = None) -> Path:
    """Resolve a single-track catalog JSON.

    Prefer ``ROADMAP_JSON_PATH`` (single-file override for tests/legacy).
    Otherwise load ``data/catalog/<track_id>.json``.
    """
    env_path = os.environ.get("ROADMAP_JSON_PATH")
    if env_path:
        return Path(env_path)

    resolved_track = normalize_catalog_track_id(track_id)
    path = catalog_dir() / f"{resolved_track}.json"
    if path.is_file():
        return path

    raise FileNotFoundError(
        f"Catalog for track '{resolved_track}' not found at {path} — "
        "set CATALOG_DIR / ROADMAP_JSON_PATH or mount ./data"
    )


def list_catalog_paths() -> list[Path]:
    """All track JSON files under the catalog directory (or single ROADMAP override)."""
    env_path = os.environ.get("ROADMAP_JSON_PATH")
    if env_path:
        return [Path(env_path)]

    directory = catalog_dir()
    return sorted(directory.glob("*.json"))
