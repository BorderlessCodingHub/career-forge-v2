"""LLM knowledge-gap classifier + deterministic fallback (HAC-67).

Takes the wrong answers from a mock interview attempt and classifies each into a
structured knowledge gap. Batched into a single LLM call. Falls back to a
deterministic mapping when no API key is configured (tests / offline).
"""

from __future__ import annotations

import asyncio

from career_forge.ai.llm.client import StructuredToolClient
from career_forge.ai.tracing import LlmTraceContext
from career_forge.schemas.knowledge_gap import (
    KnowledgeGapClassification,
    KnowledgeGapDraft,
    WrongAnswerItem,
)
from career_forge.services.forge_locale import is_portuguese
from career_forge.learner_text import GAP_FIELDS, with_learner_instruction

_GAP_BODY = (
    "You classify a learner's knowledge gaps from wrong answers in a multiple-choice "
    "mock interview. For each miss, copy `concept` from that miss unchanged. "
    "Estimate severity (low/medium/high), and write suggested_remediation as a "
    "short concrete next step for the real technical gap (not 'missed question X'). "
    "Merge misses on the same concept into one gap."
)


def gap_classifier_system(locale: str | None) -> str:
    """English classifier body plus the locale instruction."""
    return with_learner_instruction(_GAP_BODY, locale, GAP_FIELDS)


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
    *,
    locale: str | None = None,
) -> KnowledgeGapClassification:
    gaps = []
    for item in wrong_items:
        if is_portuguese(locale):
            remediation = (
                f"Revise o conceito '{item.concept}' e refaça um exercício prático."
            )
        else:
            remediation = (
                f"Review the concept '{item.concept}' and redo a practical exercise."
            )
        gaps.append(
            KnowledgeGapDraft(
                concept=item.concept,
                severity="medium",
                evidence=(
                    f"Missed a question on {item.concept}: chose "
                    f"{item.chosen or '—'} ({item.chosen_text}), correct was "
                    f"{item.correct} ({item.correct_text})."
                ),
                suggested_remediation=remediation,
            ),
        )
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
        trace: LlmTraceContext | None = None,
        locale: str | None = None,
    ) -> KnowledgeGapClassification:
        system = gap_classifier_system(locale)
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
            trace=trace,
            operation="gap_classify",
        )

    async def classify(
        self,
        *,
        node_title: str,
        learner_summary: str | None,
        wrong_items: list[WrongAnswerItem],
        trace: LlmTraceContext | None = None,
        locale: str | None = None,
    ) -> KnowledgeGapClassification:
        return await asyncio.to_thread(
            self._invoke,
            node_title=node_title,
            learner_summary=learner_summary,
            wrong_items=wrong_items,
            trace=trace,
            locale=locale,
        )


def pin_gap_concepts(
    classification: KnowledgeGapClassification,
    wrong_items: list[WrongAnswerItem],
    *,
    locale: str | None = None,
) -> KnowledgeGapClassification:
    """Keep a gap only when its concept is the missed question's concept.

    A paraphrased concept is replaced by the deterministic fallback for that
    miss. The ledger matches on the exact string.
    """
    seen: set[str] = set()
    misses: list[WrongAnswerItem] = []
    for item in wrong_items:
        if item.concept in seen:
            continue
        seen.add(item.concept)
        misses.append(item)
    by_concept = {gap.concept: gap for gap in classification.gaps if gap.concept in seen}
    gaps: list[KnowledgeGapDraft] = []
    missing: list[WrongAnswerItem] = []
    for item in misses:
        pinned = by_concept.get(item.concept)
        if pinned is None:
            missing.append(item)
        else:
            gaps.append(pinned)
    if missing:
        gaps.extend(_fallback_classification(missing, locale=locale).gaps)
    return KnowledgeGapClassification(gaps=gaps)


def classify_gaps(
    *,
    node_title: str,
    learner_summary: str | None,
    wrong_items: list[WrongAnswerItem],
    trace: LlmTraceContext | None = None,
    locale: str | None = None,
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
        return _fallback_classification(wrong_items, locale=locale)
    try:
        drafted = classifier._invoke(
            node_title=node_title,
            learner_summary=learner_summary,
            wrong_items=wrong_items,
            trace=trace,
            locale=locale,
        )
    except Exception:
        return _fallback_classification(wrong_items, locale=locale)
    return pin_gap_concepts(drafted, wrong_items, locale=locale)
