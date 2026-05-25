"""Seed skill_nodes from data/roadmap.json and optional demo user Ana."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from sqlalchemy import select

from career_forge.db.session import SessionLocal
from career_forge.db.models.profile import Profile
from career_forge.db.models.skill_node import SkillNode
from career_forge.db.models.user import User
from career_forge.db.models.user_skill_node import UserSkillNode

REPO_ROOT = Path(__file__).resolve().parents[3]
ROADMAP_PATH = REPO_ROOT / "data" / "roadmap.json"

DEMO_ANA_EXTERNAL_ID = "demo-ana"
DEMO_ANA_SKILL_STATE: dict[str, dict] = {
    "js": {"status": "aprovado", "mastery_score": 65, "priority": "low"},
    "git": {"status": "aprovado", "mastery_score": 78, "priority": "low"},
    "http": {
        "status": "recomendado",
        "mastery_score": 42,
        "priority": "high",
        "rationale": "Lacuna principal — foco do onboarding",
    },
    "db": {"status": "recomendado", "mastery_score": 35, "priority": "high"},
    "rest": {"status": "bloqueado", "mastery_score": 0, "priority": None},
    "auth": {"status": "bloqueado", "mastery_score": 0, "priority": None},
    "final": {"status": "bloqueado", "mastery_score": 0, "priority": None},
}


def load_roadmap(path: Path = ROADMAP_PATH) -> dict:
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def seed_skill_nodes(session, roadmap: dict | None = None) -> int:
    roadmap = roadmap or load_roadmap()
    track_id = roadmap["track"]["id"]
    count = 0

    for node in roadmap["nodes"]:
        existing = session.get(SkillNode, node["id"])
        payload = {
            "track_id": track_id,
            "title": node["title"],
            "category": node["category"],
            "description": node.get("description"),
            "icon": node.get("icon"),
            "side": node.get("side"),
            "sort_order": node.get("sort_order", 0),
            "prerequisites": node.get("prerequisites", []),
            "outcomes": node.get("outcomes", []),
            "rubric": node.get("rubric", []),
        }
        if existing:
            for key, value in payload.items():
                setattr(existing, key, value)
        else:
            session.add(SkillNode(id=node["id"], **payload))
        count += 1

    session.commit()
    return count


def seed_demo_ana(session) -> User:
    user = session.scalar(select(User).where(User.external_id == DEMO_ANA_EXTERNAL_ID))
    if not user:
        user = User(
            external_id=DEMO_ANA_EXTERNAL_ID,
            display_name="Ana",
            email="ana@demo.careerforge.local",
        )
        session.add(user)
        session.flush()

    profile = session.scalar(select(Profile).where(Profile.user_id == user.id))
    if not profile:
        session.add(
            Profile(
                user_id=user.id,
                track_id="backend-beginner",
                goal="Backend para APIs em space tech",
                motivation="Quero construir serviços que alimentem missões espaciais.",
                diagnosis={
                    "fortes": ["JavaScript base", "Git"],
                    "lacunas": ["HTTP", "Banco relacional"],
                    "recomendacao": "Priorizar HTTP e SQL antes de REST.",
                },
            )
        )

    for node_id, state in DEMO_ANA_SKILL_STATE.items():
        usn = session.scalar(
            select(UserSkillNode).where(
                UserSkillNode.user_id == user.id,
                UserSkillNode.skill_node_id == node_id,
            )
        )
        if usn:
            usn.status = state["status"]
            usn.mastery_score = state["mastery_score"]
            usn.priority = state.get("priority")
            usn.rationale = state.get("rationale")
        else:
            session.add(
                UserSkillNode(
                    user_id=user.id,
                    skill_node_id=node_id,
                    status=state["status"],
                    mastery_score=state["mastery_score"],
                    priority=state.get("priority"),
                    rationale=state.get("rationale"),
                    evidence=[],
                )
            )

    session.commit()
    return user


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed Career Forge skill graph catalog")
    parser.add_argument(
        "--demo-ana",
        action="store_true",
        help="Create demo user Ana with prototype-aligned skill states",
    )
    parser.add_argument(
        "--roadmap",
        type=Path,
        default=ROADMAP_PATH,
        help="Path to roadmap.json (default: repo data/roadmap.json)",
    )
    args = parser.parse_args()

    roadmap = load_roadmap(args.roadmap)
    session = SessionLocal()
    try:
        node_count = seed_skill_nodes(session, roadmap)
        print(f"Seeded {node_count} skill_nodes for track '{roadmap['track']['id']}'")

        if args.demo_ana:
            user = seed_demo_ana(session)
            print(f"Demo user '{user.display_name}' ({user.external_id}) ready — id={user.id}")
    finally:
        session.close()


if __name__ == "__main__":
    main()
