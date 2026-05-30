"""Tests — knowledge gap ledger + async classifier (HAC-67)."""

from __future__ import annotations

from sqlalchemy import select

from career_forge.db.models.knowledge_gap import KnowledgeGap
from career_forge.db.models.user import User
from career_forge.db.session import SessionLocal
from career_forge.schemas.common import Priority, SkillStatus, UserSkillNode
from career_forge.schemas.knowledge_gap import KnowledgeGapDraft
from career_forge.services import knowledge_gaps as svc
from career_forge.services.mock_interview_session import MockInterviewSessionRecord

NODE_ID = "gen-llm-apis"


def _generated_node() -> UserSkillNode:
    return UserSkillNode(
        node_id=NODE_ID,
        title="APIs para LLMs",
        status=SkillStatus.RECOMENDADO,
        mastery_score=0,
        priority=Priority.HIGH,
        tasks=[
            {
                "title": "Wrapper de provider",
                "outcome": "Wrapper com testes",
                "evidence_prompt": "Como estrutura chamadas ao provedor?",
            },
        ],
        references=[{"title": "OpenAI docs", "url": "https://platform.openai.com/docs"}],
    )


def _sync_node(client, user_id: str) -> None:
    response = client.post(
        "/roadmap/sync",
        json={"user_id": user_id, "nodes": [_generated_node().model_dump()]},
    )
    assert response.status_code == 200


def _user_id(external_id: str):
    with SessionLocal() as session:
        user = session.scalar(select(User).where(User.external_id == external_id))
        assert user is not None
        return user.id


class TestKnowledgeGapLedger:
    def test_upsert_is_idempotent_per_concept(self, client) -> None:
        _sync_node(client, "gap-upsert")
        uid = _user_id("gap-upsert")

        with SessionLocal() as session:
            svc.upsert_knowledge_gap(
                session,
                user_id=uid,
                skill_node_id=NODE_ID,
                draft=KnowledgeGapDraft(concept="streaming SSE", severity="high", evidence="x"),
            )
            svc.upsert_knowledge_gap(
                session,
                user_id=uid,
                skill_node_id=NODE_ID,
                draft=KnowledgeGapDraft(
                    concept="streaming SSE", severity="medium", evidence="atualizado"
                ),
            )
            session.commit()

        with SessionLocal() as session:
            rows = session.scalars(
                select(KnowledgeGap).where(
                    KnowledgeGap.user_id == uid,
                    KnowledgeGap.skill_node_id == NODE_ID,
                    KnowledgeGap.concept == "streaming SSE",
                ),
            ).all()
        assert len(rows) == 1
        assert rows[0].severity == "medium"
        assert rows[0].evidence == "atualizado"
        assert rows[0].status == "open"

    def test_resolve_concepts_marks_resolved(self, client) -> None:
        _sync_node(client, "gap-resolve")
        uid = _user_id("gap-resolve")

        with SessionLocal() as session:
            svc.upsert_knowledge_gap(
                session,
                user_id=uid,
                skill_node_id=NODE_ID,
                draft=KnowledgeGapDraft(concept="retry/backoff"),
            )
            session.commit()

        with SessionLocal() as session:
            resolved = svc.resolve_concepts(
                session,
                user_id=uid,
                skill_node_id=NODE_ID,
                concepts=["retry/backoff"],
            )
            session.commit()
        assert resolved == 1

        with SessionLocal() as session:
            open_gaps = svc.list_open_gaps(session, user_id="gap-resolve", skill_node_id=NODE_ID)
        assert open_gaps == []

    def test_list_open_gaps_scoped_to_node(self, client) -> None:
        _sync_node(client, "gap-list")
        uid = _user_id("gap-list")
        with SessionLocal() as session:
            svc.upsert_knowledge_gap(
                session,
                user_id=uid,
                skill_node_id=NODE_ID,
                draft=KnowledgeGapDraft(concept="rate limits", severity="high"),
            )
            session.commit()

        with SessionLocal() as session:
            gaps = svc.list_open_gaps(session, user_id="gap-list", skill_node_id=NODE_ID)
        assert len(gaps) == 1
        assert gaps[0].concept == "rate limits"
        assert gaps[0].severity == "high"
        assert gaps[0].status == "open"


