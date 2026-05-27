"use client";

import { useRouter } from "next/navigation";
import { useCallback, useEffect, useMemo, useState } from "react";

import {
  startDiagnosisInterview,
  submitDiagnosisTurn,
} from "@/lib/api-client";
import { buildSkeletonMappingProgress } from "@/lib/ctrr-dimensions";
import {
  buildInterviewIntake,
  MAX_INTERVIEW_ROUNDS,
  MAX_QUESTIONS_PER_TURN,
  MIN_ANSWER_LENGTH,
} from "@/lib/diagnosis-interview";
import {
  getCvAttachment,
  getMotivation,
  getSelectedGoal,
  getStoredDiagnosis,
  getYearsXp,
  setAnswers,
  setDiagnosisSessionId,
  setStoredDiagnosis,
} from "@/lib/onboarding-session";
import type {
  InterviewQuestion,
  InterviewTurnResponse,
  RubricDimensionKey,
  RubricMapItem,
} from "@/types/contracts";

type OnboardingIntake = {
  goalId: string;
  motivation: string;
  yearsXp: NonNullable<ReturnType<typeof getYearsXp>>;
};

function readOnboardingIntake(): OnboardingIntake | null {
  const goalId = getSelectedGoal();
  const motivation = getMotivation().trim();
  const yearsXp = getYearsXp();
  if (!goalId || motivation.length < 20 || !yearsXp) return null;
  return { goalId, motivation, yearsXp };
}

export function useDiagnosisInterview() {
  const router = useRouter();
  const intake = useMemo(() => readOnboardingIntake(), []);

  const [sessionId, setSessionId] = useState<string | null>(null);
  const [questions, setQuestions] = useState<InterviewQuestion[]>([]);
  const [mappingProgress, setMappingProgress] = useState<RubricMapItem[]>(
    buildSkeletonMappingProgress,
  );
  const [answers, setAnswersState] = useState<Record<string, string>>({});
  const [roundCount, setRoundCount] = useState(0);
  const [bootstrapping, setBootstrapping] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!intake) {
      router.replace("/");
      return;
    }
    if (getStoredDiagnosis()) {
      router.replace("/onboarding/edit");
    }
  }, [intake, router]);

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
    if (!intake || getStoredDiagnosis()) return;
    const readyIntake = intake;

    let cancelled = false;

    async function bootstrap() {
      setBootstrapping(true);
      setError(null);
      try {
        const response = await startDiagnosisInterview(
          buildInterviewIntake({
            goalId: readyIntake.goalId,
            motivation: readyIntake.motivation,
            yearsXp: readyIntake.yearsXp,
            cv: getCvAttachment(),
          }),
        );
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
        if (!cancelled) setBootstrapping(false);
      }
    }

    void bootstrap();
    return () => {
      cancelled = true;
    };
  }, [applyTurnResponse, intake]);

  const activeKeys = useMemo(
    () => new Set(questions.map((question) => question.rubric_key)),
    [questions],
  );

  const roundComplete = questions.every(
    (question) => (answers[question.id]?.trim().length ?? 0) >= MIN_ANSWER_LENGTH,
  );

  const answeredInRound = questions.filter(
    (question) => (answers[question.id]?.trim().length ?? 0) >= MIN_ANSWER_LENGTH,
  ).length;

  const totalExpectedQuestions = Math.min(
    MAX_INTERVIEW_ROUNDS * MAX_QUESTIONS_PER_TURN,
    10,
  );
  const answeredTotal = (roundCount - 1) * MAX_QUESTIONS_PER_TURN + answeredInRound;
  const progressPct = Math.min(
    100,
    Math.round((answeredTotal / totalExpectedQuestions) * 100),
  );

  const setAnswer = useCallback((questionId: string, text: string) => {
    setAnswersState((current) => ({ ...current, [questionId]: text }));
  }, []);

  const submitRound = useCallback(async () => {
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
  }, [
    answers,
    applyTurnResponse,
    questions,
    roundComplete,
    router,
    sessionId,
    submitting,
  ]);

  return {
    intake,
    questions,
    mappingProgress,
    answers,
    roundCount,
    bootstrapping,
    submitting,
    error,
    activeKeys: activeKeys as Set<RubricDimensionKey>,
    roundComplete,
    progressPct,
    setAnswer,
    submitRound,
    maxRounds: MAX_INTERVIEW_ROUNDS,
  };
}
