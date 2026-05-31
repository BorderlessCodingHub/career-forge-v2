import type {
  CvAttachment,
  DiagnosisIntake,
  DiagnosisInterviewCvAttachment,
  YearsXpRange,
} from "@/types/contracts";

/** Mirror backend diagnosis_interview.py interview limits. */
export const MAX_INTERVIEW_ROUNDS = 2;
// Keep aligned with backend InterviewAnswer.text: explicit short answers like
// "Nada." are meaningful signals for hands-on baseline.
export const MIN_ANSWER_LENGTH = 1;

/** Deterministic round titles — mirror backend interview/script.py */
const INTERVIEW_ROUND_LABELS = [
  "Prática e rotina",
  "Contexto e limitações",
] as const;

export function interviewRoundLabel(roundCount: number): string {
  const index = Math.max(
    0,
    Math.min(roundCount - 1, INTERVIEW_ROUND_LABELS.length - 1),
  );
  return INTERVIEW_ROUND_LABELS[index];
}

export function toInterviewCv(cv: CvAttachment): DiagnosisInterviewCvAttachment {
  if (cv.mimeType !== "application/pdf") {
    throw new Error(
      "Currículo deve ser PDF. Remova o anexo ou envie um arquivo .pdf.",
    );
  }
  return {
    filename: cv.filename,
    mime_type: "application/pdf",
    content_base64: cv.dataBase64,
  };
}

export function buildInterviewIntake(input: {
  goalId: string;
  motivation: string;
  yearsXp: YearsXpRange;
  cv?: CvAttachment | null;
}): DiagnosisIntake {
  return {
    goal_id: input.goalId,
    motivation: input.motivation,
    years_xp: input.yearsXp,
    cv: input.cv ? toInterviewCv(input.cv) : undefined,
  };
}
