"""Unit tests — roadmap service and HTTP API (HAC-9)."""

from __future__ import annotations

from types import SimpleNamespace

from career_forge.schemas.common import Priority, SkillStatus, UserSkillNode
from career_forge.schemas.roadmap import RoadmapCategory, RoadmapNode, RoadmapResponse, RoadmapTrack
from career_forge.services.planning import _roadmap_to_graph, _apply_graph_to_roadmap
from career_forge.services.roadmap import (
    _catalog_node_from_generated_row,
    _checklist_counts,
    _delete_stale_generated_rows,
    _enrich_checklist_items,
    _generated_row_sort_order,
    build_roadmap_from_catalog,
)


class TestRoadmapCatalog:
    def test_build_roadmap_from_catalog_has_nodes(self) -> None:
        roadmap = build_roadmap_from_catalog()
        assert roadmap.track.id == "backend-beginner"
        assert len(roadmap.nodes) >= 6
        node_ids = {node.node_id for node in roadmap.nodes}
        assert "http" in node_ids
        assert "final" in node_ids

    def test_demo_state_marks_http_in_progress(self) -> None:
        roadmap = build_roadmap_from_catalog()
        http = next(n for n in roadmap.nodes if n.node_id == "http")
        assert http.status == SkillStatus.EM_ESTUDO
        assert http.mastery_score == 42

    def test_demo_state_marks_rest_ready_to_validate(self) -> None:
        roadmap = build_roadmap_from_catalog()
        rest = next(n for n in roadmap.nodes if n.node_id == "rest")
        assert rest.status == SkillStatus.VALIDAR


def test_get_roadmap_api(client) -> None:
    response = client.get("/roadmap/?user_id=demo-ana")
    assert response.status_code == 200
    payload = response.json()
    assert payload["track"]["id"] == "backend-beginner"
    assert len(payload["nodes"]) >= 6
    assert payload["nodes"][0]["node_id"]


def test_sync_roadmap_api(client) -> None:
    nodes = [
        UserSkillNode(
            node_id="http",
            title="HTTP básico",
            status=SkillStatus.RECOMENDADO,
            mastery_score=55,
        ),
    ]
    response = client.post(
        "/roadmap/sync",
        json={"user_id": "demo-ana", "nodes": [n.model_dump() for n in nodes]},
    )
    assert response.status_code == 200
    payload = response.json()
    http = next(n for n in payload["nodes"] if n["node_id"] == "http")
    assert http["mastery_score"] == 55


def test_generated_rows_keep_persisted_sort_order_and_evidence() -> None:
    row = SimpleNamespace(
        skill_node_id="python-ai",
        evidence=[
            {"type": "metadata", "sort_order": 4},
            {
                "type": "task",
                "title": "Criar notebook",
                "outcome": "Publicar notebook",
            },
        ],
        skill_node=SimpleNamespace(
            title="Python para IA",
            prerequisites=["setup"],
            sort_order=99,
        ),
        rationale="Base para IA.",
    )

    catalog_node = _catalog_node_from_generated_row(row)

    assert _generated_row_sort_order(row) == 4
    assert catalog_node["id"] == "python-ai"
    assert catalog_node["sort_order"] == 4
    assert catalog_node["outcomes"] == ["Publicar notebook"]


def test_delete_stale_generated_rows_removes_only_old_generated_rows() -> None:
    generated = SimpleNamespace(skill_node=SimpleNamespace(track_id="ai-generated"))
    catalog = SimpleNamespace(skill_node=SimpleNamespace(track_id="backend-beginner"))
    kept = SimpleNamespace(skill_node=SimpleNamespace(track_id="ai-generated"))
    deleted: list[object] = []
    session = SimpleNamespace(delete=lambda row: deleted.append(row))

    _delete_stale_generated_rows(
        session,
        {
            "old-generated": generated,
            "catalog-node": catalog,
            "new-generated": kept,
        },
        {"new-generated"},
    )

    assert deleted == [generated]


def test_planning_roundtrip_preserves_tasks_and_references() -> None:
    roadmap = RoadmapResponse(
        track=RoadmapTrack(id="ai", title="AI"),
        categories=[RoadmapCategory(id="ai_generated", label="AI")],
        nodes=[
            RoadmapNode(
                node_id="python-ai",
                title="Python para IA",
                category="ai_generated",
                description="Base",
                status=SkillStatus.RECOMENDADO,
                mastery_score=0,
                priority=Priority.HIGH,
                tasks=[{"title": "Criar notebook"}],
                references=[{"title": "Python docs", "url": "https://docs.python.org"}],
            ),
        ],
    )
    graph = _roadmap_to_graph(roadmap)
    updated = _apply_graph_to_roadmap(roadmap, graph)

    assert graph[0].tasks == [{"title": "Criar notebook"}]
    assert graph[0].references[0]["title"] == "Python docs"
    assert updated.nodes[0].tasks == [{"title": "Criar notebook"}]
    assert updated.nodes[0].references[0]["url"] == "https://docs.python.org"


def test_enrich_checklist_items_adds_ids_and_done_state() -> None:
    items = [{"title": "Ler docs"}]
    progress = {"tasks": {"task-0": True}}
    enriched = _enrich_checklist_items(items, "tasks", progress)
    assert enriched[0]["id"] == "task-0"
    assert enriched[0]["done"] is True


def test_checklist_counts_completed_items() -> None:
    tasks = [{"id": "task-0", "done": True, "title": "A"}]
    references = [{"id": "ref-0", "done": False, "title": "B", "url": "https://x"}]
    completed, total = _checklist_counts(tasks, references)
    assert completed == 1
    assert total == 2


def test_patch_checklist_api_persists_progress(client) -> None:
    nodes = [
        UserSkillNode(
            node_id="http",
            title="HTTP básico",
            status=SkillStatus.RECOMENDADO,
            mastery_score=10,
            tasks=[{"title": "Montar request"}],
            references=[{"title": "MDN HTTP", "url": "https://developer.mozilla.org"}],
        ),
    ]
    sync_response = client.post(
        "/roadmap/sync",
        json={"user_id": "checklist-user", "nodes": [n.model_dump() for n in nodes]},
    )
    assert sync_response.status_code == 200
    synced = sync_response.json()
    http = next(n for n in synced["nodes"] if n["node_id"] == "http")
    task_id = http["tasks"][0]["id"]
    ref_id = http["references"][0]["id"]

    toggle_task = client.patch(
        "/roadmap/nodes/http/checklist",
        json={
            "user_id": "checklist-user",
            "item_type": "task",
            "item_id": task_id,
            "done": True,
        },
    )
    assert toggle_task.status_code == 200
    after_task = next(n for n in toggle_task.json()["nodes"] if n["node_id"] == "http")
    assert after_task["checklist_completed"] == 1
    assert after_task["tasks"][0]["done"] is True

    toggle_ref = client.patch(
        "/roadmap/nodes/http/checklist",
        json={
            "user_id": "checklist-user",
            "item_type": "reference",
            "item_id": ref_id,
            "done": True,
        },
    )
    assert toggle_ref.status_code == 200
    after_ref = next(n for n in toggle_ref.json()["nodes"] if n["node_id"] == "http")
    assert after_ref["checklist_completed"] == 2
    assert after_ref["checklist_total"] == 2


def test_patch_checklist_rejects_unknown_item(client) -> None:
    response = client.patch(
        "/roadmap/nodes/http/checklist",
        json={
            "user_id": "demo-ana",
            "item_type": "task",
            "item_id": "missing-task",
            "done": True,
        },
    )
    assert response.status_code == 400

