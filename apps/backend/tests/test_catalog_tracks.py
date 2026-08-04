"""Catalog multi-track seed + forge scoping (CAR-5)."""

from __future__ import annotations

from career_forge.ai.graphs.roadmap_forge import build_accumulated_graph
from career_forge.paths import list_catalog_paths, normalize_catalog_track_id, roadmap_json_path
from career_forge.schemas.diagnosis import DiagnosisProfile, DiagnosisResponse
from career_forge.services.roadmap.catalog import load_all_catalogs, load_roadmap_catalog

EXPECTED_TRACKS = {
    "rag-engineer-beginner",
    "agent-engineer-beginner",
    "llm-evals-beginner",
    "fine-tuning-beginner",
}


def test_catalog_dir_has_four_tracks() -> None:
    paths = list_catalog_paths()
    track_ids = {path.stem for path in paths}
    assert track_ids == EXPECTED_TRACKS


def test_normalize_goal_slug_to_catalog_track() -> None:
    assert normalize_catalog_track_id("rag-engineer") == "rag-engineer-beginner"
    assert normalize_catalog_track_id("agent-engineer") == "agent-engineer-beginner"
    assert normalize_catalog_track_id("rag-engineer-beginner") == "rag-engineer-beginner"
    assert normalize_catalog_track_id(None) == "rag-engineer-beginner"


def test_roadmap_json_path_aliases_goal_slug() -> None:
    path = roadmap_json_path("rag-engineer")
    assert path.name == "rag-engineer-beginner.json"
    assert path.is_file()


def test_load_all_catalogs_unique_node_ids() -> None:
    catalogs = load_all_catalogs()
    assert len(catalogs) == 4
    all_ids: list[str] = []
    for catalog in catalogs:
        assert catalog["track"]["id"] in EXPECTED_TRACKS
        # CAR-17: 10 nodes/track (= frozen must-have set + catalog gaps)
        assert len(catalog["nodes"]) == 10
        all_ids.extend(node["id"] for node in catalog["nodes"])
    assert len(all_ids) == len(set(all_ids))
    assert len(all_ids) == 40


def test_forge_graph_scoped_to_track_only() -> None:
    for track_id in sorted(EXPECTED_TRACKS):
        catalog = load_roadmap_catalog(track_id)
        node_ids = {node["id"] for node in catalog["nodes"]}
        diagnosis = DiagnosisResponse(
            profile=DiagnosisProfile(
                label="Synthetic",
                track_id=track_id,
                persona_slug="synth",
            ),
            strengths=["motivation"],
            gaps=["practice"],
            starting_priorities=list(node_ids)[:3],
            estimated_mastery={nid: 20 for nid in node_ids},
        )
        graph = build_accumulated_graph(diagnosis)
        graph_ids = {node.node_id for node in graph}
        assert graph_ids == node_ids
        # No bleed from other tracks
        for other in EXPECTED_TRACKS - {track_id}:
            other_ids = {n["id"] for n in load_roadmap_catalog(other)["nodes"]}
            assert graph_ids.isdisjoint(other_ids)


def test_forge_graph_accepts_goal_slug_track_id() -> None:
    """LLM finalize sometimes returns goal slug; forge must still load catalog."""
    diagnosis = DiagnosisResponse(
        profile=DiagnosisProfile(
            label="Drift",
            track_id="rag-engineer",
            persona_slug="drift",
        ),
        strengths=["motivation"],
        gaps=["practice"],
        starting_priorities=["rag-embeddings"],
        estimated_mastery={"rag-embeddings": 20},
    )
    graph = build_accumulated_graph(diagnosis)
    assert {node.node_id for node in graph} == {
        n["id"] for n in load_roadmap_catalog("rag-engineer-beginner")["nodes"]
    }
