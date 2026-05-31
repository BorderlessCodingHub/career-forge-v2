"""Canonical `UserSkillNode.evidence` envelope + legacy read adapter (HAC-85).

Historically `evidence` had two shapes: a list of typed items
(`[{type: metadata}, {type: task}, {type: reference}, {type: validation}]`,
with remediation tasks injected into the same list) and a plain dict summary
(`{strengths, gaps, next_action}`). Callers branched on `isinstance(evidence,
dict|list)` everywhere — the most pervasive leaked persistence abstraction.

This module defines the single canonical envelope::

    {
        "checklist":   [ {type: task|reference, ...} ],   # StudyPlan items
        "validation":  {strengths, gaps, next_action, [mock_interview]} | None,
        "remediation": [ {type: task, id: gap-rem-*, source: gap, ...} ],
        "metadata":    {"sort_order": int} | {},
    }

`read_evidence` normalizes ANY stored shape (canonical, legacy list, legacy
dict, None) into `EvidenceEnvelope`, so readers never branch on shape again.
Writers always emit `to_storage()` — legacy rows migrate lazily on next write.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

REMEDIATION_PREFIX = "gap-rem-"


def _format_checklist_item(item: dict[str, Any]) -> dict[str, str]:
    """Strip the internal `type` tag and stringify values for UI checklist rows."""
    return {str(key): str(value) for key, value in item.items() if key != "type" and value is not None}


@dataclass
class EvidenceEnvelope:
    """Canonical, shape-agnostic view of a node's evidence."""

    checklist: list[dict[str, Any]] = field(default_factory=list)
    validation: dict[str, Any] | None = None
    remediation: list[dict[str, Any]] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def task_items(self) -> list[dict[str, Any]]:
        """Checklist tasks plus remediation tasks (both surface as node tasks)."""
        tasks = [item for item in self.checklist if item.get("type") == "task"]
        return [*tasks, *self.remediation]

    def reference_items(self) -> list[dict[str, Any]]:
        return [item for item in self.checklist if item.get("type") == "reference"]

    def validation_summary(self) -> dict[str, Any]:
        return dict(self.validation) if self.validation else {}

    def sort_order(self) -> int | None:
        raw = self.metadata.get("sort_order")
        if raw is None:
            return None
        try:
            return int(raw)
        except (TypeError, ValueError):
            return None

    def to_storage(self) -> dict[str, Any]:
        return {
            "checklist": self.checklist,
            "validation": self.validation,
            "remediation": self.remediation,
            "metadata": self.metadata,
        }


def _read_legacy_list(raw: list) -> EvidenceEnvelope:
    checklist: list[dict[str, Any]] = []
    remediation: list[dict[str, Any]] = []
    validation: dict[str, Any] | None = None
    metadata: dict[str, Any] = {}
    for item in raw:
        if not isinstance(item, dict):
            continue
        item_type = item.get("type")
        if item_type == "metadata":
            metadata = {key: value for key, value in item.items() if key != "type"}
        elif item_type == "validation":
            validation = {key: value for key, value in item.items() if key != "type"}
        elif item_type in ("task", "reference"):
            is_remediation = item_type == "task" and str(item.get("id", "")).startswith(
                REMEDIATION_PREFIX,
            )
            (remediation if is_remediation else checklist).append(item)
    return EvidenceEnvelope(
        checklist=checklist,
        validation=validation,
        remediation=remediation,
        metadata=metadata,
    )


def read_evidence(raw: list | dict | None) -> EvidenceEnvelope:
    """Normalize stored evidence (canonical / legacy list / legacy dict / None)."""
    if raw is None:
        return EvidenceEnvelope()
    if isinstance(raw, dict):
        if "checklist" in raw or "remediation" in raw or "metadata" in raw:
            return EvidenceEnvelope(
                checklist=list(raw.get("checklist") or []),
                validation=raw.get("validation"),
                remediation=list(raw.get("remediation") or []),
                metadata=dict(raw.get("metadata") or {}),
            )
        # Legacy plain summary: {strengths, gaps, next_action, [mock_interview]}.
        return EvidenceEnvelope(validation=dict(raw))
    if isinstance(raw, list):
        return _read_legacy_list(raw)
    return EvidenceEnvelope()
