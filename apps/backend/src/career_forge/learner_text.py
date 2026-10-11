"""English language instruction for learner-facing model fields (CAR-133).

No database access. Prompt modules import this file. Account reads stay
in services/learner_locale.py.
"""

from __future__ import annotations

from career_forge.output_locale import forge_output_locale

JUDGE_FIELDS = "label, description, and note"
INTERVIEW_FIELDS = "topic, question, and example_of_answer"
FINALIZE_FIELDS = "strengths, gaps, profile label, and starting-priority prose"
MOCK_FIELDS = "question, options, hint, and concept"
GAP_FIELDS = (
    "suggested_remediation. Keep concept equal to the missed question's concept"
)
TUTOR_FIELDS = "the reply"
RESEARCH_FIELDS = "the two UI sentences"


def learner_text_instruction(locale: str | None, fields: str) -> str:
    """English instruction that names the output language and the fields."""
    if forge_output_locale(locale) == "pt-BR":
        language = "Brazilian Portuguese (português do Brasil)"
    else:
        language = "English"
    return (
        f"Write these learner-facing strings in {language}: {fields}. "
        "Leave rubric keys, track ids, and node ids in English. "
        "Do not translate the learner's own words."
    )


def with_learner_instruction(prompt: str, locale: str | None, fields: str) -> str:
    """Append the one language instruction. The prompt body stays as written."""
    return f"{prompt.rstrip()}\n\n{learner_text_instruction(locale, fields)}"