class TestGapCapture:
    def test_build_gap_capture_splits_wrong_and_correct(self) -> None:
        from career_forge.schemas.mock_interview import MockInterviewRequest
        from career_forge.schemas.validation import ValidationAnswer

        record = MockInterviewSessionRecord(
            session_id="s1",
            user_id="demo-ana",
            node_id=NODE_ID,
            node_title="APIs para LLMs",
            rubric=["streaming SSE", "retry/backoff"],
            answer_key={"q1": "A", "q2": "B"},
            questions_public=[
                {
                    "id": "q1",
                    "prompt": "O que é SSE?",
                    "options": [
                        {"letter": "A", "text": "Server-Sent Events"},
                        {"letter": "B", "text": "Errado"},
                    ],
                },
                {
                    "id": "q2",
                    "prompt": "Como tratar 429?",
                    "options": [
                        {"letter": "A", "text": "Ignorar"},
                        {"letter": "B", "text": "Retry com backoff"},
                    ],
                },
            ],
        )
        payload = MockInterviewRequest(
            user_id="demo-ana",
            node_id=NODE_ID,
            node_title="APIs para LLMs",
            session_id="s1",
            answers=[
                ValidationAnswer(question_id="q1", answer="A"),  # correct
                ValidationAnswer(question_id="q2", answer="A"),  # wrong
                ValidationAnswer(question_id="q3", answer="A"),
                ValidationAnswer(question_id="q4", answer="A"),
                ValidationAnswer(question_id="q5", answer="A"),
            ],
        )
        wrong, correct = svc.build_gap_capture(record, payload)
        assert correct == ["streaming SSE"]
        assert len(wrong) == 1
        assert wrong[0].concept == "retry/backoff"
        assert wrong[0].correct_text == "Retry com backoff"
        assert wrong[0].chosen_text == "Ignorar"


class TestGapClassifierFallback:
    def test_fallback_preserves_concept_per_wrong_item(self) -> None:
        from career_forge.ai.tools.gap_classifier import classify_gaps
        from career_forge.schemas.knowledge_gap import WrongAnswerItem

        result = classify_gaps(
            node_title="APIs para LLMs",
            learner_summary=None,
            wrong_items=[
                WrongAnswerItem(
                    question_id="q1",
                    concept="streaming SSE",
                    prompt="O que é SSE?",
                    chosen="B",
                    chosen_text="Errado",
                    correct="A",
                    correct_text="Server-Sent Events",
                ),
            ],
        )
        assert len(result.gaps) == 1
        assert result.gaps[0].concept == "streaming SSE"
        assert result.gaps[0].suggested_remediation


