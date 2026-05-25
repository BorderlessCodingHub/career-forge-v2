"use client";

import Link from "next/link";
import { useCallback, useEffect, useState } from "react";

import { Button } from "@/components/ui";
import { storeAdaptiveSession } from "@/lib/adaptive-session";
import {
  getMockInterviewQuestions,
  getValidationQuestions,
  submitMockInterview,
  submitValidation,
} from "@/lib/api-client";
import type {
  MockInterviewQuestion,
  PlanUpdateResponse,
  ValidationQuestion,
  ValidationResponse,
} from "@/types/contracts";

import { ValidationResult } from "./ValidationResult";

export type InterviewMode = "loop" | "quick";

type InterviewLoopProps = {
  nodeId: string;
  mode?: InterviewMode;
};

type Phase = "loading" | "interview" | "submitting" | "result";

type InterviewQuestion = ValidationQuestion | MockInterviewQuestion;

const MODE_COPY: Record<
  InterviewMode,
  {
    screen: string;
    title: string;
    subtitle: string;
    badge: string;
    loading: string;
    loadError: string;
    footer: string;
    answerTestId: string;
    submitTestId: string;
  }
> = {
  loop: {
    screen: "mock-interview-loop",
    title: "Mock interview — validação profunda",
    subtitle:
      "5–7 perguntas contextuais antes de liberar o próximo tópico. Suas respostas recalibram a trilha automaticamente.",
    badge: "MI",
    loading: "Preparando mock interview…",
    loadError: "Falha ao carregar mock interview",
    footer: "Mock interview retroalimenta o plano — lacunas detectadas recalibram a trilha",
    answerTestId: "mock-interview-answer",
    submitTestId: "mock-interview-submit",
  },
  quick: {
    screen: "validation",
    title: "Pronto para validar seu aprendizado?",
    subtitle:
      "A IA vai te entrevistar antes de liberar o próximo tópico. Pense como se estivesse explicando para um colega.",
    badge: "/v",
    loading: "Preparando entrevista…",
    loadError: "Falha ao carregar entrevista",
    footer: "Avaliação por evidência — não basta marcar como concluído",
    answerTestId: "validation-answer",
    submitTestId: "validation-submit",
  },
};

function isMockQuestion(question: InterviewQuestion): question is MockInterviewQuestion {
  return "phase" in question;
}

