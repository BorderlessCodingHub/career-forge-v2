"""Unit tests — adaptive planning after validation (HAC-11)."""

from __future__ import annotations

from career_forge.schemas.common import SkillStatus, ValidationStatus
from career_forge.schemas.validation import ValidationAnswer, ValidationRequest, ValidationResponse
from career_forge.services.planning import build_adaptive_patch, build_plan_update
from career_forge.services.roadmap import build_roadmap_from_catalog

WEAK_REST_ANSWERS = [
    ValidationAnswer(
        question_id="rest-q1",
        answer="REST é quando duas aplicações trocam dados. POST /users cria usuário.",
    ),
    ValidationAnswer(
        question_id="rest-q2",
        answer="Acho que POST e PUT são parecidos, não sei direito.",
    ),
    ValidationAnswer(
        question_id="rest-q3",
        answer="Retorna erro genérico quando dá ruim.",
    ),
]

SAMPLE_PAYLOAD = ValidationRequest(
    user_id="demo-ana",
    node_id="rest",
    node_title="APIs REST",
    rubric=[
        "Lista endpoints CRUD para um recurso",
        "Explica idempotência de PUT vs POST",
        "Descreve estrutura de erro JSON consistente",
    ],
    answers=WEAK_REST_ANSWERS,
)


def _user_skill_nodes():
    from career_forge.schemas.common import UserSkillNode

    roadmap = build_roadmap_from_catalog()
    return [
        UserSkillNode(
            node_id=node.node_id,
            title=node.title,
            status=node.status,
            mastery_score=node.mastery_score,
            priority=node.priority,
            rationale=node.rationale,
        )
        for node in roadmap.nodes
    ]


def _failed_validation() -> ValidationResponse:
    return ValidationResponse(
        score=48,
        status=ValidationStatus.REVISAR,
        strengths=["Demonstra esforço"],
        gaps=["Endpoints CRUD incompletos ou genéricos"],
        next_action="Revise endpoints CRUD, idempotência PUT vs POST e contrato JSON de erros.",
        mentor_summary="Falhou validação REST.",
    )


def _passed_validation() -> ValidationResponse:
    return ValidationResponse(
        score=82,
        status=ValidationStatus.APROVADO,
        strengths=["Lista endpoints REST para um recurso"],
        gaps=["Aprofunde com exemplos reais"],
        next_action="Avance para autenticação JWT.",
        mentor_summary="Aprovado em REST.",
    )


class TestAdaptivePatch:
    def test_failure_marks_node_revisar_and_blocks_dependents(self) -> None:
        graph = _user_skill_nodes()
        patch = build_adaptive_patch("rest", _failed_validation(), graph)

        rest_patch = next(item for item in patch.patches if item.node_id == "rest")
        assert rest_patch.status == SkillStatus.REVISAR
        assert rest_patch.priority.value == "high"

        blocked_ids = {item.node_id for item in patch.patches if item.status == SkillStatus.BLOQUEADO}
        assert "auth" in blocked_ids
        assert "final" in blocked_ids
        assert patch.continue_research is True

    def test_pass_unlocks_next_node(self) -> None:
        graph = _user_skill_nodes()
        for node in graph:
            if node.node_id in {"js", "git", "http", "db"}:
                node.status = SkillStatus.APROVADO
            if node.node_id == "rest":
                node.status = SkillStatus.EM_ESTUDO
            if node.node_id in {"auth", "final"}:
                node.status = SkillStatus.BLOQUEADO

        patch = build_adaptive_patch("rest", _passed_validation(), graph)

        rest_patch = next(item for item in patch.patches if item.node_id == "rest")
        assert rest_patch.status == SkillStatus.APROVADO

        auth_patch = next((item for item in patch.patches if item.node_id == "auth"), None)
        assert auth_patch is not None
        assert auth_patch.status == SkillStatus.VALIDAR
        assert auth_patch.priority.value == "high"
        assert patch.continue_research is False


class TestPlanUpdate:
    def test_build_plan_update_for_failure(self) -> None:
        plan = build_plan_update("rest", "APIs REST", _failed_validation())
        assert plan.today_focus.node_id == "rest"
        assert plan.today_focus.duration_minutes == 45
        assert "REST" in plan.next_mission

    def test_build_plan_update_for_pass(self) -> None:
        plan = build_plan_update("rest", "APIs REST", _passed_validation())
        assert plan.today_focus.duration_minutes == 30


def test_post_validation_returns_adaptive_payload(client) -> None:
    response = client.post("/validation", json=SAMPLE_PAYLOAD.model_dump())
    assert response.status_code == 200
    payload = response.json()
    assert payload["plan_update"] is not None
    assert payload["graph_patch"] is not None
    assert payload["roadmap"] is not None
    assert payload["graph_patch"]["patches"]
    revisar_nodes = [
        node["status"]
        for node in payload["roadmap"]["nodes"]
        if node["node_id"] == "rest"
    ]
    assert revisar_nodes == ["revisar"]
