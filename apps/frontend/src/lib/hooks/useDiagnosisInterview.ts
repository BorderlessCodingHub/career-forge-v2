"use client";

import { useRouter } from "next/navigation";
import { useCallback, useEffect, useMemo, useState } from "react";

import {
  streamDiagnosisInterviewStart,
  streamDiagnosisInterviewTurn,
} from "@/lib/api-client";
import { buildSkeletonMappingProgress, profileCompletenessPct } from "@/lib/profile-dimensions";
import {
  buildInterviewIntake,
  MAX_INTERVIEW_ROUNDS,
  MAX_QUESTIONS_PER_TURN,
  MIN_ANSWER_LENGTH,
} from "@/lib/diagnosis-interview";
import {
  applyMappingDimensionEvent,
  diagnosisStreamPhaseLabel,
  nextAnalyzingKey,
} from "@/lib/diagnosis-stream";
import {
  getCvAttachment,
  getDiagnosisSessionId,
  getMotivation,
  getSelectedGoal,
  getYearsXp,
  setAnswers,
  setDiagnosisSessionId,
  setStoredDiagnosis,
} from "@/lib/onboarding-session";
import type {
  DiagnosisInterviewStatusPhase,
  DiagnosisStreamEvent,
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

type InterviewPhase = "bootstrapping" | "ready" | "submitting";

function readOnboardingIntake(): OnboardingIntake | null {
  const goalId = getSelectedGoal();
  const motivation = getMotivation().trim();
  const yearsXp = getYearsXp();
  if (!goalId || motivation.length < 20 || !yearsXp) return null;
  return { goalId, motivation, yearsXp };
}

function answersForQuestions(
  questions: InterviewQuestion[],
  answers: Record<string, string>,
): Record<string, string> {
  return Object.fromEntries(
    questions.map((question) => [question.id, answers[question.id]?.trim() ?? ""]),
  );
}

function handleStreamEvent(
  event: DiagnosisStreamEvent,
  setters: {
    setStreamPhase: (phase: DiagnosisInterviewStatusPhase | null) => void;
    setAnalyzingKey: (key: RubricDimensionKey | null) => void;
    setMappingProgress: React.Dispatch<React.SetStateAction<RubricMapItem[]>>;
  },
) {
  if (event.type === "interview_status") {
    setters.setStreamPhase(event.phase);
    if (event.phase === "judging") {
      setters.setAnalyzingKey("motivation_goal");
    }
    return;
  }

  if (event.type === "mapping_dimension") {
    setters.setMappingProgress((current) => {
      const updated = applyMappingDimensionEvent(current, event);
      setters.setAnalyzingKey(nextAnalyzingKey(updated, event.item.rubric_key));
      return updated;
    });
  }
}

export function useDiagnosisInterview() {
  const router = useRouter();
  const intake = useMemo(() => readOnboardingIntake(), []);

  const [sessionId, setSessionId] = useState<string | null>(() =>
    getDiagnosisSessionId(),
  );
  const [questions, setQuestions] = useState<InterviewQuestion[]>([]);
  const [mappingProgress, setMappingProgress] = useState<RubricMapItem[]>(
    buildSkeletonMappingProgress,
  );
  const [answers, setAnswersState] = useState<Record<string, string>>({});
  const [roundCount, setRoundCount] = useState(0);
  const [phase, setPhase] = useState<InterviewPhase>("bootstrapping");
  const [streamPhase, setStreamPhase] = useState<DiagnosisInterviewStatusPhase | null>(
    "analyzing_intake",
  );
  const [analyzingKey, setAnalyzingKey] = useState<RubricDimensionKey | null>(
    "motivation_goal",
  );
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!intake) router.replace("/");
  }, [intake, router]);

  const streamSetters = useMemo(
    () => ({
      setStreamPhase,
      setAnalyzingKey,
      setMappingProgress,
    }),
    [],
  );

  const applyTurnResponse = useCallback(
    (response: InterviewTurnResponse): boolean => {
      setSessionId(response.session_id);
      setDiagnosisSessionId(response.session_id);
      setMappingProgress(response.mapping_progress);
      setStreamPhase(null);
      setAnalyzingKey(null);

      if (response.status === "complete" && response.diagnosis) {
        setStoredDiagnosis(response.diagnosis);
        return true;
      }

      setQuestions(response.questions);
      setAnswersState(
        Object.fromEntries(
          response.questions.map((question) => [question.id, ""]),
        ),
      );
      return false;
    },
    [],
  );

  useEffect(() => {
    if (!intake) return;
    const readyIntake = intake;

    let cancelled = false;

    async function bootstrap() {
      setPhase("bootstrapping");
      setStreamPhase("analyzing_intake");
      setAnalyzingKey("motivation_goal");
      setMappingProgress(buildSkeletonMappingProgress());
      setError(null);
      try {
        const response = await streamDiagnosisInterviewStart(
          buildInterviewIntake({
            goalId: readyIntake.goalId,
            motivation: readyIntake.motivation,
            yearsXp: readyIntake.yearsXp,
            cv: getCvAttachment(),
          }),
          (event) => {
            if (cancelled) return;
            handleStreamEvent(event, streamSetters);
          },
        );
        if (cancelled) return;
        const completed = applyTurnResponse(response);
        if (completed) {
          router.push("/onboarding/edit");
          return;
        }
        setRoundCount(1);
        setPhase("ready");
      } catch (cause) {
        if (cancelled) return;
        setError(
          cause instanceof Error
            ? cause.message
            : "Não foi possível iniciar o diagnóstico.",
        );
        setPhase("ready");
      }
    }

    void bootstrap();
    return () => {
      cancelled = true;
    };
  }, [applyTurnResponse, intake, router, streamSetters]);

  const activeKeys = useMemo(
    () => new Set(questions.map((question) => question.rubric_key)),
    [questions],
  );

  const roundComplete = questions.every(
    (question) => (answers[question.id]?.trim().length ?? 0) >= MIN_ANSWER_LENGTH,
  );

  const progressPct = useMemo(
    () => profileCompletenessPct(mappingProgress),
    [mappingProgress],
  );

  const setAnswer = useCallback((questionId: string, text: string) => {
    setAnswersState((current) => ({ ...current, [questionId]: text }));
  }, []);

  const submitRound = useCallback(async () => {
    if (!roundComplete || phase !== "ready" || !sessionId) return;

    setPhase("submitting");
    setStreamPhase("processing_answers");
    setAnalyzingKey(null);
    setError(null);

    const turnAnswers = questions.map((question) => ({
      question_id: question.id,
      text: answers[question.id]?.trim() ?? "",
    }));

    try {
      setAnswers(answersForQuestions(questions, answers));

      const response = await streamDiagnosisInterviewTurn(
        sessionId,
        { answers: turnAnswers },
        (event) => handleStreamEvent(event, streamSetters),
      );

      if (response.status === "complete" && response.diagnosis) {
        setStoredDiagnosis(response.diagnosis);
        router.push("/onboarding/edit");
        return;
      }

      applyTurnResponse(response);
      setRoundCount((count) => count + 1);
    } catch (cause) {
      setError(
        cause instanceof Error
          ? cause.message
          : "Não foi possível enviar suas respostas. Tente novamente.",
      );
    } finally {
      setPhase("ready");
      setStreamPhase(null);
      setAnalyzingKey(null);
    }
  }, [
    answers,
    applyTurnResponse,
    phase,
    questions,
    roundComplete,
    router,
    sessionId,
    streamSetters,
  ]);

  return {
    intake,
    questions,
    mappingProgress,
    answers,
    roundCount,
    bootstrapping: phase === "bootstrapping",
    submitting: phase === "submitting",
    streaming: phase === "bootstrapping" || phase === "submitting",
    streamPhaseLabel: diagnosisStreamPhaseLabel(streamPhase),
    analyzingKey,
    error,
    activeKeys: activeKeys as Set<RubricDimensionKey>,
    roundComplete,
    progressPct,
    setAnswer,
    submitRound,
    maxRounds: MAX_INTERVIEW_ROUNDS,
  };
}
