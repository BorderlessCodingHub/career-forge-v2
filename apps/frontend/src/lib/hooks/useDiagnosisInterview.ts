"use client";

import { useRouter } from "next/navigation";
import { useCallback, useEffect, useMemo, useState } from "react";

import {
  getDiagnosisInterviewSession,
  streamDiagnosisInterviewStart,
  streamDiagnosisInterviewTurn,
} from "@/lib/api-client";
import {
  applyDiagnosisStreamEvent,
  createInitialDiagnosisStreamState,
  diagnosisStreamPhaseLabel,
  firstPendingAnalyzingKey,
  hydrateMappingFromResponse,
  type DiagnosisStreamUiState,
} from "@/lib/diagnosis-stream";
import {
  buildInterviewIntake,
  MAX_INTERVIEW_ROUNDS,
  MIN_ANSWER_LENGTH,
} from "@/lib/diagnosis-interview";
import { buildSkeletonMappingProgress, profileCompletenessPct } from "@/lib/profile-dimensions";
import {
  clearDiagnosisSessionId,
  clearStoredDiagnosis,
  getCvAttachment,
  getDiagnosisSessionId,
  getMotivation,
  getSelectedGoal,
  getStoredDiagnosis,
  getYearsXp,
  setAnswers,
  setDiagnosisSessionId,
  setStoredDiagnosis,
} from "@/lib/onboarding-session";
import type {
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

type InterviewPhase = "bootstrapping" | "ready" | "submitting" | "complete";

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

function hydrateInterviewResponse(response: InterviewTurnResponse): {
  mappingProgress: RubricMapItem[];
  questions: InterviewQuestion[];
  answers: Record<string, string>;
  roundCount: number;
} {
  return {
    mappingProgress: hydrateMappingFromResponse(response),
    questions: response.questions,
    answers: Object.fromEntries(
      response.questions.map((question) => [question.id, ""]),
    ),
    roundCount: Math.max(1, response.round_count || 1),
  };
}

export function useDiagnosisInterview() {
  const router = useRouter();
  const intake = useMemo(() => readOnboardingIntake(), []);

  const [sessionId, setSessionId] = useState<string | null>(() =>
    getDiagnosisSessionId(),
  );
  const [questions, setQuestions] = useState<InterviewQuestion[]>([]);
  const [streamUi, setStreamUi] = useState<DiagnosisStreamUiState>(
    createInitialDiagnosisStreamState,
  );
  const [answers, setAnswersState] = useState<Record<string, string>>({});
  const [roundCount, setRoundCount] = useState(0);
  const [phase, setPhase] = useState<InterviewPhase>("bootstrapping");
  const [error, setError] = useState<string | null>(null);

  const { mappingProgress, streamPhase, analyzingKey } = streamUi;

  useEffect(() => {
    if (!intake) {
      router.replace("/");
      return;
    }
    if (getStoredDiagnosis()) {
      router.replace("/onboarding/edit");
    }
  }, [intake, router]);

  const dispatchStreamEvent = useCallback((event: DiagnosisStreamEvent) => {
    setStreamUi((current) => applyDiagnosisStreamEvent(current, event));
  }, []);

  const finishWithDiagnosis = useCallback(
    (diagnosis: NonNullable<InterviewTurnResponse["diagnosis"]>) => {
      setStoredDiagnosis(diagnosis);
      clearDiagnosisSessionId();
      setPhase("complete");
      router.push("/onboarding/edit");
    },
    [router],
  );

  const applyTurnResponse = useCallback(
    (
      response: InterviewTurnResponse,
      options?: { preserveMapping?: boolean },
    ): boolean => {
      setSessionId(response.session_id);
      setDiagnosisSessionId(response.session_id);

      setStreamUi((current) => ({
        ...current,
        streamPhase: null,
        analyzingKey: null,
        mappingProgress: hydrateMappingFromResponse(
          response,
          options?.preserveMapping ? current.mappingProgress : undefined,
        ),
      }));

      if (response.status === "complete" && response.diagnosis) {
        finishWithDiagnosis(response.diagnosis);
        return true;
      }

      const hydrated = hydrateInterviewResponse(response);
      setQuestions(hydrated.questions);
      setAnswersState(hydrated.answers);
      setRoundCount(hydrated.roundCount);
      return false;
    },
    [finishWithDiagnosis],
  );

  useEffect(() => {
    if (!intake || getStoredDiagnosis()) return;

    const readyIntake = intake;
    let cancelled = false;

    async function bootstrap() {
      const existingSessionId = getDiagnosisSessionId();
      if (existingSessionId) {
        setPhase("bootstrapping");
        setError(null);
        try {
          const response = await getDiagnosisInterviewSession(existingSessionId);
          if (cancelled) return;

          if (response.status === "complete" && response.diagnosis) {
            finishWithDiagnosis(response.diagnosis);
            return;
          }

          const hydrated = hydrateInterviewResponse(response);
          setSessionId(response.session_id);
          setStreamUi({
            streamPhase: null,
            analyzingKey: null,
            mappingProgress: hydrated.mappingProgress,
          });
          setQuestions(hydrated.questions);
          setAnswersState(hydrated.answers);
          setRoundCount(hydrated.roundCount);
          setPhase("ready");
          return;
        } catch {
          if (cancelled) return;
          clearDiagnosisSessionId();
        }
      }

      setPhase("bootstrapping");
      setStreamUi({
        streamPhase: "analyzing_intake",
        analyzingKey: "motivation_goal",
        mappingProgress: buildSkeletonMappingProgress(),
      });
      setError(null);
      clearStoredDiagnosis();

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
            dispatchStreamEvent(event);
          },
        );
        if (cancelled) return;

        const completed = applyTurnResponse(response);
        if (completed) return;

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
  }, [applyTurnResponse, dispatchStreamEvent, finishWithDiagnosis, intake, router]);

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
    setStreamUi((current) => ({
      ...current,
      streamPhase: "processing_answers",
      analyzingKey: firstPendingAnalyzingKey(current.mappingProgress),
    }));
    setError(null);

    const turnAnswers = questions.map((question) => ({
      question_id: question.id,
      text: answers[question.id]?.trim() ?? "",
    }));

    let finished = false;

    try {
      setAnswers(answersForQuestions(questions, answers));

      const response = await streamDiagnosisInterviewTurn(
        sessionId,
        { answers: turnAnswers },
        (event) => dispatchStreamEvent(event),
      );

      if (response.status === "complete" && response.diagnosis) {
        finished = true;
        finishWithDiagnosis(response.diagnosis);
        return;
      }

      applyTurnResponse(response, { preserveMapping: true });
    } catch (cause) {
      setError(
        cause instanceof Error
          ? cause.message
          : "Não foi possível enviar suas respostas. Tente novamente.",
      );
    } finally {
      if (!finished) {
        setPhase("ready");
        setStreamUi((current) => ({
          ...current,
          streamPhase: null,
          analyzingKey: null,
        }));
      }
    }
  }, [
    answers,
    applyTurnResponse,
    dispatchStreamEvent,
    finishWithDiagnosis,
    phase,
    questions,
    roundComplete,
    sessionId,
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
