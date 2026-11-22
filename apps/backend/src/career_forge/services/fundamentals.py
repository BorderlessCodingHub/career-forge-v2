"""Load one Fundamentals edition from git. A forge does not write it (ADR-010)."""

from __future__ import annotations

from career_forge.errors import NotFoundError
from career_forge.paths import fundamentals_content_dir
from career_forge.schemas.fundamentals import FundamentalsGuide, FundamentalsLocale

GOAL_IDS = ("rag-engineer", "agent-engineer", "llm-evals", "fine-tuning")


class FundamentalsNotFoundError(NotFoundError):
    """This Goal has no edition the learner can read."""


def _strip_frontmatter(raw: str) -> str:
    text = raw.lstrip("\ufeff")
    if not text.startswith("---"):
        body = text.strip()
        return f"{body}\n" if body else ""
    rest = text[3:]
    if rest.startswith("\n"):
        rest = rest[1:]
    closing = rest.find("\n---")
    if closing < 0:
        body = text.strip()
        return f"{body}\n" if body else ""
    body = rest[closing + 4 :].strip()
    return f"{body}\n" if body else ""


def _edition(goal_id: str, locale: str) -> str | None:
    path = fundamentals_content_dir() / goal_id / f"{locale}.md"
    if not path.is_file():
        return None
    body = _strip_frontmatter(path.read_text(encoding="utf-8"))
    if not body.strip():
        return None
    return body


def load_fundamentals(goal_id: str, locale: FundamentalsLocale) -> FundamentalsGuide | None:
    """Return the requested edition, or the other language when that edition is missing.

    None when the Goal has no edition at all.
    """
    if goal_id not in GOAL_IDS:
        return None
    other: FundamentalsLocale = "en" if locale == "pt-BR" else "pt-BR"
    for served in (locale, other):
        body = _edition(goal_id, served)
        if body is not None:
            return FundamentalsGuide(goal_id=goal_id, locale=served, body_markdown=body)
    return None


def list_published_goal_ids() -> list[str]:
    """Catalog order. A Goal is published when either locale has an edition."""
    published: list[str] = []
    for goal_id in GOAL_IDS:
        if load_fundamentals(goal_id, "en") is not None:
            published.append(goal_id)
    return published


def require_fundamentals(goal_id: str, locale: FundamentalsLocale) -> FundamentalsGuide:
    guide = load_fundamentals(goal_id, locale)
    if guide is None:
        raise FundamentalsNotFoundError("fundamentals guide not found")
    return guide
