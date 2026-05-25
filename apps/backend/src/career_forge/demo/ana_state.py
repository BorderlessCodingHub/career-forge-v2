"""Shared demo user Ana state — seed, roadmap fallback, demo API."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

DEMO_ANA_EXTERNAL_ID = "demo-ana"

DEMO_ANA_PROFILE = {
    "track_id": "backend-beginner",
    "goal": "Backend para APIs em space tech",
    "motivation": "Quero construir serviços que alimentem missões espaciais.",
}

# Pitch-ready graph: js/git validated, http/db in progress, rest ready to validate live.
DEMO_ANA_SKILL_STATE: dict[str, dict[str, Any]] = {
    "js": {
        "status": "aprovado",
        "mastery_score": 65,
        "priority": "low",
        "evidence": {
            "strengths": ["Sintaxe e lógica JavaScript sólidas"],
            "gaps": [],
            "next_action": "Avançar para HTTP e APIs.",
        },
    },
    "git": {
        "status": "aprovado",
        "mastery_score": 78,
        "priority": "low",
        "evidence": {
            "strengths": ["Versionamento com commits e branches"],
            "gaps": [],
            "next_action": "Aplicar Git em fluxo de API.",
        },
    },
    "http": {
        "status": "em_estudo",
        "mastery_score": 42,
        "priority": "high",
        "rationale": "Lacuna principal — foco do onboarding",
    },
    "db": {
        "status": "recomendado",
        "mastery_score": 35,
        "priority": "high",
    },
    "rest": {
        "status": "validar",
        "mastery_score": 0,
        "priority": "high",
        "rationale": "Próximo passo — validação ao vivo no pitch",
    },
    "auth": {"status": "bloqueado", "mastery_score": 0, "priority": None},
    "final": {"status": "bloqueado", "mastery_score": 0, "priority": None},
}

DEMO_ANA_VALIDATIONS: list[dict[str, Any]] = [
    {
        "skill_node_id": "js",
        "score": 65,
        "passed": True,
        "feedback": "Domínio sólido de JavaScript básico — pronto para APIs.",
        "questions": [
            {
                "id": "js-q1",
                "index": 1,
                "label": "conceito",
                "prompt": "Com suas palavras, explique variáveis e tipos em JS.",
                "rubric_criterion": "Entender tipos primitivos e let/const",
            },
            {
                "id": "js-q2",
                "index": 2,
                "label": "aplicação",
                "prompt": "Como você aplicaria funções e arrays em um projeto?",
                "rubric_criterion": "Manipular arrays e funções",
            },
            {
                "id": "js-q3",
                "index": 3,
                "label": "aprofundamento",
                "prompt": "Explique closures para um colega iniciante.",
                "rubric_criterion": "Conceito de escopo e closures",
            },
        ],
        "answers": [
            {"question_id": "js-q1", "answer": "let e const definem escopo; tipos primitivos incluem string e number."},
            {"question_id": "js-q2", "answer": "Uso map/filter em arrays e funções puras para transformar dados."},
            {"question_id": "js-q3", "answer": "Closure é função que lembra variáveis do escopo externo."},
        ],
    },
    {
        "skill_node_id": "git",
        "score": 78,
        "passed": True,
        "feedback": "Bom domínio de Git — commits, branches e merge básico.",
        "questions": [
            {
                "id": "git-q1",
                "index": 1,
                "label": "conceito",
                "prompt": "O que é um commit e por que versionar código?",
                "rubric_criterion": "Entender commits e histórico",
            },
            {
                "id": "git-q2",
                "index": 2,
                "label": "aplicação",
                "prompt": "Como você criaria uma branch para uma feature?",
                "rubric_criterion": "Branches e fluxo básico",
            },
            {
                "id": "git-q3",
                "index": 3,
                "label": "aprofundamento",
                "prompt": "Explique merge vs rebase para um colega.",
                "rubric_criterion": "Integrar mudanças",
            },
        ],
        "answers": [
            {"question_id": "git-q1", "answer": "Commit registra snapshot; versionamento permite colaborar e reverter."},
            {"question_id": "git-q2", "answer": "git checkout -b feature/api e commits incrementais."},
            {"question_id": "git-q3", "answer": "Merge junta históricos; rebase reaplica commits em cima da main."},
        ],
    },
]


def load_demo_diagnosis(path: Path | None = None) -> dict[str, Any]:
    if path is not None:
        fixture = path
    else:
        fixture = Path(__file__).resolve().parents[1] / "fixtures" / "diagnosis_response.json"
    with fixture.open(encoding="utf-8") as handle:
        return json.load(handle)
