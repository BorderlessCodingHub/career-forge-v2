"""ADR-004 — canonical skill content attach + inventory lookup.

Seams: focus_skill_ids, resolve_canonical_ref, load_published_canonical.
"""

from __future__ import annotations

from career_forge.schemas.canonical import CanonicalRef
from career_forge.services.canonical_content import (
    focus_skill_ids,
    load_published_canonical,
    resolve_canonical_ref,
)


def test_must_have_or_diagnosis_gap_is_focus() -> None:
    catalog = [
        {"id": "rag-chunking", "title": "Chunking"},
        {"id": "rag-eval", "title": "Evaluation"},
        {"id": "rag-latency-cost", "title": "Latency & cost"},
    ]

    ids = focus_skill_ids(
        must_have_ids=["rag-chunking"],
        gaps=["Evaluation"],
        starting_priorities=["rag-latency-cost"],
        catalog_nodes=catalog,
    )

    assert ids == {"rag-chunking", "rag-eval", "rag-latency-cost"}


def test_focus_with_published_canonical_attaches_skill_id_only() -> None:
    published = {
        "rag-chunking": CanonicalRef(skill_id="rag-chunking", title="Chunking for RAG"),
    }

    ref = resolve_canonical_ref(
        skill_id="rag-chunking",
        focus_ids={"rag-chunking"},
        published=published,
    )

    assert ref == CanonicalRef(skill_id="rag-chunking", title="Chunking for RAG")


def test_focus_without_canonical_is_silence() -> None:
    ref = resolve_canonical_ref(
        skill_id="rag-chunking",
        focus_ids={"rag-chunking"},
        published={},
    )

    assert ref is None


def test_non_focus_with_canonical_is_silence() -> None:
    published = {
        "rag-chunking": CanonicalRef(skill_id="rag-chunking", title="Chunking for RAG"),
    }

    ref = resolve_canonical_ref(
        skill_id="rag-chunking",
        focus_ids={"rag-eval"},
        published=published,
    )

    assert ref is None


def test_load_published_canonical_requires_sidecar_and_git_body(
    monkeypatch, tmp_path
) -> None:
    import uuid

    from career_forge.db.models.skill_content import SkillContent
    from career_forge.db.session import SessionLocal

    skill_id = f"car94-{uuid.uuid4().hex[:10]}"
    canonical_dir = tmp_path / "canonical"
    canonical_dir.mkdir()
    monkeypatch.setenv("CANONICAL_CONTENT_DIR", str(canonical_dir))
    (canonical_dir / f"{skill_id}.md").write_text(
        f"---\nskill_id: {skill_id}\ntitle: Frontmatter title\n---\n\n# Body\n\nChunk well.\n",
        encoding="utf-8",
    )

    with SessionLocal() as session:
        assert load_published_canonical(session, skill_id) is None

        session.add(
            SkillContent(
                skill_id=skill_id,
                title="Live sidecar title",
                url="https://learn.borderlesscoding.com/rag-chunking",
                published=True,
            )
        )
        session.commit()

        page = load_published_canonical(session, skill_id)
        session.delete(session.get(SkillContent, skill_id))
        session.commit()

    assert page is not None
    assert page.skill_id == skill_id
    assert page.title == "Live sidecar title"
    assert page.url == "https://learn.borderlesscoding.com/rag-chunking"
    assert page.body_markdown.startswith("# Body")
    assert "Frontmatter title" not in page.body_markdown


def test_unpublished_or_missing_body_is_not_published(monkeypatch, tmp_path) -> None:
    import uuid

    from career_forge.db.models.skill_content import SkillContent
    from career_forge.db.session import SessionLocal

    missing_body_id = f"car94-miss-{uuid.uuid4().hex[:8]}"
    draft_id = f"car94-draft-{uuid.uuid4().hex[:8]}"
    canonical_dir = tmp_path / "canonical"
    canonical_dir.mkdir()
    monkeypatch.setenv("CANONICAL_CONTENT_DIR", str(canonical_dir))

    with SessionLocal() as session:
        session.add(
            SkillContent(
                skill_id=missing_body_id,
                title="Eval",
                published=True,
            )
        )
        session.add(
            SkillContent(
                skill_id=draft_id,
                title="Draft",
                published=False,
            )
        )
        session.commit()
        (canonical_dir / f"{draft_id}.md").write_text("# Draft body\n", encoding="utf-8")

        assert load_published_canonical(session, missing_body_id) is None
        assert load_published_canonical(session, draft_id) is None
        assert load_published_canonical(session, "missing") is None

        session.delete(session.get(SkillContent, missing_body_id))
        session.delete(session.get(SkillContent, draft_id))
        session.commit()
