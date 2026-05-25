"use client";

import { useRouter } from "next/navigation";
import { useEffect, useMemo, useState } from "react";

import { Button } from "@/components/ui";
import { createDiagnosis } from "@/lib/api-client";
import {
  CAREER_GOALS,
  DIAG_MAP_LABELS,
  DIAG_ROUNDS,
} from "@/lib/onboarding-data";
import {
  getMotivation,
  getSelectedGoal,
  setAnswers,
  setStoredDiagnosis,
} from "@/lib/onboarding-session";

import { PillRound } from "./PillRound";

function initialAnswers() {
  const init: Record<string, string> = {};
  DIAG_ROUNDS.forEach((round) =>
    round.questions.forEach((question) => {
      init[question.id] = question.defaultValue;
    }),
  );
  return init;
}

export function DiagnosticPills() {
  const router = useRouter();
  const [roundIdx, setRoundIdx] = useState(0);
  const [answers, setAnswersState] = useState<Record<string, string>>(initialAnswers);
  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const goalId = getSelectedGoal() ?? "backend";
  const motivation = getMotivation();
  const goalTitle =
    CAREER_GOALS.find((goal) => goal.id === goalId)?.title ?? "Backend Developer";

  useEffect(() => {
    if (!getSelectedGoal() || getMotivation().trim().length < 20) {
      router.replace("/");
    }
  }, [router]);

  const round = DIAG_ROUNDS[roundIdx];
  const totalQuestions = DIAG_ROUNDS.reduce(
    (count, current) => count + current.questions.length,
    0,
  );
  const answeredCount =
    roundIdx * 2 +
    round.questions.filter((question) => answers[question.id]?.trim()).length;
  const pct = Math.min(100, Math.round((answeredCount / totalQuestions) * 100));
  const roundComplete = round.questions.every(
    (question) => (answers[question.id]?.trim().length ?? 0) >= 8,
  );
  const isLastRound = roundIdx === DIAG_ROUNDS.length - 1;

  const mapStatus = useMemo(() => {
    const doneLabels = new Set<string>();
    for (let index = 0; index < roundIdx; index += 1) {
      DIAG_ROUNDS[index].maps.forEach((label) => doneLabels.add(label));
    }
    return (label: string) => {
      if (doneLabels.has(label)) return "done";
      if (round.maps.includes(label)) return "active";
      return "pending";
    };
  }, [round.maps, roundIdx]);

  const submitRound = async () => {
    if (!roundComplete || generating) return;

    if (!isLastRound) {
      setRoundIdx((index) => index + 1);
      return;
    }

    setGenerating(true);
    setError(null);
    setAnswers(answers);

    try {
      const result = await createDiagnosis({
        goal_id: goalId,
        motivation,
        answers,
      });
      setStoredDiagnosis(result.diagnosis);
      router.push("/onboarding/edit");
    } catch (cause) {
      setError(
        cause instanceof Error
          ? cause.message
          : "Não foi possível gerar o diagnóstico.",
      );
      setGenerating(false);
    }
  };

  return (
    <main
      className="min-h-screen grid-dots px-4 py-8 lg:px-8"
      data-testid="diagnostic-pills"
    >
      <div className="mx-auto grid max-w-6xl gap-6 lg:grid-cols-[320px_1fr]">
        <aside className="rounded-card border border-border bg-surface p-6">
          <div className="text-xs uppercase tracking-wide text-text-muted">
            Seu sonho
          </div>
          <div className="mt-3 text-lg font-medium text-text-primary">
            {goalTitle}
          </div>
          <p className="mt-3 text-sm leading-relaxed text-text-secondary">
            {motivation}
          </p>

          <div className="mt-6">
            <div className="flex items-center justify-between text-xs text-text-muted">
              <span>Diagnóstico</span>
              <span>
                Rodada {roundIdx + 1}/{DIAG_ROUNDS.length}
              </span>
            </div>
            <div className="mt-2 h-2 overflow-hidden rounded-full bg-surface-elevated">
              <div
                className="h-full rounded-full bg-brand-ribbon transition-all"
                style={{ width: `${pct}%` }}
              />
            </div>
          </div>

          <div className="mt-6">
            <div className="text-xs uppercase tracking-wide text-text-muted">
              O que a IA está mapeando
            </div>
            <ul className="mt-3 space-y-2">
              {DIAG_MAP_LABELS.map((label) => {
                const status = mapStatus(label);
                return (
                  <li
                    key={label}
                    className={`flex items-center gap-2 text-sm ${
                      status === "done"
                        ? "text-accent-mint"
                        : status === "active"
                          ? "text-text-primary"
                          : "text-text-muted"
                    }`}
                  >
                    <span
                      className={`h-2 w-2 rounded-full ${
                        status === "done"
                          ? "bg-accent-mint"
                          : status === "active"
                            ? "bg-accent"
                            : "bg-border"
                      }`}
                    />
                    {label}
                  </li>
                );
              })}
            </ul>
          </div>
        </aside>

        <section className="rounded-card border border-border bg-surface p-6">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div className="text-sm text-text-secondary">
              Passo <strong>2/3</strong> · Diagnóstico · Rodada {roundIdx + 1} de{" "}
              {DIAG_ROUNDS.length}
            </div>
            <PillRound label={round.title} />
          </div>

          <p className="mt-4 text-sm text-text-secondary">{round.intro}</p>

          <div className="mt-6 grid gap-4">
            {round.questions.map((question) => (
              <div
                key={question.id}
                className="rounded-card border border-border-soft bg-surface-elevated p-4"
              >
                <div className="mb-3 flex flex-wrap items-center gap-2">
                  <PillRound label={question.tag} />
                  <p className="text-sm font-medium text-text-primary">
                    {question.prompt}
                  </p>
                </div>
                <textarea
                  data-testid={`answer-${question.id}`}
                  className="min-h-[96px] w-full rounded-lg border border-border bg-bg px-3 py-2 text-sm text-text-primary outline-none ring-accent focus:ring-2"
                  placeholder={question.placeholder}
                  value={answers[question.id] ?? ""}
                  disabled={generating}
                  onChange={(event) =>
                    setAnswersState((current) => ({
                      ...current,
                      [question.id]: event.target.value,
                    }))
                  }
                />
              </div>
            ))}
          </div>

          {generating ? (
            <div
              className="mt-6 flex items-center gap-3 rounded-card border border-border-soft bg-surface-elevated p-4"
              data-testid="diagnosis-generating"
            >
              <div className="h-5 w-5 animate-spin rounded-full border-2 border-accent border-t-transparent" />
              <div className="text-sm text-text-secondary">
                <strong className="text-text-primary">Gerando diagnóstico…</strong>{" "}
                mapeando {totalQuestions} sinais nas suas respostas.
              </div>
            </div>
          ) : (
            <div className="mt-6 flex flex-wrap items-center justify-between gap-4">
              <span className="text-sm text-text-muted">
                {round.questions.length} perguntas nesta rodada · responda todas
                para continuar
              </span>
              <Button
                data-testid="submit-round"
                disabled={!roundComplete}
                onClick={() => void submitRound()}
              >
                {isLastRound ? "Gerar diagnóstico" : "Próxima rodada"} →
              </Button>
            </div>
          )}

          {error && (
            <p className="mt-4 text-sm text-warning" data-testid="diagnosis-error">
              {error}
            </p>
          )}
        </section>
      </div>
    </main>
  );
}
