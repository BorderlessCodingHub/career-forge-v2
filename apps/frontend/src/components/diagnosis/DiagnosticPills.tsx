"use client";

import { useRouter } from "next/navigation";
import { useCallback, useEffect, useMemo, useState } from "react";

import { Button } from "@/components/ui";
import {
  startDiagnosisInterview,
  submitDiagnosisTurn,
} from "@/lib/api-client";
import { CAREER_GOALS } from "@/lib/onboarding-data";
import {
  getCvAttachment,
  getMotivation,
  getSelectedGoal,
  getYearsXp,
  setAnswers,
  setDiagnosisSessionId,
  setStoredDiagnosis,
} from "@/lib/onboarding-session";
import type {
  CvAttachment,
  InterviewQuestion,
  InterviewTurnResponse,
  RubricMapItem,
} from "@/types/contracts";

import { PillRound } from "./PillRound";

const MIN_ANSWER_LENGTH = 8;
const MAX_ROUNDS = 5;

function toInterviewCv(cv: CvAttachment) {
  if (cv.mimeType !== "application/pdf") return undefined;
  return {
    filename: cv.filename,
    mime_type: "application/pdf" as const,
    content_base64: cv.dataBase64,
  };
}

function mapStatusFromProgress(
  item: RubricMapItem,
): "done" | "active" | "pending" {
  if (item.saturated) return "done";
  if (item.confidence > 0) return "active";
  return "pending";
}

