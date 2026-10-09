"""Roadmap language for one forge run (CAR-132).

The planner prompt stays English. The locale is copied onto the GraphRun
when the run starts. A later switch applies to the next forge. An existing
roadmap is not translated.
"""

from __future__ import annotations

from typing import Any


def forge_output_locale(stored: str | None) -> str:
    """English until the learner has chosen Brazilian Portuguese."""
    if stored == "pt-BR":
        return "pt-BR"
    return "en"


def stamp_forge_output_locale(
    forge_input: dict[str, Any],
    stored: str | None,
) -> dict[str, Any]:
    """Copy the account locale onto this run. Ignores a client-supplied value."""
    stamped = dict(forge_input)
    stamped["output_locale"] = forge_output_locale(stored)
    return stamped


_STUDY_PLAN_PROSE = (
    "goal, learner_context_summary, strategy, each node's title, why_now, "
    "and key_concepts, and each task's title, outcome, and evidence_prompt"
)


def roadmap_language_instruction(locale: str | None) -> str:
    """English instruction that names the roadmap's output language."""
    if forge_output_locale(locale) == "pt-BR":
        language = "Brazilian Portuguese (português do Brasil)"
    else:
        language = "English"
    return f"Write these StudyPlan strings in {language}: {_STUDY_PLAN_PROSE}."
