"use client";

import Link from "next/link";
import { useCallback, useEffect, useState } from "react";

import { Button } from "@/components/ui";
import { getValidationQuestions, submitValidation } from "@/lib/api-client";
import type { ValidationQuestion, ValidationResponse } from "@/types/contracts";

import { ValidationResult } from "./ValidationResult";

type ValidationInterviewProps = {
  nodeId: string;
};

type Phase = "loading" | "interview" | "submitting" | "result";

export function ValidationInterview({ nodeId }: ValidationInterviewProps) {
  const [phase, setPhase] = useState<Phase>("loading");
  const [questions, setQuestions] = useState<ValidationQuestion[]>([]);
  const [nodeTitle, setNodeTitle] = useState("");
  const [currentIndex, setCurrentIndex] = useState(0);
  const [answers, setAnswers] = useState<Record<string, string>>({});
  const [draft, setDraft] = useState("");
  const [result, setResult] = useState<ValidationResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const loadQuestions = useCallback(async () => {
    setPhase("loading");
    setError(null);
    try {
      const payload = await getValidationQuestions(nodeId);
      setQuestions(payload.questions);
      setNodeTitle(payload.node_title);
      setCurrentIndex(0);
      setAnswers({});
      setDraft("");
      setResult(null);
      setPhase("interview");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Falha ao carregar entrevista");
      setPhase("interview");
    }
  }, [nodeId]);

  useEffect(() => {
    void loadQuestions();
  }, [loadQuestions]);

  const currentQuestion = questions[currentIndex];

  const goNext = () => {
    if (!currentQuestion) return;
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
      const response = await submitValidation({
        node_id: nodeId,
        node_title: nodeTitle,
        rubric: questions.map((question) => question.rubric_criterion),
        answers: questions.map((question) => ({
          question_id: question.id,
          answer: finalAnswers[question.id] ?? "",
        })),
      });
      setResult(response.validation);
      setPhase("result");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Falha ao avaliar respostas");
      setPhase("interview");
    }
  };

  if (phase === "result" && result) {
    return (
      <ValidationResult
        nodeTitle={nodeTitle}
        result={result}
        onRetry={() => {
          void loadQuestions();
        }}
      />
    );
  }

  if (phase === "loading") {
    return (
      <p className="py-20 text-center text-sm text-text-muted animate-pulse">
        Preparando entrevista…
      </p>
    );
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
    <div className="mx-auto max-w-3xl px-4 py-10" data-screen="validation">
      <div className="text-center">
        <h1 className="text-3xl font-semibold text-text-primary">
          Pronto para validar seu aprendizado?
        </h1>
        <p className="mt-2 text-sm text-text-secondary">
          A IA vai te entrevistar antes de liberar o próximo tópico. Pense como se estivesse
          explicando para um colega.
        </p>
      </div>

      {currentQuestion && (
        <>
          <div className="mt-8 flex flex-wrap items-center justify-between gap-4 rounded-xl border border-border bg-surface px-4 py-3">
            <div className="flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-accent/20 text-sm font-semibold text-accent">
                /v
              </div>
              <p className="font-medium text-text-primary">{nodeTitle}</p>
            </div>
            <div className="flex items-center gap-2 text-xs text-text-muted">
              <span>
                Pergunta <strong className="text-text-primary">{currentIndex + 1}</strong> de 3
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
              placeholder="Comece pela sua intuição..."
              disabled={phase === "submitting"}
              className="min-h-[160px] w-full rounded-xl border border-border bg-surface px-4 py-3 text-sm text-text-primary placeholder:text-text-muted"
              data-testid="validation-answer"
            />
            <div className="mt-2 flex justify-between text-xs text-text-muted">
              <span>{draft.length} caracteres · sem limite</span>
              <span>Enter para avançar</span>
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
        <p className="text-xs text-text-muted">Avaliação por evidência — não basta marcar como concluído</p>
        <div className="flex gap-2">
          <Link href="/roadmap">
            <Button variant="ghost">Desistir</Button>
          </Link>
          <Button
            disabled={phase === "submitting" || draft.trim().length < 10}
            onClick={goNext}
            data-testid="validation-submit"
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
