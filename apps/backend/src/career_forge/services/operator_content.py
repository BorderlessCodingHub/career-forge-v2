"""Content desk sidecar over the seeded skill catalog (CAR-79)."""

from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session

from career_forge.auth.operator_session import OperatorPrincipal
from career_forge.db.models.skill_content import SkillContent
from career_forge.errors import ConflictError, ForbiddenError, NotFoundError
from career_forge.paths import canonical_content_dir
from career_forge.schemas.operator_content import OperatorContentPatch
from career_forge.services.roadmap.catalog import load_all_catalogs


@dataclass(frozen=True)
class ContentSkillSnapshot:
    skill_id: str
    track_id: str
    title: str
    description: str | None
    url: str | None
    published: bool
    body_present: bool


@dataclass(frozen=True)
class CatalogSkillDefinition:
    skill_id: str
    track_id: str
    title: str
    description: str | None
    sort_order: int


class CatalogSkillNotFoundError(NotFoundError):
    pass


class CanonicalBodyMissingError(ConflictError):
    pass


def require_content_role(principal: OperatorPrincipal) -> None:
    if principal.desk_roles not in {"editor", "both"}:
        raise ForbiddenError(
            "Content desk role required",
            code="content_desk_forbidden",
        )


def canonical_body_present(skill_id: str) -> bool:
    return (canonical_content_dir() / f"{skill_id}.md").is_file()


def _catalog_inventory() -> list[CatalogSkillDefinition]:
    inventory: list[CatalogSkillDefinition] = []
    for catalog in load_all_catalogs():
        track_id = str(catalog["track"]["id"])
        for node in catalog.get("nodes", []):
            inventory.append(
                CatalogSkillDefinition(
                    skill_id=str(node["id"]),
                    track_id=track_id,
                    title=str(node["title"]),
                    description=(
                        str(node["description"]) if node.get("description") else None
                    ),
                    sort_order=int(node.get("sort_order", 0)),
                )
            )
    return sorted(
        inventory,
        key=lambda skill: (skill.track_id, skill.sort_order, skill.skill_id),
    )


def list_content_skills(
    session: Session,
    *,
    principal: OperatorPrincipal,
) -> list[ContentSkillSnapshot]:
    require_content_role(principal)
    inventory = _catalog_inventory()
    content_by_id = {
        content.skill_id: content
        for content in session.scalars(
            select(SkillContent).where(
                SkillContent.skill_id.in_([skill.skill_id for skill in inventory])
            )
        ).all()
    }
    snapshots: list[ContentSkillSnapshot] = []
    for skill in inventory:
        content = content_by_id.get(skill.skill_id)
        snapshots.append(
            ContentSkillSnapshot(
                skill_id=skill.skill_id,
                track_id=skill.track_id,
                title=content.title if content else skill.title,
                description=skill.description,
                url=content.url if content else None,
                published=bool(content.published) if content else False,
                body_present=canonical_body_present(skill.skill_id),
            )
        )
    return snapshots


def update_content_skill(
    session: Session,
    *,
    principal: OperatorPrincipal,
    skill_id: str,
    patch: OperatorContentPatch,
) -> ContentSkillSnapshot:
    require_content_role(principal)
    definition = next(
        (skill for skill in _catalog_inventory() if skill.skill_id == skill_id),
        None,
    )
    if definition is None:
        raise CatalogSkillNotFoundError("catalog skill not found")

    body_present = canonical_body_present(definition.skill_id)
    content = session.get(SkillContent, definition.skill_id)
    published = content.published if content else False
    if "published" in patch.model_fields_set:
        published = bool(patch.published)
    if published and not body_present:
        raise CanonicalBodyMissingError(
            "published content requires a git-owned canonical body"
        )

    if content is None:
        content = SkillContent(
            skill_id=definition.skill_id,
            title=definition.title,
            url=None,
            published=False,
        )
        session.add(content)

    if "title" in patch.model_fields_set:
        content.title = str(patch.title).strip()
    if "url" in patch.model_fields_set:
        content.url = str(patch.url) if patch.url is not None else None
    if "published" in patch.model_fields_set:
        content.published = bool(patch.published)

    session.flush()
    return ContentSkillSnapshot(
        skill_id=definition.skill_id,
        track_id=definition.track_id,
        title=content.title,
        description=definition.description,
        url=content.url,
        published=bool(content.published),
        body_present=body_present,
    )
