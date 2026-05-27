"""Build canonical learner context for Roadmap Forge planning."""

from __future__ import annotations

from pydantic import BaseModel, Field

from career_forge.schemas.diagnosis import DiagnosisResponse
from career_forge.schemas.profile_diagnosis import (
    DiagnosisMotorIntake,
    ProfileDiagnosisRecord,
    parse_profile_diagnosis,
)


class LearnerForgeContext(BaseModel):
    """Single payload consumed by roadmap planner/research/evaluator."""

    user_id: str
    goal_id: str
    motivation: str
    years_xp: str | None = None
    diagnosis: DiagnosisResponse
    interview_answers: dict[str, str] = Field(default_factory=dict)
    cv_summary: str | None = None

    def compact_summary(self) -> str:
        answers = "; ".join(
            f"{key}: {value}" for key, value in self.interview_answers.items() if value
        )
        return "\n".join(
            part
            for part in [
                f"goal_id: {self.goal_id}",
                f"motivation: {self.motivation}",
                f"years_xp: {self.years_xp or 'não informado'}",
                f"profile: {self.diagnosis.profile.label}",
                f"strengths: {'; '.join(self.diagnosis.strengths)}",
                f"gaps: {'; '.join(self.diagnosis.gaps)}",
                f"priorities: {'; '.join(self.diagnosis.starting_priorities)}",
                f"cv: {self.cv_summary}" if self.cv_summary else "",
                f"interview_answers: {answers}" if answers else "",
            ]
            if part
        )


def build_forge_context_from_input(
    *,
    user_id: str,
    input_data: dict,
) -> LearnerForgeContext:
    """Build context from GraphRun input, supporting v2 profile envelopes."""
    diagnosis = DiagnosisResponse.model_validate(input_data.get("diagnosis") or input_data)
    profile_record = _profile_record_from_input(input_data, diagnosis)
    intake = profile_record.intake
    return LearnerForgeContext(
        user_id=user_id,
        goal_id=str(input_data.get("goal_id") or intake.goal_id),
        motivation=str(input_data.get("motivation") or intake.motivation),
        years_xp=str(input_data.get("years_xp") or intake.years_xp or "") or None,
        diagnosis=profile_record.diagnosis,
        interview_answers=_answers_from_input(input_data, intake),
        cv_summary=_cv_summary(intake),
    )


def _profile_record_from_input(
    input_data: dict,
    diagnosis: DiagnosisResponse,
) -> ProfileDiagnosisRecord:
    raw_profile = input_data.get("profile_diagnosis")
    if isinstance(raw_profile, dict):
        parsed = parse_profile_diagnosis(raw_profile)
        if parsed is not None:
            return parsed
    return ProfileDiagnosisRecord(
        diagnosis=diagnosis,
        intake=DiagnosisMotorIntake(
            goal_id=str(input_data.get("goal_id") or diagnosis.profile.track_id),
            motivation=str(input_data.get("motivation") or ""),
            years_xp=input_data.get("years_xp"),
            answers=dict(input_data.get("answers") or {}),
        ),
    )


def _answers_from_input(
    input_data: dict,
    intake: DiagnosisMotorIntake,
) -> dict[str, str]:
    answers = dict(intake.answers)
    answers.update(
        {
            str(key): str(value)
            for key, value in dict(input_data.get("answers") or {}).items()
            if value
        },
    )
    return answers


def _cv_summary(intake: DiagnosisMotorIntake) -> str | None:
    if intake.cv_signals is None:
        return None
    signals = intake.cv_signals
    chunks = [
        f"skills={', '.join(signals.skills)}" if signals.skills else "",
        f"roles={', '.join(signals.roles)}" if signals.roles else "",
        f"years_hint={signals.years_hint}" if signals.years_hint else "",
        f"evidence={'; '.join(signals.evidence_snippets)}"
        if signals.evidence_snippets
        else "",
    ]
    return "; ".join(chunk for chunk in chunks if chunk) or None
