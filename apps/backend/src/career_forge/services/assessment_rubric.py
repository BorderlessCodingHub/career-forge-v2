"""Shared rubric constants + deterministic scoring primitives (HAC-77).

Single source of truth for the rubric used by validation and mock interview,
consumed by both the deterministic graph runnables (``ai/graphs/*``) and the
persistence services. Pure domain logic — no AI, DB or transport dependencies —
so any layer may import it without creating a cycle.

Previously these lived in ``ai/graphs/validation.py`` and were imported by
services, inverting the layer direction. Centralizing here removes that
inversion and the duplicated ``QUESTION_*`` constants.
"""

from __future__ import annotations

import re

PASS_THRESHOLD = 70

QUESTION_LABELS = ("conceito", "aplicação", "aprofundamento")
QUESTION_TEMPLATES = (
    "Com suas palavras, {criterion}. Dê um exemplo prático.",
    "Como você aplicaria isso em um projeto real: {criterion}?",
    "Explique para um colega iniciante: {criterion}.",
)
QUESTION_HINTS = {
    "conceito": "Pense na definição e no porquê antes do como.",
    "aplicação": "Use um exemplo concreto de projeto ou endpoint.",
    "aprofundamento": "Explique como se estivesse ensinando um colega.",
}

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


def score_answer(text: str, keywords: tuple[str, ...]) -> int:
    """Deterministic 0–100 score for a single answer against keyword hits."""
    lowered = text.lower()
    hits = sum(1 for keyword in keywords if keyword in lowered)
    length_bonus = min(len(lowered) // 50, 4)
    uncertainty = sum(
        1 for token in ("acho", "não sei", "talvez", "nunca", "confuso", "não tenho certeza")
        if token in lowered
    )
    return max(0, min(100, 30 + hits * 14 + length_bonus * 6 - uncertainty * 12))


def keywords_for(node_id: str, rubric_index: int, rubric: list[str]) -> tuple[str, ...]:
    """Resolve the keyword set for a rubric criterion (static map, else tokenized)."""
    node_keywords = RUBRIC_KEYWORDS.get(node_id)
    if node_keywords and rubric_index < len(node_keywords):
        return node_keywords[rubric_index]
    criterion = rubric[rubric_index].lower() if rubric_index < len(rubric) else ""
    tokens = tuple(token for token in re.findall(r"[a-záàâãéêíóôõúç0-9]+", criterion) if len(token) > 3)
    return tokens or ("exemplo", "prática", "conceito")
