"""Demo mode API contracts — HAC-12."""

from __future__ import annotations

from pydantic import BaseModel, Field

from career_forge.schemas.diagnosis import DiagnosisResponse
from career_forge.schemas.roadmap import RoadmapResponse


class DemoValidationSummary(BaseModel):
    node_id: str
    score: int = Field(ge=0, le=100)
    passed: bool
    feedback: str | None = None


class DemoAnaResponse(BaseModel):
    user_id: str
    display_name: str
    diagnosis: DiagnosisResponse
    roadmap: RoadmapResponse
    validations: list[DemoValidationSummary] = Field(default_factory=list)
    pitch_node_id: str = Field(
        default="rest",
        description="Skill node to highlight for live validation in pitch",
    )
