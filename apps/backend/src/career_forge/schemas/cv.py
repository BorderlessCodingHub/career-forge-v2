"""CV ingest contracts for diagnosis intake (HAC-33).

Re-exports CTRR attachment/signal models from diagnosis_interview (HAC-42)
and adds parse-result wrapper for the ingest service.
"""

from __future__ import annotations

from pydantic import BaseModel, Field

from career_forge.schemas.diagnosis_interview import CvAttachment, CvSignals

__all__ = ["CvAttachment", "CvParseResult", "CvSignals"]


class CvParseResult(BaseModel):
    """Outcome of CV processing — always safe to consume (fail open)."""

    text: str | None = Field(
        default=None,
        description="Extracted plain text when PDF parse succeeded",
    )
    signals: CvSignals | None = Field(
        default=None,
        description="Structured signals when text was available",
    )
    parse_ok: bool = Field(
        default=False,
        description="True when PDF text extraction succeeded",
    )
