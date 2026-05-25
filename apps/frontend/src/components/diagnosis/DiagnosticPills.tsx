"use client";

import { Button } from "@/components/ui";
import { OnboardingRecapSidebar } from "@/components/diagnosis/OnboardingRecapSidebar";
import { CAREER_GOALS } from "@/lib/onboarding-data";
import { getCvAttachment } from "@/lib/onboarding-session";
import { interviewRoundLabel } from "@/lib/diagnosis-interview";
import { useDiagnosisInterview } from "@/lib/hooks/useDiagnosisInterview";

import { PillRound } from "./PillRound";

const ROUND_INTRO =
  "Sem certo ou errado — são 2 etapas fixas. Quanto mais concreto, melhor a IA mapeia seu perfil.";

export function DiagnosticPills() {
  const {
    intake,
    questions,
    mappingProgress,
    answers,
    roundCount,
    bootstrapping,
    submitting,
    streaming,
    streamPhaseLabel,
    analyzingKey,
    error,
    activeKeys,
    roundComplete,
    progressPct,
    setAnswer,
    submitRound,
    maxRounds,
  } = useDiagnosisInterview();

  if (!intake) return null;

  const goalTitle =
    CAREER_GOALS.find((goal) => goal.id === intake.goalId)?.title ??
    intake.goalId;
  const cvAttachment = getCvAttachment();

  const roundTitle = interviewRoundLabel(roundCount);

  return (
    <main
      className="min-h-screen grid-dots px-4 py-8 lg:px-8"
      data-testid="diagnostic-pills"
    >
      <div className="mx-auto grid max-w-6xl gap-6 lg:grid-cols-[320px_1fr]">
        <OnboardingRecapSidebar
          goalTitle={goalTitle}
          motivation={intake.motivation}
          yearsXp={intake.yearsXp}
          cvAttachment={cvAttachment}
          bootstrapping={bootstrapping}
          streaming={streaming}
          streamPhaseLabel={streamPhaseLabel}
          roundCount={roundCount}
          progressPct={progressPct}
          mappingProgress={mappingProgress}
          activeKeys={activeKeys}
          analyzingKey={analyzingKey}
        />

        <section className="rounded-card border border-border bg-surface p-6">
          {bootstrapping ? (
            <div className="space-y-4" data-testid="diagnosis-bootstrapping">
              <div className="h-6 w-40 animate-pulse rounded bg-surface-elevated" />
              <div className="h-4 w-full max-w-md animate-pulse rounded bg-surface-elevated" />
              <div className="mt-6 h-32 animate-pulse rounded-card bg-surface-elevated" />
              <p className="text-sm text-text-muted">{streamPhaseLabel}</p>
            </div>
          ) : (
            <>
              <div className="flex flex-wrap items-center gap-3">
                <PillRound label={roundTitle} />
              </div>

              <p className="mt-4 text-sm text-text-secondary">{ROUND_INTRO}</p>

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
                      onChange={(event) => setAnswer(question.id, event.target.value)}
                    />
                  </div>
                ))}
              </div>

              <div className="mt-6 flex flex-wrap items-center justify-between gap-4">
                <span className="text-sm text-text-muted">
                  {questions.length} pergunta(s) nesta rodada · responda todas
                  para continuar
                </span>
                <Button
                  data-testid="submit-round"
                  disabled={!roundComplete || questions.length === 0 || submitting}
                  onClick={() => void submitRound()}
                >
                  {roundCount >= maxRounds ? "Gerar diagnóstico" : "Próxima rodada"} →
                </Button>
              </div>
            </>
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
