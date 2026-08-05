"""Must-have coverage + post-forge inject (CAR-17).

Coverage is measured **pre-inject** (LLM/planner quality). Inject B merges
missing must-have catalog nodes into the student-facing artifact.
"""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from typing import Any

from career_forge.paths import normalize_catalog_track_id
from career_forge.schemas.common import Priority, SkillStatus, UserSkillNode
from career_forge.services.lean_forge import load_must_have_ids
from career_forge.services.roadmap.catalog import load_roadmap_catalog

DEFAULT_COVERAGE_PASS_BAR = 0.70


@dataclass(frozen=True)
class CoverageResult:
    """Pre-inject must-have coverage for one forge output."""

    goal_id: str
    must_have_ids: list[str]
    forged_ids: list[str]
    hit_ids: list[str]
    missing_ids: list[str]
    coverage: float
    pass_bar: float = DEFAULT_COVERAGE_PASS_BAR

    @property
    def passed(self) -> bool:
        return self.coverage >= self.pass_bar


def forged_node_ids(graph: Sequence[UserSkillNode] | Sequence[dict[str, Any]]) -> list[str]:
    """Extract node ids from UserSkillNode list or graph_ready dicts."""
    ids: list[str] = []
    for node in graph:
        if isinstance(node, UserSkillNode):
            ids.append(node.node_id)
        elif isinstance(node, dict) and node.get("node_id"):
            ids.append(str(node["node_id"]))
    return ids


def compute_must_have_coverage(
    must_have_ids: Sequence[str],
    forged_ids: Iterable[str],
    *,
    goal_id: str = "",
    pass_bar: float = DEFAULT_COVERAGE_PASS_BAR,
) -> CoverageResult:
    """Share of must-have ids present in forged node ids (definition A)."""
    must = [str(node_id) for node_id in must_have_ids if str(node_id).strip()]
    forged = {str(node_id) for node_id in forged_ids if str(node_id).strip()}
    if not must:
        return CoverageResult(
            goal_id=goal_id,
            must_have_ids=[],
            forged_ids=sorted(forged),
            hit_ids=[],
            missing_ids=[],
            coverage=1.0,
            pass_bar=pass_bar,
        )
    hit = [node_id for node_id in must if node_id in forged]
    missing = [node_id for node_id in must if node_id not in forged]
    return CoverageResult(
        goal_id=goal_id,
        must_have_ids=list(must),
        forged_ids=sorted(forged),
        hit_ids=hit,
        missing_ids=missing,
        coverage=len(hit) / len(must),
        pass_bar=pass_bar,
    )


def coverage_for_goal(
    goal_id: str,
    forged_ids: Iterable[str],
    *,
    pass_bar: float = DEFAULT_COVERAGE_PASS_BAR,
    must_have_ids: Sequence[str] | None = None,
) -> CoverageResult:
    """Load frozen must-haves for ``goal_id`` and compute coverage."""
    seeds = list(must_have_ids) if must_have_ids is not None else load_must_have_ids(goal_id)
    return compute_must_have_coverage(
        seeds,
        forged_ids,
        goal_id=goal_id,
        pass_bar=pass_bar,
    )


def inject_missing_must_haves(
    graph: list[UserSkillNode],
    must_have_ids: Sequence[str],
    *,
    track_id: str | None,
    catalog: dict[str, Any] | None = None,
) -> list[UserSkillNode]:
    """Append missing must-have catalog nodes; add edges when prereq already present.

    Deterministic — no LLM. Preserves existing graph order; new nodes append.
    """
    resolved_track = normalize_catalog_track_id(track_id)
    catalog_data = catalog if catalog is not None else load_roadmap_catalog(resolved_track)
    by_id = {
        str(node["id"]): node
        for node in (catalog_data.get("nodes") or [])
        if isinstance(node, dict) and node.get("id")
    }

    present = {node.node_id for node in graph}
    out = list(graph)

    for must_id in must_have_ids:
        node_id = str(must_id)
        if node_id in present:
            continue
        catalog_node = by_id.get(node_id)
        if catalog_node is None:
            continue

        catalog_prereqs = [
            str(prereq)
            for prereq in (catalog_node.get("prerequisites") or [])
            if prereq
        ]
        # Only keep edges to nodes already in the forged graph.
        edge_prereqs = [prereq for prereq in catalog_prereqs if prereq in present]

        out.append(
            UserSkillNode(
                node_id=node_id,
                title=str(catalog_node.get("title") or node_id),
                status=SkillStatus.BLOQUEADO,
                mastery_score=0,
                priority=Priority.MEDIUM,
                rationale="Injected must-have (CAR-17)",
                prerequisites=edge_prereqs,
            ),
        )
        present.add(node_id)

    return out


def apply_must_have_inject(
    graph: list[UserSkillNode],
    *,
    goal_id: str,
    track_id: str | None,
    must_have_ids: Sequence[str] | None = None,
) -> tuple[list[UserSkillNode], CoverageResult]:
    """Measure pre-inject coverage, then inject missing must-haves.

    Returns ``(post_inject_graph, pre_inject_coverage)``.
    """
    seeds = list(must_have_ids) if must_have_ids is not None else load_must_have_ids(goal_id)
    pre = compute_must_have_coverage(seeds, forged_node_ids(graph), goal_id=goal_id)
    injected = inject_missing_must_haves(graph, seeds, track_id=track_id)
    return injected, pre
