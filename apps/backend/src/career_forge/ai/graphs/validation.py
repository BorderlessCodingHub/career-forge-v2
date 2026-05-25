"""Validation graph — rubric-based mastery interview (HAC-10)."""

from __future__ import annotations

import re
from collections.abc import AsyncIterator
from typing import Any
from uuid import uuid4

from career_forge.schemas.common import ValidationStatus
from career_forge.schemas.validation import ValidationRequest, ValidationResponse

PASS_THRESHOLD = 70

QUESTION_LABELS = ("conceito", "aplicação", "aprofundamento")
QUESTION_TEMPLATES = (
    "Com suas palavras, {criterion}. Dê um exemplo prático.",
    "Como você aplicaria isso em um projeto real: {criterion}?",
    "Explique para um colega iniciante: {criterion}.",
)

RUBRIC_KEYWORDS: dict[str, list[tuple[str, ...]]] = {
    "js": [
        ("let", "const", "var", "escopo", "hoisting", "block"),
        ("async", "await", "promise", "callback", "assíncron"),
        ("map", "filter", "reduce", "array", "método"),
    ],
    "git": [
        ("branch", "feature", "pull request", "pr", "merge", "fluxo"),
        ("commit", "histórico", "snapshot", "mensagem"),
        ("reset", "revert", "desfazer", "soft", "commit"),
    ],
    "http": [
        ("get", "post", "put", "patch", "delete", "crud", "método"),
        ("401", "403", "unauthorized", "forbidden", "autenticação", "autorização"),
        ("header", "content-type", "authorization", "corpo", "requisição"),
    ],
    "db": [
        ("schema", "tabela", "coluna", "entidade", "modelagem", "relacion"),
        ("join", "inner", "left", "query", "select", "relacion"),
        ("índice", "indice", "index", "busca", "performance", "coluna"),
    ],
    "rest": [
        ("endpoint", "rota", "crud", "recurso", "get", "post", "put", "delete"),
        ("idempot", "put", "post", "patch", "verbo", "semântica"),
        ("erro", "json", "status", "400", "404", "500", "consistente"),
    ],
    "auth": [
        ("jwt", "payload", "header", "claim", "token"),
        ("senha", "password", "hash", "nunca", "token", "plain"),
        ("bearer", "authorization", "header", "autentica"),
    ],
    "final": [
        ("status", "200", "201", "400", "404", "endpoint"),
        ("sql", "schema", "tabela", "modelagem", "coerente"),
        ("readme", "rodar", "local", "docker", "instala"),
    ],
}

RUBRIC_GAPS: dict[str, list[str]] = {
    "js": [
        "Não diferenciou var, let e const com clareza",
        "Callback vs async/await ainda confuso",
        "Não citou map/filter/reduce com exemplo concreto",
    ],
    "git": [
        "Fluxo feature branch → PR → merge incompleto",
        "Commit como snapshot do histórico não ficou claro",
        "Não explicou como desfazer commit (reset/revert)",
    ],
    "http": [
        "Métodos HTTP para CRUD ainda imprecisos",
        "Confundiu 401 (autenticação) com 403 (autorização)",
        "Headers ou corpo da requisição não foram detalhados",
    ],
    "db": [
        "Schema mínimo do recurso não foi desenhado",
        "JOIN e resultado da query mal explicados",
        "Índice para busca não mencionado",
    ],
    "rest": [
        "Endpoints CRUD incompletos ou genéricos",
        "Idempotência de PUT vs POST não explicada",
        "Estrutura de erro JSON consistente ausente",
    ],
    "auth": [
        "Payload JWT não descrito",
        "Risco de expor senha no token não mencionado",
        "Header Authorization Bearer sem exemplo",
    ],
    "final": [
        "Status codes da API inconsistentes",
        "Schema SQL não alinha com endpoints",
        "README / execução local não cobertos",
    ],
}

RUBRIC_STRENGTHS: dict[str, list[str]] = {
    "js": [
        "Diferencia escopo de variáveis com clareza",
        "Relaciona callbacks com async/await",
        "Usa métodos de array em exemplo prático",
    ],
    "git": [
        "Descreve fluxo colaborativo com branches",
        "Entende commit como registro no histórico",
        "Sabe opções para desfazer alterações locais",
    ],
    "http": [
        "Escolhe verbos HTTP coerentes com CRUD",
        "Diferencia 401 e 403 corretamente",
        "Monta GET/POST com headers adequados",
    ],
    "db": [
        "Modela entidades com campos essenciais",
        "Explica JOIN com clareza",
        "Justifica índice para colunas de busca",
    ],
    "rest": [
        "Lista endpoints REST para um recurso",
        "Explica idempotência PUT vs POST",
        "Propõe JSON de erro consistente",
    ],
    "auth": [
        "Descreve estrutura típica de JWT",
        "Reforça que senha não vai no token",
        "Cita Authorization Bearer corretamente",
    ],
    "final": [
        "API com status codes coerentes",
        "SQL alinhado aos endpoints",
        "Documentação de execução local presente",
    ],
}

