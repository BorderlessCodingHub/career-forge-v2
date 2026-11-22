"""LABS01-219 — a signed-in learner reads one Fundamentals guide.

Seam: GET /fundamentals/{goal_id}?locale=
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from fastapi.testclient import TestClient

from career_forge.auth.providers import get_auth_provider
from career_forge.db.repositories.user import ensure_user
from career_forge.db.session import SessionLocal

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


def test_goal_with_no_edition_is_absent(
    client: TestClient, monkeypatch, tmp_path
) -> None:
    root = tmp_path / "fundamentals"
    _write_edition(root, "rag-engineer", "en", "---\ntitle: blank\n---\n\n")
    monkeypatch.setenv("FUNDAMENTALS_CONTENT_DIR", str(root))

    blank = client.get("/fundamentals/rag-engineer", params={"locale": "en"})
    assert blank.status_code == 404
    assert blank.json()["detail"] == "fundamentals guide not found"

    missing = client.get("/fundamentals/llm-evals", params={"locale": "pt-BR"})
    assert missing.status_code == 404
    assert missing.json()["detail"] == "fundamentals guide not found"


def test_unauthenticated_read_is_rejected(
    raw_client: TestClient, monkeypatch, tmp_path
) -> None:
    root = tmp_path / "fundamentals"
    _write_edition(root, "rag-engineer", "en", ENGLISH_BODY)
    monkeypatch.setenv("FUNDAMENTALS_CONTENT_DIR", str(root))

    denied = raw_client.get("/fundamentals/rag-engineer", params={"locale": "en"})

    assert denied.status_code == 401
    assert denied.json()["detail"] == "Missing or invalid Authorization Bearer token"


def test_paywall_does_not_block_the_guide(
    raw_client: TestClient, monkeypatch, tmp_path
) -> None:
    root = tmp_path / "fundamentals"
    _write_edition(root, "rag-engineer", "en", ENGLISH_BODY)
    monkeypatch.setenv("FUNDAMENTALS_CONTENT_DIR", str(root))

    external_id = f"fundamentals-paywall-{uuid.uuid4().hex[:8]}"
    minted = raw_client.post("/auth/anon/mint", json={"external_id": external_id})
    assert minted.status_code == 200, minted.text
    headers = {"Authorization": f"Bearer {get_auth_provider().mint_email(external_id)}"}
    with SessionLocal() as session:
        row = ensure_user(session, external_id)
        row.membership_label = "external"
        row.membership_entitled = False
        row.billing_entitled = False
        row.stripe_subscription_status = None
        row.lifetime_forge_started_at = datetime.now(UTC)
        session.commit()

    blocked = raw_client.post(
        "/diagnosis",
        json={
            "goal_id": "rag-engineer",
            "motivation": "I want to ship grounded RAG systems in production.",
            "answers": {"level": "beginner"},
        },
        headers=headers,
    )
    assert blocked.status_code == 402, blocked.text
    assert blocked.json()["detail"]["code"] == "paywall"

    found = raw_client.get(
        "/fundamentals/rag-engineer",
        params={"locale": "en"},
        headers=headers,
    )
    assert found.status_code == 200, found.text
    assert found.json()["body_markdown"] == ENGLISH_BODY


def test_shipped_rag_engineer_guide_is_english_with_a_video(client: TestClient) -> None:
    found = client.get("/fundamentals/rag-engineer", params={"locale": "en"})

    assert found.status_code == 200, found.text
    payload = found.json()
    assert payload["goal_id"] == "rag-engineer"
    assert payload["locale"] == "en"
    body = payload["body_markdown"]
    assert body.startswith(
        "A production RAG system retrieves passages first, then asks the model to answer from those passages.\n"
    )
    assert "## Retrieve before the model writes\n" in body
    assert "## Chunks the retriever can find\n" in body
    assert "## Answer from the passages\n" in body
    assert "## Watch the retrieval loop\n" in body
    assert body.count("https://www.youtube.com/watch?v=T-D1OfcDW1M") == 1
    assert "goal_id:" not in body

    absent = client.get("/fundamentals/agent-engineer", params={"locale": "en"})
    assert absent.status_code == 404
    assert absent.json()["detail"] == "fundamentals guide not found"


ENGLISH_SECTIONS = (
    "Retrieve before the model writes",
    "Chunks the retriever can find",
    "Answer from the passages",
    "Watch the retrieval loop",
    "Know when the answer is unsupported",
)
PORTUGUESE_SECTIONS = (
    "Recupere antes de o modelo escrever",
    "Trechos que o recuperador encontra",
    "Responda a partir das passagens",
    "Observe o ciclo de recuperação",
    "Saiba quando a resposta não se sustenta",
)
PORTUGUESE_LEDE = (
    "Um sistema de RAG em produção recupera passagens primeiro e só então "
    "pede ao modelo que responda a partir dessas passagens.\n"
)


def _sections(body: str) -> list[str]:
    return [line.removeprefix("## ") for line in body.splitlines() if line.startswith("## ")]


def test_shipped_rag_engineer_guide_has_a_portuguese_edition(client: TestClient) -> None:
    portuguese = client.get("/fundamentals/rag-engineer", params={"locale": "pt-BR"})
    english = client.get("/fundamentals/rag-engineer", params={"locale": "en"})

    assert portuguese.status_code == 200, portuguese.text
    assert english.status_code == 200, english.text
    pt = portuguese.json()
    en = english.json()
    assert pt["goal_id"] == "rag-engineer"
    assert en["goal_id"] == "rag-engineer"
    assert pt["locale"] == "pt-BR"
    assert en["locale"] == "en"
    assert pt["body_markdown"].startswith(PORTUGUESE_LEDE)
    assert "goal_id:" not in pt["body_markdown"]
    assert _sections(pt["body_markdown"]) == list(PORTUGUESE_SECTIONS)
    assert _sections(en["body_markdown"]) == list(ENGLISH_SECTIONS)
    assert pt["body_markdown"].count("https://www.youtube.com/watch?v=T-D1OfcDW1M") == 1
    assert en["body_markdown"].count("https://www.youtube.com/watch?v=T-D1OfcDW1M") == 1