class TestGapFeedbackLoop:
    def test_list_knowledge_gaps_endpoint(self, client) -> None:
        _sync_node(client, "gap-endpoint")
        uid = _user_id("gap-endpoint")
        with SessionLocal() as session:
            svc.upsert_knowledge_gap(
                session,
                user_id=uid,
                skill_node_id=NODE_ID,
                draft=KnowledgeGapDraft(
                    concept="async/await",
                    severity="high",
                    suggested_remediation="praticar 3 exemplos",
                ),
            )
            session.commit()

        resp = client.get(
            "/knowledge-gaps",
            params={"user_id": "gap-endpoint", "node_id": NODE_ID},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 1
        assert data[0]["concept"] == "async/await"
        assert data[0]["severity"] == "high"
        assert data[0]["status"] == "open"
        assert data[0]["suggested_remediation"] == "praticar 3 exemplos"

    def test_context_includes_open_gaps_for_next_mock(self, client) -> None:
        from career_forge.services.mock_interview_context import build_mock_interview_context

        _sync_node(client, "gap-context")
        uid = _user_id("gap-context")
        with SessionLocal() as session:
            svc.upsert_knowledge_gap(
                session,
                user_id=uid,
                skill_node_id=NODE_ID,
                draft=KnowledgeGapDraft(concept="rate limiting"),
            )
            session.commit()

        with SessionLocal() as session:
            study_block, _ = build_mock_interview_context(
                session, user_id="gap-context", node_id=NODE_ID
            )
        assert "rate limiting" in study_block.get("open_gaps", [])


class TestRemediationTasks:
    def _gap_tasks(self, client, user_id: str) -> list[dict]:
        roadmap = client.get("/roadmap/", params={"user_id": user_id}).json()
        node = next(n for n in roadmap["nodes"] if n["node_id"] == NODE_ID)
        return [task for task in node["tasks"] if task.get("source") == "gap"]

    def test_high_gap_injects_remediation_task(self, client) -> None:
        _sync_node(client, "rem-inject")
        uid = _user_id("rem-inject")
        with SessionLocal() as session:
            svc.upsert_knowledge_gap(
                session,
                user_id=uid,
                skill_node_id=NODE_ID,
                draft=KnowledgeGapDraft(
                    concept="streaming SSE",
                    severity="high",
                    suggested_remediation="praticar streaming token a token",
                ),
            )
            session.flush()
            svc.sync_remediation_tasks(session, user_id=uid, skill_node_id=NODE_ID)
            session.commit()

        gap_tasks = self._gap_tasks(client, "rem-inject")
        assert len(gap_tasks) == 1
        assert gap_tasks[0]["title"].startswith("Reforçar")
        assert "praticar streaming" in gap_tasks[0]["evidence_prompt"]

        # original (non-gap) task is preserved
        roadmap = client.get("/roadmap/", params={"user_id": "rem-inject"}).json()
        node = next(n for n in roadmap["nodes"] if n["node_id"] == NODE_ID)
        assert any(task.get("source") != "gap" for task in node["tasks"])

    def test_remediation_idempotent_then_resolved(self, client) -> None:
        _sync_node(client, "rem-idem")
        uid = _user_id("rem-idem")
        with SessionLocal() as session:
            svc.upsert_knowledge_gap(
                session,
                user_id=uid,
                skill_node_id=NODE_ID,
                draft=KnowledgeGapDraft(concept="retry/backoff", severity="high"),
            )
            session.flush()
            svc.sync_remediation_tasks(session, user_id=uid, skill_node_id=NODE_ID)
            svc.sync_remediation_tasks(session, user_id=uid, skill_node_id=NODE_ID)
            session.commit()
        assert len(self._gap_tasks(client, "rem-idem")) == 1

        with SessionLocal() as session:
            svc.resolve_concepts(
                session, user_id=uid, skill_node_id=NODE_ID, concepts=["retry/backoff"]
            )
            session.flush()
            svc.sync_remediation_tasks(session, user_id=uid, skill_node_id=NODE_ID)
            session.commit()
        assert self._gap_tasks(client, "rem-idem") == []

    def test_medium_gap_does_not_inject(self, client) -> None:
        _sync_node(client, "rem-medium")
        uid = _user_id("rem-medium")
        with SessionLocal() as session:
            svc.upsert_knowledge_gap(
                session,
                user_id=uid,
                skill_node_id=NODE_ID,
                draft=KnowledgeGapDraft(concept="cache de respostas", severity="medium"),
            )
            session.flush()
            svc.sync_remediation_tasks(session, user_id=uid, skill_node_id=NODE_ID)
            session.commit()
        assert self._gap_tasks(client, "rem-medium") == []


class TestMockInterviewGapLoop:
    def test_submit_records_gaps_then_resolves(self, client) -> None:
        """End-to-end: wrong answers create gaps; correct answers resolve them."""
        _sync_node(client, "gap-loop")

        # Submit with wrong answers (fallback gabarito is always "A" → submit "B").
        questions = client.get(
            "/mock-interview/questions",
            params={"node_id": NODE_ID, "user_id": "gap-loop"},
        ).json()
        wrong_body = {
            "user_id": "gap-loop",
            "node_id": NODE_ID,
            "node_title": "APIs para LLMs",
            "session_id": questions["session_id"],
            "answers": [{"question_id": q["id"], "answer": "B"} for q in questions["questions"]],
        }
        assert client.post("/mock-interview", json=wrong_body).status_code == 200

        with SessionLocal() as session:
            uid = session.scalar(select(User).where(User.external_id == "gap-loop")).id
            gaps = session.scalars(
                select(KnowledgeGap).where(
                    KnowledgeGap.user_id == uid,
                    KnowledgeGap.status == "open",
                ),
            ).all()
        assert len(gaps) >= 1
        recorded_concepts = {gap.concept for gap in gaps}

        # Re-take with correct answers (all "A") → concepts resolved.
        questions2 = client.get(
            "/mock-interview/questions",
            params={"node_id": NODE_ID, "user_id": "gap-loop"},
        ).json()
        correct_body = {
            "user_id": "gap-loop",
            "node_id": NODE_ID,
            "node_title": "APIs para LLMs",
            "session_id": questions2["session_id"],
            "answers": [{"question_id": q["id"], "answer": "A"} for q in questions2["questions"]],
        }
        assert client.post("/mock-interview", json=correct_body).status_code == 200

        with SessionLocal() as session:
            uid = session.scalar(select(User).where(User.external_id == "gap-loop")).id
            still_open = session.scalars(
                select(KnowledgeGap).where(
                    KnowledgeGap.user_id == uid,
                    KnowledgeGap.status == "open",
                    KnowledgeGap.concept.in_(recorded_concepts),
                ),
            ).all()
        assert still_open == []