export function InterviewLoop({ nodeId, mode = "loop" }: InterviewLoopProps) {
  const copy = MODE_COPY[mode];
  const [phase, setPhase] = useState<Phase>("loading");
  const [questions, setQuestions] = useState<InterviewQuestion[]>([]);
  const [nodeTitle, setNodeTitle] = useState("");
  const [currentIndex, setCurrentIndex] = useState(0);
  const [answers, setAnswers] = useState<Record<string, string>>({});
  const [draft, setDraft] = useState("");
  const [result, setResult] = useState<ValidationResponse | null>(null);
  const [planUpdate, setPlanUpdate] = useState<PlanUpdateResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const loadQuestions = useCallback(async () => {
    setPhase("loading");
    setError(null);
    try {
      const payload =
        mode === "loop"
          ? await getMockInterviewQuestions(nodeId)
          : await getValidationQuestions(nodeId);
      setQuestions(payload.questions);
      setNodeTitle(payload.node_title);
      setCurrentIndex(0);
      setAnswers({});
      setDraft("");
      setResult(null);
      setPlanUpdate(null);
      setPhase("interview");
    } catch (err) {
      setError(err instanceof Error ? err.message : copy.loadError);
      setPhase("interview");
    }
  }, [copy.loadError, mode, nodeId]);

  useEffect(() => {
    void loadQuestions();
  }, [loadQuestions]);

  const currentQuestion = questions[currentIndex];
  const totalQuestions = questions.length;
  const canAdvance = phase !== "submitting" && draft.trim().length >= 10;

  const goNext = () => {
    if (!currentQuestion || !canAdvance) return;
    const nextAnswers = { ...answers, [currentQuestion.id]: draft.trim() };
    setAnswers(nextAnswers);
    setDraft("");

    if (currentIndex < questions.length - 1) {
      setCurrentIndex((index) => index + 1);
      return;
    }

    void submitAll(nextAnswers);
  };

  const submitAll = async (finalAnswers: Record<string, string>) => {
    setPhase("submitting");
    setError(null);
    try {
      const payload = {
        node_id: nodeId,
        node_title: nodeTitle,
        rubric: questions.map((question) => question.rubric_criterion),
        answers: questions.map((question) => ({
          question_id: question.id,
          answer: finalAnswers[question.id] ?? "",
        })),
      };
      const response =
        mode === "loop" ? await submitMockInterview(payload) : await submitValidation(payload);
      setResult(response.validation);
      if (response.plan_update && response.roadmap) {
        setPlanUpdate(response.plan_update);
        storeAdaptiveSession({
          plan: response.plan_update,
          roadmap: response.roadmap,
          nodeId,
        });
      }
      setPhase("result");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Falha ao avaliar respostas");
      setPhase("interview");
    }
  };

  const handleAnswerKeyDown = (event: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      goNext();
    }
  };

  if (phase === "result" && result) {
    return (
      <ValidationResult
        nodeTitle={nodeTitle}
        result={result}
        planUpdate={planUpdate}
        onRetry={() => {
          void loadQuestions();
        }}
      />
    );
  }

  if (phase === "loading") {
    return <p className="py-20 text-center text-sm text-text-muted animate-pulse">{copy.loading}</p>;
  }

  if (error && !currentQuestion) {
    return (
      <div className="mx-auto max-w-lg py-20 text-center">
        <p className="text-sm text-danger">{error}</p>
        <Link href="/roadmap" className="mt-4 inline-block">
          <Button variant="ghost">Voltar à trilha</Button>
        </Link>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-3xl px-4 py-10" data-screen={copy.screen}>
      <div className="text-center">
        <h1 className="text-3xl font-semibold text-text-primary">{copy.title}</h1>
        <p className="mt-2 text-sm text-text-secondary">{copy.subtitle}</p>
      </div>

      {currentQuestion && (
        <>
          <div className="mt-8 flex flex-wrap items-center justify-between gap-4 rounded-xl border border-border bg-surface px-4 py-3">
            <div className="flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-accent/20 text-sm font-semibold text-accent">
                {copy.badge}
              </div>
              <p className="font-medium text-text-primary">{nodeTitle}</p>
            </div>
            <div className="flex items-center gap-2 text-xs text-text-muted">
              <span>
                Pergunta <strong className="text-text-primary">{currentIndex + 1}</strong> de{" "}
                {totalQuestions}
              </span>
              {questions.map((question, index) => (
                <span
                  key={question.id}
                  className={`h-2 w-2 rounded-full ${
                    index < currentIndex
                      ? "bg-success"
                      : index === currentIndex
                        ? "bg-accent"
                        : "bg-border"
                  }`}
                />
              ))}
            </div>
          </div>

          <div className="mt-6 rounded-xl border border-border bg-surface-elevated p-6">
            <p className="text-xs uppercase tracking-widest text-text-muted">
              Pergunta {String(currentIndex + 1).padStart(2, "0")} · {currentQuestion.label}
              {isMockQuestion(currentQuestion) && currentQuestion.phase !== "base" && (
                <span className="ml-2 rounded bg-accent/20 px-1.5 py-0.5 text-accent">
                  {currentQuestion.phase === "gap_probe" ? "lacuna" : "cenário"}
                </span>
              )}
            </p>
            <p className="mt-3 text-lg text-text-primary">{currentQuestion.prompt}</p>
            {currentQuestion.hint && (
              <p className="mt-2 text-sm text-text-muted">Dica: {currentQuestion.hint}</p>
            )}
          </div>

          <div className="mt-4">
            <textarea
              value={draft}
              onChange={(event) => setDraft(event.target.value)}
              onKeyDown={handleAnswerKeyDown}
              placeholder="Comece pela sua intuição..."
              disabled={phase === "submitting"}
              className="min-h-[160px] w-full rounded-xl border border-border bg-surface px-4 py-3 text-sm text-text-primary placeholder:text-text-muted"
              data-testid={copy.answerTestId}
            />
            <div className="mt-2 flex justify-between text-xs text-text-muted">
              <span>{draft.length} caracteres · sem limite</span>
              <span>Enter para avançar · Shift+Enter nova linha</span>
            </div>
          </div>
        </>
      )}

      {error && (
        <p className="mt-4 rounded-lg border border-danger/30 bg-danger/10 p-3 text-sm text-danger">
          {error}
        </p>
      )}

      <div className="mt-8 flex flex-wrap items-center justify-between gap-3">
        <p className="text-xs text-text-muted">{copy.footer}</p>
        <div className="flex gap-2">
          <Link href="/roadmap">
            <Button variant="ghost">Desistir</Button>
          </Link>
          <Button
            disabled={!canAdvance}
            onClick={goNext}
            data-testid={copy.submitTestId}
          >
            {phase === "submitting"
              ? "Avaliando…"
              : currentIndex === questions.length - 1
                ? "Enviar respostas →"
                : "Próxima pergunta →"}
          </Button>
        </div>
      </div>
    </div>
  );
}
