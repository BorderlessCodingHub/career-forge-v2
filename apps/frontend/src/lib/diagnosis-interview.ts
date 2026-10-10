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
  "Practice and routine",
  "Context and constraints",
] as const;

const INTERVIEW_ROUND_MESSAGE_KEYS = ["roundPractice", "roundContext"] as const;

export type InterviewRoundMessageKey = (typeof INTERVIEW_ROUND_MESSAGE_KEYS)[number];

function interviewRoundIndex(roundCount: number): number {
  return Math.max(
    0,
    Math.min(roundCount - 1, INTERVIEW_ROUND_LABELS.length - 1),
  );
}

export function interviewRoundLabel(roundCount: number): string {
  return INTERVIEW_ROUND_LABELS[interviewRoundIndex(roundCount)];
}

export function interviewRoundMessageKey(roundCount: number): InterviewRoundMessageKey {
  return INTERVIEW_ROUND_MESSAGE_KEYS[interviewRoundIndex(roundCount)];
}

export function toInterviewCv(cv: CvAttachment): DiagnosisInterviewCvAttachment {
  if (cv.mimeType !== "application/pdf") {
    throw new Error(
      "Resume must be a PDF. Remove the attachment or upload a .pdf file.",
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
