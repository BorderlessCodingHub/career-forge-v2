"""Catalog multi-track seed + forge scoping (CAR-5)."""

from __future__ import annotations

from career_forge.ai.graphs.roadmap_forge import build_accumulated_graph
from career_forge.paths import list_catalog_paths
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


def test_load_all_catalogs_unique_node_ids() -> None:
    catalogs = load_all_catalogs()
    assert len(catalogs) == 4
    all_ids: list[str] = []
    for catalog in catalogs:
        assert catalog["track"]["id"] in EXPECTED_TRACKS
        assert 6 <= len(catalog["nodes"]) <= 8
        all_ids.extend(node["id"] for node in catalog["nodes"])
    assert len(all_ids) == len(set(all_ids))


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
