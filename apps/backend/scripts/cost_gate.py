"""Synthetic cost gate runner (CAR-7 baseline · F2 re-cost).

Runs 20–30 roadmap_forge GraphRuns (+ diagnosis / validation / mentor samples)
with ``_cost.synthetic_gate=true``, measures token→USD→BRL, writes Yuri report.

F2 path: forge inputs go through ``apply_lean_forge_input`` (must-have bias +
soft-gate lean allowlist) with a spectrum of ``profile_score`` personas.

Usage (from repo root)::

    ./scripts/cost-gate.sh
    ./scripts/cost-gate.sh --forges 24 --diagnosis 4

Requires ``OPENAI_API_KEY``. Uses in-memory GraphRun + usage stores so the
student cost pool is untouched.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
import time
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

# Ensure package imports when run as ``python -m scripts.cost_gate``.
_BACKEND_ROOT = Path(__file__).resolve().parents[1]
_SRC = _BACKEND_ROOT / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from langchain_core.callbacks.usage import get_usage_metadata_callback

from career_forge.ai.executor import GraphExecutor
from career_forge.ai.run import GraphRun, GraphRunResult, InMemoryGraphRunStore
from career_forge.schemas.diagnosis import DiagnosisProfile, DiagnosisResponse
from career_forge.schemas.diagnosis_interview import (
    BeliefState,
    DiagnosisIntake,
    DiagnosisSession,
)
from career_forge.schemas.mentor import MentorContextSnapshot, MentorRequest
from career_forge.schemas.validation import ValidationAnswer, ValidationRequest
from career_forge.services.cost_gate_report import (
    APPROVAL_CEILING_BRL,
    DEFAULT_BUFFER,
    DEFAULT_FX_USD_BRL,
    HARD_BUDGET_BRL,
    RunCostRecord,
    cost_usd_from_usage,
    project_monthly_spend_brl,
    records_to_jsonable,
    render_report,
    summarize_costs,
    to_brl,
)
from career_forge.services.cost_guard import CostGuard, InMemoryUsageStore
from career_forge.services.lean_forge import apply_lean_forge_input

GOALS: dict[str, dict[str, Any]] = {
    "rag-engineer": {
        "track_id": "rag-engineer-beginner",
        "label": "Beginner with retrieval fundamentals",
        "gaps": ["Vector retrieval and top-k debugging", "Grounded generation with citations"],
        "strengths": ["Understands embedding fundamentals", "Can reason about chunking"],
        "priorities": ["rag-retrieval", "rag-chunking", "rag-rerank"],
        "mastery": {
            "rag-embeddings": 65,
            "rag-chunking": 78,
            "rag-retrieval": 42,
            "rag-rerank": 35,
            "rag-grounding": 0,
            "rag-eval": 0,
            "rag-production": 0,
        },
    },
    "agent-engineer": {
        "track_id": "agent-engineer-beginner",
        "label": "Beginner building tool-using agents",
        "gaps": ["Tool-loop failure modes", "MCP connectors"],
        "strengths": ["Basic prompt chaining", "Reads API docs"],
        "priorities": ["agent-tool-use", "agent-planning", "agent-failure-modes"],
        "mastery": {
            "agent-tool-use": 55,
            "agent-mcp": 20,
            "agent-planning": 40,
            "agent-memory": 15,
            "agent-failure-modes": 10,
            "agent-observability": 0,
            "agent-ship": 0,
        },
    },
    "llm-evals": {
        "track_id": "llm-evals-beginner",
        "label": "Beginner in LLM evaluation",
        "gaps": ["Judge calibration", "Regression gates"],
        "strengths": ["Writes clear rubrics", "Knows offline vs online eval"],
        "priorities": ["evals-metrics", "evals-llm-judge", "evals-regression"],
        "mastery": {
            "evals-metrics": 60,
            "evals-llm-judge": 35,
            "evals-datasets": 45,
            "evals-regression": 20,
            "evals-tracing": 15,
            "evals-online": 0,
            "evals-llmops": 0,
        },
    },
    "fine-tuning": {
        "track_id": "fine-tuning-beginner",
        "label": "Beginner in model adaptation",
        "gaps": ["LoRA setup", "Preference-data quality"],
        "strengths": ["Clean dataset hygiene", "Knows SFT vs RLHF at high level"],
        "priorities": ["ft-data-prep", "ft-lora", "ft-eval"],
        "mastery": {
            "ft-data-prep": 55,
            "ft-sft": 40,
            "ft-lora": 25,
            "ft-eval": 30,
            "ft-dpo": 10,
            "ft-serve": 0,
            "ft-alignment": 0,
        },
    },
}

GATE_USER = "gate-runner"
COST_META = {"_cost": {"synthetic_gate": True}}

# Golden-aligned spectrum (CAR-18 seeds) — drives soft-gate lean vs full forge.
PERSONA_SCORES: dict[str, float] = {
    "mid": 0.75,
    "early": 0.58,
    "staff": 0.90,
    "soft-gated-weak": 0.42,
}
PERSONA_ORDER = ("mid", "early", "staff", "soft-gated-weak")


def _load_dotenv(repo_root: Path) -> None:
    env_path = repo_root / ".env"
    if not env_path.exists():
        return
    for line in env_path.read_text().splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def _diagnosis_for_goal(goal_id: str, *, persona: str = "mid") -> DiagnosisResponse:
    spec = GOALS[goal_id]
    score = PERSONA_SCORES.get(persona, PERSONA_SCORES["mid"])
    return DiagnosisResponse(
        profile=DiagnosisProfile(
            label=spec["label"],
            track_id=spec["track_id"],
            persona_slug=f"{goal_id}_{persona}",
        ),
        strengths=list(spec["strengths"]),
        gaps=list(spec["gaps"]),
        starting_priorities=list(spec["priorities"]),
        estimated_mastery=dict(spec["mastery"]),
        profile_score=score,
    )


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


async def _execute_measured(
    executor: GraphExecutor,
    *,
    graph_name: str,
    goal_id: str | None,
    run_input: dict[str, Any],
    fx: float,
) -> RunCostRecord:
    payload = {**COST_META, **run_input}
    # Preserve richer `_cost` labels from forge inputs; always keep synthetic_gate.
    cost_meta = dict(COST_META["_cost"])
    if isinstance(run_input.get("_cost"), dict):
        cost_meta.update(run_input["_cost"])
    cost_meta["synthetic_gate"] = True
    payload["_cost"] = cost_meta
    run = GraphRun(graph_name=graph_name, user_id=GATE_USER, input=payload)
    started = time.perf_counter()
    error: str | None = None
    usage: dict[str, dict[str, Any]] = {}
    try:
        with get_usage_metadata_callback() as cb:
            result = await executor.execute(run, stream=False)
        assert isinstance(result, GraphRunResult)
        usage = {k: dict(v) for k, v in dict(cb.usage_metadata).items()}
        status = result.run.status
        run_id = result.run.id
        exclude = result.run.exclude_reason
        if status == "failed":
            error = result.run.error
    except Exception as exc:  # noqa: BLE001 — gate continues on single-run failure
        status = "failed"
        run_id = run.id
        exclude = "synthetic_gate"
        error = str(exc)
    duration = time.perf_counter() - started
    usd = cost_usd_from_usage(usage)
    return RunCostRecord(
        run_id=run_id,
        graph_name=graph_name,
        goal_id=goal_id,
        status=status,
        duration_sec=duration,
        exclude_reason=exclude,
        usage_by_model=usage,
        cost_usd=usd,
        cost_brl=to_brl(usd, fx),
        error=error,
    )


def _forge_input(goal_id: str, index: int, *, persona: str) -> dict[str, Any]:
    diagnosis = _diagnosis_for_goal(goal_id, persona=persona)
    raw = {
        "diagnosis": diagnosis.model_dump(mode="json"),
        "goal_id": goal_id,
        "motivation": f"F2 cost-gate forge #{index} {goal_id}__{persona}",
        "years_xp": "1-3",
        "_cost": {
            "synthetic_gate": True,
            "label": f"cost-gate:{goal_id}__{persona}",
            "persona": persona,
        },
    }
    return apply_lean_forge_input(raw)


def _diagnosis_start_input(goal_id: str) -> dict[str, Any]:
    session = DiagnosisSession(
        session_id=str(uuid.uuid4()),
        intake=DiagnosisIntake(
            user_id=GATE_USER,
            goal_id=goal_id,
            motivation=f"CAR-7 diagnosis sample for {goal_id}",
            years_xp="1-3",
        ),
        belief=BeliefState.empty(),
        status="asking",
        round_count=0,
    )
    return {
        "phase": "start",
        "session": session.model_dump(mode="json"),
        "answers": [],
    }


def _validation_input(goal_id: str) -> dict[str, Any]:
    node_id = GOALS[goal_id]["priorities"][0]
    body = ValidationRequest(
        user_id=GATE_USER,
        node_id=node_id,
        node_title=node_id,
        rubric=["criterion-a", "criterion-b", "criterion-c"],
        answers=[
            ValidationAnswer(question_id="q1", answer="I explain the concept with a concrete project example."),
            ValidationAnswer(question_id="q2", answer="I measure quality with a simple metric and iterate."),
            ValidationAnswer(question_id="q3", answer="I document failure modes and a rollback plan."),
        ],
    )
    return body.model_dump(mode="json")


def _mentor_input(goal_id: str) -> dict[str, Any]:
    node_id = GOALS[goal_id]["priorities"][0]
    req = MentorRequest(
        user_id=GATE_USER,
        message=f"How should I practice {node_id} this week?",
        node_id=node_id,
        node_title=node_id,
    )
    context = MentorContextSnapshot(
        recent_gaps=list(GOALS[goal_id]["gaps"][:2]),
        recent_strengths=list(GOALS[goal_id]["strengths"][:2]),
        failed_nodes=[],
        current_node_status="em_progresso",
        current_node_mastery=40,
        validation_count=0,
        last_validation_feedback=None,
    )
    return {**req.model_dump(mode="json"), "context_snapshot": context.model_dump(mode="json")}


def _plan_jobs(forges: int, diagnosis: int, validation: int, mentor: int) -> list[tuple[str, str | None, dict[str, Any]]]:
    goals = list(GOALS.keys())
    jobs: list[tuple[str, str | None, dict[str, Any]]] = []
    for i in range(forges):
        goal = goals[i % len(goals)]
        # Round-robin personas across goals so each track sees lean + full forge.
        persona = PERSONA_ORDER[(i // len(goals)) % len(PERSONA_ORDER)]
        jobs.append(("roadmap_forge", goal, _forge_input(goal, i + 1, persona=persona)))
    for i in range(diagnosis):
        goal = goals[i % len(goals)]
        jobs.append(("diagnosis_interview", goal, _diagnosis_start_input(goal)))
    for i in range(validation):
        goal = goals[i % len(goals)]
        jobs.append(("validation", goal, _validation_input(goal)))
    for i in range(mentor):
        goal = goals[i % len(goals)]
        jobs.append(("mentor", goal, _mentor_input(goal)))
    return jobs


async def run_gate(args: argparse.Namespace) -> int:
    repo = _repo_root()
    _load_dotenv(repo)

    if not os.getenv("OPENAI_API_KEY", "").strip():
        print("ERROR: OPENAI_API_KEY missing", file=sys.stderr)
        return 2

    # Gate hygiene: no stream delay, no pool pollution, quieter LangSmith 403s.
    os.environ["FORGE_STREAM_DELAY_SEC"] = "0"
    os.environ.setdefault("GRAPH_RUN_STORE", "memory")
    if args.disable_langsmith:
        os.environ["LANGCHAIN_TRACING_V2"] = "false"

    fx = float(os.getenv("COST_FX_USD_BRL", str(DEFAULT_FX_USD_BRL)))
    buffer = float(os.getenv("COST_BUFFER_FACTOR", str(DEFAULT_BUFFER)))
    batch_id = args.batch_id or str(uuid.uuid4())[:8]

    out_dir = Path(args.out_dir) if args.out_dir else repo / "docs" / "reports"
    out_dir.mkdir(parents=True, exist_ok=True)
    runtime_dir = out_dir / ".runtime"
    runtime_dir.mkdir(parents=True, exist_ok=True)
    jsonl_path = runtime_dir / f"cost-gate-{batch_id}.jsonl"
    report_path = out_dir / f"{datetime.now(UTC).strftime('%Y-%m-%d')}-cost-gate.md"

    store = InMemoryGraphRunStore()
    guard = CostGuard(store=InMemoryUsageStore())
    executor = GraphExecutor(store=store, cost_guard=guard)

    jobs = _plan_jobs(args.forges, args.diagnosis, args.validation, args.mentor)
    soft_gated_forges = sum(
        1
        for name, _, payload in jobs
        if name == "roadmap_forge" and payload.get("soft_gated")
    )
    print(
        f"F2 cost gate batch={batch_id} jobs={len(jobs)} "
        f"soft_gated_forges={soft_gated_forges} fx={fx} → {report_path}",
    )

    records: list[RunCostRecord] = []
    with jsonl_path.open("w", encoding="utf-8") as ledger:
        for idx, (graph_name, goal_id, run_input) in enumerate(jobs, start=1):
            print(f"[{idx}/{len(jobs)}] {graph_name} goal={goal_id} …", flush=True)
            rec = await _execute_measured(
                executor,
                graph_name=graph_name,
                goal_id=goal_id,
                run_input=run_input,
                fx=fx,
            )
            records.append(rec)
            ledger.write(json.dumps(records_to_jsonable([rec])[0], ensure_ascii=False) + "\n")
            ledger.flush()
            flag = "OK" if rec.status == "completed" else "FAIL"
            print(
                f"  → {flag} {rec.run_id[:8]} BRL={rec.cost_brl:.4f} "
                f"USD={rec.cost_usd:.4f} {rec.duration_sec:.1f}s",
                flush=True,
            )

    summary = summarize_costs(records)
    forge_p95 = float(summary["forge"]["p95_brl"])
    diag_bucket = summary["by_graph"].get("diagnosis_interview", {"p95_brl": 0.0})
    other_costs = [
        float(summary["by_graph"].get(name, {"p95_brl": 0.0})["p95_brl"])
        for name in ("validation", "mentor")
    ]
    projection = project_monthly_spend_brl(
        forge_p95_brl=forge_p95,
        diagnosis_p95_brl=float(diag_bucket["p95_brl"]),
        other_p95_brl=max(other_costs) if other_costs else 0.0,
        students=args.students,
        forges_per_user=args.forges_per_user,
        diagnosis_runs_per_user=args.diagnosis_per_user,
        other_runs_per_user=args.other_per_user,
        buffer=buffer,
    )
    assumptions = {
        "students": args.students,
        "forges_per_user_month": args.forges_per_user,
        "diagnosis_runs_per_user_month": args.diagnosis_per_user,
        "other_billable_runs_per_user_month": args.other_per_user,
        "gate_forges_executed": args.forges,
        "gate_soft_gated_forges": soft_gated_forges,
        "gate_personas": ",".join(PERSONA_ORDER),
        "gate_f2_path": "apply_lean_forge_input + must_have_node_ids + soft_gate",
        "gate_diagnosis_samples": args.diagnosis,
        "gate_validation_samples": args.validation,
        "gate_mentor_samples": args.mentor,
    }
    report = render_report(
        records=records,
        summary=summary,
        projection=projection,
        fx=fx,
        hard_budget=HARD_BUDGET_BRL,
        approval_ceiling=APPROVAL_CEILING_BRL,
        assumptions=assumptions,
        pricing_note=(
            "USD from OpenAI list prices (gpt-5.4 $2.50/$15, gpt-5.4-mini $0.75/$4.50, "
            "gpt-4.1-nano $0.10/$0.40 per 1M tokens; cached input at 10% of input)."
        ),
        batch_id=batch_id,
        report_title="Career Forge — F2 re-cost gate (stack pós CAR-14…18)",
        method_extra=(
            "F2 path: each forge runs through `apply_lean_forge_input` (must-have bias; "
            "lean allowlist when `profile_score` < SOFT_GATE_CUTOFF). Personas cycle "
            f"{list(PERSONA_ORDER)} with golden seed scores "
            f"(weak={PERSONA_SCORES['soft-gated-weak']}, early={PERSONA_SCORES['early']}, "
            f"mid={PERSONA_SCORES['mid']}, staff={PERSONA_SCORES['staff']}). "
            "Compares to F1 baseline (2026-07-24, same 4 LLM goals, pre soft-gate/inject)."
        ),
    )
    report_path.write_text(report, encoding="utf-8")
    (runtime_dir / f"cost-gate-{batch_id}-summary.json").write_text(
        json.dumps(
            {
                "batch_id": batch_id,
                "summary": summary,
                "projection": projection,
                "fx_usd_brl": fx,
                "recommended_cost_p95_brl_per_run": forge_p95,
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    print(f"\nReport: {report_path}")
    print(f"Ledger: {jsonl_path}")
    print(f"Forge P95 BRL: {forge_p95:.4f}")
    print(f"Projected buffered monthly: R${projection['buffered_brl']:.2f}")
    return 0 if summary["failed"] == 0 else 1


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="CAR-7 synthetic cost gate")
    p.add_argument("--forges", type=int, default=24, help="roadmap_forge runs (20–30)")
    p.add_argument("--diagnosis", type=int, default=4, help="diagnosis_interview start samples")
    p.add_argument("--validation", type=int, default=2, help="validation samples (deterministic)")
    p.add_argument("--mentor", type=int, default=2, help="mentor samples (deterministic)")
    p.add_argument("--students", type=int, default=30, help="pilot cohort size for projection")
    p.add_argument("--forges-per-user", type=int, default=2, help="FORGE_CAP_PER_USER_MONTH")
    p.add_argument("--diagnosis-per-user", type=int, default=4, help="diagnosis GraphRuns / user / mo")
    p.add_argument("--other-per-user", type=int, default=6, help="validation+mentor runs / user / mo")
    p.add_argument("--out-dir", type=str, default="", help="report output directory")
    p.add_argument("--batch-id", type=str, default="")
    p.add_argument(
        "--disable-langsmith",
        action="store_true",
        default=True,
        help="set LANGCHAIN_TRACING_V2=false (default; avoids 403 noise)",
    )
    p.add_argument("--enable-langsmith", action="store_true", help="keep LangSmith tracing on")
    return p


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    if args.enable_langsmith:
        args.disable_langsmith = False
    raise SystemExit(asyncio.run(run_gate(args)))


if __name__ == "__main__":
    main()
