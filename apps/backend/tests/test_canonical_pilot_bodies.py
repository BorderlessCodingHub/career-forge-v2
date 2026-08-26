"""Pilot git bodies in data/canonical/ — renderer-safe, nonempty, catalog ids."""

from __future__ import annotations

import re

from career_forge.paths import canonical_content_dir
from career_forge.services.canonical_content import _canonical_body

PILOT_RAG_SKILLS = (
    "rag-embeddings",
    "rag-chunking",
    "rag-retrieval",
    "rag-eval",
    "rag-production",
)

_NUMBERED = re.compile(r"^\d+\.\s+")
_TABLE = re.compile(r"^\|")


def test_pilot_rag_canonical_bodies_exist_and_are_learn_safe() -> None:
    root = canonical_content_dir()
    for skill_id in PILOT_RAG_SKILLS:
        raw = (root / f"{skill_id}.md").read_text(encoding="utf-8")
        assert f"skill_id: {skill_id}" in raw.split("---", 2)[1]
        body = _canonical_body(skill_id)
        assert body is not None
        for heading in ("## Knowledge", "## Practice", "## Check", "## Done when", "## Primary source"):
            assert heading in body, f"{skill_id} missing {heading} (teach lesson shape)"
        assert "https://" in body
        assert "ask a follow-up" in body.lower()
        for line in body.splitlines():
            stripped = line.strip()
            assert not _NUMBERED.match(stripped), f"{skill_id}: numbered list will not render as a list"
            assert not _TABLE.match(stripped), f"{skill_id}: tables are not rendered on /learn"
