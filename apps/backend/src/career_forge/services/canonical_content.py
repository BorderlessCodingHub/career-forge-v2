"""Canonical skill content inventory + deterministic attach (ADR-004).

Content unit is catalog ``skill_id`` (N learners → 1 piece). Forge does not
create content. Attach is rule + lookup: focus (must-have or diagnosis gap)
and a published git body. Missing content is silence.
"""

from __future__ import annotations

from typing import Any, Iterable, Mapping, Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

from career_forge.db.models.skill_content import SkillContent
from career_forge.errors import NotFoundError
from career_forge.paths import canonical_content_dir
from career_forge.schemas.canonical import CanonicalPage, CanonicalRef


class CanonicalNotFoundError(NotFoundError):
    """No published canonical body for this skill_id."""


def _match_keys(*groups: Iterable[str]) -> set[str]:
    keys: set[str] = set()
    for group in groups:
        for item in group:
            stripped = item.strip()
            if stripped:
                keys.add(stripped.casefold())
    return keys


def focus_skill_ids(
    *,
    must_have_ids: Sequence[str],
    gaps: Sequence[str],
    starting_priorities: Sequence[str],
    catalog_nodes: Sequence[Mapping[str, Any]],
) -> set[str]:
    """Focus = must-have or diagnosis-identified skill (gap / starting priority)."""
    ids = {item.strip() for item in must_have_ids if item.strip()}
    catalog_ids = {str(node["id"]) for node in catalog_nodes if node.get("id")}
    for priority in starting_priorities:
        stripped = priority.strip()
        if stripped in catalog_ids:
            ids.add(stripped)
    keys = _match_keys(gaps, starting_priorities)
    for node in catalog_nodes:
        node_id = str(node.get("id") or "")
        title = str(node.get("title") or "")
        if not node_id:
            continue
        if node_id.casefold() in keys or title.casefold() in keys:
            ids.add(node_id)
    return ids


def resolve_canonical_ref(
    *,
    skill_id: str,
    focus_ids: set[str],
    published: Mapping[str, CanonicalRef],
) -> CanonicalRef | None:
    """Attach only when the node is focus and a published canonical exists."""
    if skill_id not in focus_ids:
        return None
    return published.get(skill_id)


def _strip_frontmatter(raw: str) -> str:
    text = raw.lstrip("\ufeff")
    if not text.startswith("---"):
        return text.strip() + ("\n" if text.strip() else "")
    rest = text[3:]
    if rest.startswith("\n"):
        rest = rest[1:]
    closing = rest.find("\n---")
    if closing < 0:
        return text.strip() + "\n"
    body = rest[closing + 4 :].lstrip("\n")
    return body.strip() + ("\n" if body.strip() else "")


def _canonical_body(skill_id: str) -> str | None:
    path = canonical_content_dir() / f"{skill_id}.md"
    if not path.is_file():
        return None
    body = _strip_frontmatter(path.read_text(encoding="utf-8"))
    if not body.strip():
        return None
    return body


def load_published_canonical(session: Session, skill_id: str) -> CanonicalPage | None:
    """Return the published piece for ``skill_id``, or None (silence)."""
    content = session.get(SkillContent, skill_id)
    if content is None or not content.published:
        return None
    body = _canonical_body(skill_id)
    if body is None:
        return None
    return CanonicalPage(
        skill_id=skill_id,
        title=content.title,
        url=content.url,
        body_markdown=body,
    )


def published_canonical_refs(session: Session) -> dict[str, CanonicalRef]:
    """skill_id → live title for every published nonempty body on disk."""
    rows = session.scalars(select(SkillContent).where(SkillContent.published.is_(True))).all()
    refs: dict[str, CanonicalRef] = {}
    for row in rows:
        if _canonical_body(row.skill_id) is None:
            continue
        refs[row.skill_id] = CanonicalRef(skill_id=row.skill_id, title=row.title)
    return refs


def require_published_canonical(session: Session, skill_id: str) -> CanonicalPage:
    page = load_published_canonical(session, skill_id)
    if page is None:
        raise CanonicalNotFoundError("canonical skill content not found")
    return page
