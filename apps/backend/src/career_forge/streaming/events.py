"""SSE event helpers — serialize RoadmapForgeEvent for HTTP streams."""

from __future__ import annotations

import json
from typing import Any

from career_forge.schemas.forge import RoadmapForgeEvent


def format_sse(event: RoadmapForgeEvent | dict[str, Any]) -> str:
    """Format a forge event as a single SSE data line."""
    payload = event.model_dump() if hasattr(event, "model_dump") else event
    return f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"