export function DiagnosticPills() {
  const router = useRouter();
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [questions, setQuestions] = useState<InterviewQuestion[]>([]);
  const [mappingProgress, setMappingProgress] = useState<RubricMapItem[]>([]);
  const [answers, setAnswersState] = useState<Record<string, string>>({});
  const [roundCount, setRoundCount] = useState(0);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const goalId = getSelectedGoal() ?? "backend";
  const motivation = getMotivation();
  const yearsXp = getYearsXp();
  const goalTitle =
    CAREER_GOALS.find((goal) => goal.id === goalId)?.title ?? "Backend Developer";

  useEffect(() => {
    if (!getSelectedGoal() || getMotivation().trim().length < 20 || !getYearsXp()) {
      router.replace("/");
    }
  }, [router]);

  const applyTurnResponse = useCallback((response: InterviewTurnResponse) => {
    setSessionId(response.session_id);
    setDiagnosisSessionId(response.session_id);
    setQuestions(response.questions);
    setMappingProgress(response.mapping_progress);
    setAnswersState((current) => {
      const next = { ...current };
      response.questions.forEach((question) => {
        if (next[question.id] === undefined) {
          next[question.id] = "";
        }
      });
      return next;
    });
  }, []);

  useEffect(() => {
    let cancelled = false;

    async function bootstrap() {
      setLoading(true);
      setError(null);
      try {
        const cv = getCvAttachment();
        const response = await startDiagnosisInterview({
          goal_id: goalId,
          motivation,
          years_xp: yearsXp ?? undefined,
          cv: cv ? toInterviewCv(cv) : undefined,
        });
        if (cancelled) return;
        applyTurnResponse(response);
        setRoundCount(1);
      } catch (cause) {
        if (cancelled) return;
        setError(
          cause instanceof Error
            ? cause.message
            : "Não foi possível iniciar o diagnóstico.",
        );
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    void bootstrap();
    return () => {
      cancelled = true;
    };
  }, [applyTurnResponse, goalId, motivation, yearsXp]);

  const roundComplete = questions.every(
    (question) => (answers[question.id]?.trim().length ?? 0) >= MIN_ANSWER_LENGTH,
  );

  const answeredInRound = questions.filter(
    (question) => (answers[question.id]?.trim().length ?? 0) >= MIN_ANSWER_LENGTH,
  ).length;

  const totalExpectedQuestions = Math.min(MAX_ROUNDS * 2, 10);
  const answeredTotal =
    (roundCount - 1) * 2 + answeredInRound;
  const pct = Math.min(
    100,
    Math.round((answeredTotal / totalExpectedQuestions) * 100),
  );

  const activeTopics = useMemo(
    () => new Set(questions.map((question) => question.topic)),
    [questions],
  );

  const submitRound = async () => {
    if (!roundComplete || submitting || !sessionId) return;

    setSubmitting(true);
    setError(null);

    const turnAnswers = questions.map((question) => ({
      question_id: question.id,
      text: answers[question.id]?.trim() ?? "",
    }));

    setAnswers(answers);

    try {
      const response = await submitDiagnosisTurn(sessionId, {
        answers: turnAnswers,
      });

      if (response.status === "complete" && response.diagnosis) {
        setStoredDiagnosis(response.diagnosis);
        router.push("/onboarding/edit");
        return;
      }

      applyTurnResponse(response);
      setRoundCount((count) => count + 1);
      setSubmitting(false);
    } catch (cause) {
      setError(
        cause instanceof Error
          ? cause.message
          : "Não foi possível enviar suas respostas. Tente novamente.",
      );
      setSubmitting(false);
    }
  };

  const roundTitle =
    questions.length === 1
      ? questions[0]?.topic ?? "Diagnóstico adaptativo"
      : "Diagnóstico adaptativo";

  const roundIntro =
    "Sem certo ou errado — quanto mais honesto, mais útil sua trilha. A IA escolhe as próximas perguntas com base no que já sabe sobre você.";

  if (loading) {
    return (
      <main
        className="min-h-screen grid-dots px-4 py-8 lg:px-8"
        data-testid="diagnostic-pills"
      >
        <div className="mx-auto flex max-w-6xl items-center justify-center py-24">
          <div className="flex items-center gap-3 text-sm text-text-secondary">
            <div className="h-5 w-5 animate-spin rounded-full border-2 border-accent border-t-transparent" />
            Preparando entrevista adaptativa…
          </div>
        </div>
      </main>
    );
  }

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
                Rodada {roundCount}/{MAX_ROUNDS}
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
              {mappingProgress.map((item) => {
                const status = activeTopics.has(item.label)
                  ? "active"
                  : mapStatusFromProgress(item);
                return (
                  <li
                    key={item.rubric_key}
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
                    {item.label}
                  </li>
                );
              })}
            </ul>
          </div>
        </aside>

        <section className="rounded-card border border-border bg-surface p-6">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div className="text-sm text-text-secondary">
              Passo <strong>2/3</strong> · Diagnóstico · Rodada {roundCount} de{" "}
              {MAX_ROUNDS}
            </div>
            <PillRound label={roundTitle} />
          </div>

          <p className="mt-4 text-sm text-text-secondary">{roundIntro}</p>

          <div className="mt-6 grid gap-4">
            {questions.map((question) => (
              <div
                key={question.id}
                className="rounded-card border border-border-soft bg-surface-elevated p-4"
              >
                <div className="mb-3 flex flex-wrap items-center gap-2">
                  <PillRound label={question.topic} />
                  <p className="text-sm font-medium text-text-primary">
                    {question.question}
                  </p>
                </div>
                <textarea
                  data-testid={`answer-${question.id}`}
                  className="min-h-[96px] w-full rounded-lg border border-border bg-bg px-3 py-2 text-sm text-text-primary outline-none ring-accent focus:ring-2"
                  placeholder={question.example_of_answer}
                  value={answers[question.id] ?? ""}
                  disabled={submitting}
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

          {submitting ? (
            <div
              className="mt-6 flex items-center gap-3 rounded-card border border-border-soft bg-surface-elevated p-4"
              data-testid="diagnosis-generating"
            >
              <div className="h-5 w-5 animate-spin rounded-full border-2 border-accent border-t-transparent" />
              <div className="text-sm text-text-secondary">
                <strong className="text-text-primary">Processando respostas…</strong>{" "}
                a IA está atualizando seu mapa de competências.
              </div>
            </div>
          ) : (
            <div className="mt-6 flex flex-wrap items-center justify-between gap-4">
              <span className="text-sm text-text-muted">
                {questions.length} pergunta(s) nesta rodada · responda todas
                para continuar
              </span>
              <Button
                data-testid="submit-round"
                disabled={!roundComplete || questions.length === 0}
                onClick={() => void submitRound()}
              >
                {roundCount >= MAX_ROUNDS ? "Gerar diagnóstico" : "Próxima rodada"} →
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
