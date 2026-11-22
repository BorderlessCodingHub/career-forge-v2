"""LABS01-219 — a signed-in learner reads one Fundamentals guide.

Seam: GET /fundamentals/{goal_id}?locale=
"""

from __future__ import annotations

from fastapi.testclient import TestClient

ENGLISH_BODY = (
    "## Retrieve before you generate\n"
    "\n"
    "The retriever runs before the model writes.\n"
)


def _write_edition(root, goal_id: str, locale: str, body: str) -> None:
    directory = root / goal_id
    directory.mkdir(parents=True, exist_ok=True)
    (directory / f"{locale}.md").write_text(body, encoding="utf-8")


def test_signed_in_read_returns_the_requested_edition(
    client: TestClient, monkeypatch, tmp_path
) -> None:
    root = tmp_path / "fundamentals"
    _write_edition(
        root,
        "rag-engineer",
        "en",
        "---\ntitle: ignored by the learner\n---\n" + ENGLISH_BODY,
    )
    monkeypatch.setenv("FUNDAMENTALS_CONTENT_DIR", str(root))

    found = client.get("/fundamentals/rag-engineer", params={"locale": "en"})

    assert found.status_code == 200, found.text
    assert found.json() == {
        "goal_id": "rag-engineer",
        "locale": "en",
        "body_markdown": ENGLISH_BODY,
    }
