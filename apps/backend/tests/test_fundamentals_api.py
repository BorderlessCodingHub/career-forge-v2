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
PORTUGUESE_BODY = (
    "## Recupere antes de gerar\n"
    "\n"
    "O recuperador corre antes de o modelo escrever.\n"
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


def test_missing_edition_falls_back_to_the_other_locale(
    client: TestClient, monkeypatch, tmp_path
) -> None:
    root = tmp_path / "fundamentals"
    _write_edition(root, "rag-engineer", "en", ENGLISH_BODY)
    monkeypatch.setenv("FUNDAMENTALS_CONTENT_DIR", str(root))

    fallback = client.get("/fundamentals/rag-engineer", params={"locale": "pt-BR"})
    assert fallback.status_code == 200, fallback.text
    assert fallback.json() == {
        "goal_id": "rag-engineer",
        "locale": "en",
        "body_markdown": ENGLISH_BODY,
    }

    _write_edition(root, "agent-engineer", "pt-BR", PORTUGUESE_BODY)
    other_way = client.get("/fundamentals/agent-engineer", params={"locale": "en"})
    assert other_way.status_code == 200, other_way.text
    assert other_way.json() == {
        "goal_id": "agent-engineer",
        "locale": "pt-BR",
        "body_markdown": PORTUGUESE_BODY,
    }

    _write_edition(root, "rag-engineer", "pt-BR", PORTUGUESE_BODY)
    requested = client.get("/fundamentals/rag-engineer", params={"locale": "pt-BR"})
    assert requested.status_code == 200, requested.text
    assert requested.json()["locale"] == "pt-BR"
    assert requested.json()["body_markdown"] == PORTUGUESE_BODY