NEXT_ACTIONS: dict[str, str] = {
    "js": "Revise let/const, Promises e map/filter/reduce com um mini exercício antes de retomar.",
    "git": "Pratique feature branch → PR → merge e experimente git reset --soft vs revert.",
    "http": "Revise GET/POST/PUT/PATCH/DELETE e diferença 401 vs 403 com exemplos curl.",
    "db": "Desenhe schema de tarefas com JOIN e explique quando indexar colunas de busca.",
    "rest": "Revise endpoints CRUD, idempotência PUT vs POST e contrato JSON de erros.",
    "auth": "Estude payload JWT, fluxo Bearer e por que senha nunca entra no token.",
    "final": "Garanta status codes corretos, schema SQL coerente e README de execução local.",
}


def _lc_event(
    event: str,
    name: str,
    run_id: str,
    data: dict[str, Any],
) -> dict[str, Any]:
    return {
        "event": event,
        "name": name,
        "run_id": run_id,
        "tags": [],
        "metadata": {},
        "data": data,
    }


def _score_text(text: str, keywords: tuple[str, ...]) -> int:
    lowered = text.lower()
    hits = sum(1 for keyword in keywords if keyword in lowered)
    length_bonus = min(len(lowered) // 50, 4)
    uncertainty = sum(
        1 for token in ("acho", "não sei", "talvez", "nunca", "confuso", "não tenho certeza")
        if token in lowered
    )
    return max(0, min(100, 30 + hits * 14 + length_bonus * 6 - uncertainty * 12))


def _keywords_for(node_id: str, rubric_index: int, rubric: list[str]) -> tuple[str, ...]:
    node_keywords = RUBRIC_KEYWORDS.get(node_id)
    if node_keywords and rubric_index < len(node_keywords):
        return node_keywords[rubric_index]
    criterion = rubric[rubric_index].lower() if rubric_index < len(rubric) else ""
    tokens = tuple(token for token in re.findall(r"[a-záàâãéêíóôõúç0-9]+", criterion) if len(token) > 3)
    return tokens or ("exemplo", "prática", "conceito")


def build_validation_response(payload: ValidationRequest) -> ValidationResponse:
    """Deterministic rubric evaluation from interview answers (no LLM for MVP)."""
    rubric = payload.rubric or [answer.question_id for answer in payload.answers]
    per_answer_scores: list[int] = []

    for index, answer in enumerate(payload.answers):
        keywords = _keywords_for(payload.node_id, index, rubric)
        per_answer_scores.append(_score_text(answer.answer, keywords))

    score = sum(per_answer_scores) // max(len(per_answer_scores), 1)
    status = ValidationStatus.APROVADO if score >= PASS_THRESHOLD else ValidationStatus.REVISAR

    node_strengths = RUBRIC_STRENGTHS.get(payload.node_id, [])
    node_gaps = RUBRIC_GAPS.get(payload.node_id, [])

    strengths: list[str] = []
    gaps: list[str] = []

    for index, answer_score in enumerate(per_answer_scores):
        if answer_score >= 65 and index < len(node_strengths):
            strengths.append(node_strengths[index])
        elif answer_score < 55 and index < len(node_gaps):
            gaps.append(node_gaps[index])

    if not strengths:
        strengths.append(f"Demonstra esforço em explicar {payload.node_title} com palavras próprias")

    if not gaps:
        if status == ValidationStatus.REVISAR:
            gaps.append(f"Ainda faltam evidências concretas sobre critérios de {payload.node_title}")
        else:
            gaps.append("Aprofunde com exemplos reais de projeto na próxima rodada")

    if status == ValidationStatus.REVISAR and len(gaps) < 2:
        gaps.append("Respostas genéricas — faltam termos técnicos da rubrica")

    next_action = NEXT_ACTIONS.get(
        payload.node_id,
        f"Revise os critérios de {payload.node_title} e tente novamente com exemplos concretos.",
    )

    mentor_summary = (
        f"Para o mentor: validação de {payload.node_title} ({payload.node_id}) — "
        f"score {score}/100 ({status.value}). "
    )
    if gaps:
        mentor_summary += f"Lacunas: {'; '.join(gaps[:2])}. "
    if strengths:
        mentor_summary += f"Pontos fortes: {strengths[0]}. "
    mentor_summary += next_action

    return ValidationResponse(
        score=score,
        status=status,
        strengths=strengths[:3],
        gaps=gaps[:3],
        next_action=next_action,
        mentor_summary=mentor_summary,
    )


class ValidationGraphRunnable:
    """GraphRunnable that maps interview answers → ValidationResponse."""

    graph_name = "validation"

    async def astream_events(
        self,
        input_data: dict[str, Any],
        *,
        version: str = "v2",
    ) -> AsyncIterator[dict[str, Any]]:
        del version
        payload = ValidationRequest.model_validate(input_data)
        result = build_validation_response(payload)
        run_id = str(uuid4())

        yield _lc_event("on_chain_start", self.graph_name, run_id, {})

        yield _lc_event(
            "on_chain_stream",
            "evaluate_rubric",
            run_id,
            {
                "chunk": {
                    "type": "progress",
                    "step": "evaluate_rubric",
                    "message": f"Avaliando evidências de {payload.node_title}",
                },
            },
        )

        output = result.model_dump()
        yield _lc_event(
            "on_chain_end",
            self.graph_name,
            run_id,
            {"output": output, "input": input_data},
        )


def build_validation_graph() -> ValidationGraphRunnable:
    """Return configured validation graph runnable."""
    return ValidationGraphRunnable()
