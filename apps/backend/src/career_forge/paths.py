"""Shared filesystem paths — local dev and Docker."""

from __future__ import annotations

import os
from pathlib import Path

DEFAULT_TRACK_ID = "rag-engineer-beginner"


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


def roadmap_json_path(track_id: str | None = None) -> Path:
    """Resolve a single-track catalog JSON.

    Prefer ``ROADMAP_JSON_PATH`` (single-file override for tests/legacy).
    Otherwise load ``data/catalog/<track_id>.json``.
    """
    env_path = os.environ.get("ROADMAP_JSON_PATH")
    if env_path:
        return Path(env_path)

    resolved_track = track_id or DEFAULT_TRACK_ID
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
