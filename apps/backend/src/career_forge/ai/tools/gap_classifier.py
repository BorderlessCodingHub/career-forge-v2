"""LLM knowledge-gap classifier + deterministic fallback (HAC-67).

Takes the wrong answers from a mock interview attempt and classifies each into a
structured knowledge gap. Batched into a single LLM call. Falls back to a
deterministic mapping when no API key is configured (tests / offline).
"""

from __future__ import annotations

import asyncio

from career_forge.ai.llm.client import StructuredToolClient
from career_forge.schemas.knowledge_gap import (
    KnowledgeGapClassification,
    KnowledgeGapDraft,
    WrongAnswerItem,
)


def _format_wrong_items(wrong_items: list[WrongAnswerItem]) -> str:
    lines: list[str] = []
    for index, item in enumerate(wrong_items, start=1):
        lines.append(
            f"{index}. concept={item.concept!r}\n"
            f"   question: {item.prompt}\n"
            f"   chose ({item.chosen}): {item.chosen_text}\n"
            f"   correct ({item.correct}): {item.correct_text}"
        )
    return "\n".join(lines)


def _fallback_classification(
    wrong_items: list[WrongAnswerItem],
) -> KnowledgeGapClassification:
    gaps = [
        KnowledgeGapDraft(
            concept=item.concept,
            severity="medium",
            evidence=(
                f"Missed a question on {item.concept}: chose "
                f"{item.chosen or '—'} ({item.chosen_text}), correct was "
                f"{item.correct} ({item.correct_text})."
            ),
            suggested_remediation=f"Review the concept '{item.concept}' and redo a practical exercise.",
        )
        for item in wrong_items
    ]
    return KnowledgeGapClassification(gaps=gaps)


class OpenAiGapClassifier:
    def __init__(self, *, model: str | None = None, api_key: str | None = None) -> None:
        self._client = StructuredToolClient(
            model_env="GAP_CLASSIFIER_MODEL",
            default_model="gpt-5.4-mini",
            temperature=0.2,
            model=model,
            api_key=api_key,
        )

    def _invoke(
        self,
        *,
        node_title: str,
        learner_summary: str | None,
        wrong_items: list[WrongAnswerItem],
    ) -> KnowledgeGapClassification:
        system = (
            "You classify a learner's knowledge gaps from wrong answers in a multiple-choice "
            "mock interview. For each miss, describe the REAL technical knowledge gap "
            "(not 'missed question X'), estimate severity (low/medium/high), and suggest a "
            "short concrete remediation. Merge misses on the same concept into one gap. "
            "Respond in English."
        )
        learner_block = f"\n\n## Learner profile\n{learner_summary}" if learner_summary else ""
        user = (
            f"## Chapter\n{node_title}{learner_block}\n\n"
            f"## Misses\n{_format_wrong_items(wrong_items)}\n\n"
            "Classify the knowledge gaps now."
        )
        return self._client.invoke(
            system=system,
            user=user,
            schema=KnowledgeGapClassification,
        )

    async def classify(
        self,
        *,
        node_title: str,
        learner_summary: str | None,
        wrong_items: list[WrongAnswerItem],
    ) -> KnowledgeGapClassification:
        return await asyncio.to_thread(
            self._invoke,
            node_title=node_title,
            learner_summary=learner_summary,
            wrong_items=wrong_items,
        )


def classify_gaps(
    *,
    node_title: str,
    learner_summary: str | None,
    wrong_items: list[WrongAnswerItem],
) -> KnowledgeGapClassification:
    """Synchronous classify with LLM when configured, else deterministic fallback.

    Runs inside the fire-and-forget background task (threadpool), so it must
    never raise and uses the blocking `_invoke` path directly.
    """
    if not wrong_items:
        return KnowledgeGapClassification(gaps=[])
    try:
        classifier = OpenAiGapClassifier()
    except RuntimeError:
        return _fallback_classification(wrong_items)
    try:
        return classifier._invoke(
            node_title=node_title,
            learner_summary=learner_summary,
            wrong_items=wrong_items,
        )
    except Exception:
        return _fallback_classification(wrong_items)
