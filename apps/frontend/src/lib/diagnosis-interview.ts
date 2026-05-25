import type {
  CvAttachment,
  DiagnosisIntake,
  DiagnosisInterviewCvAttachment,
  YearsXpRange,
} from "@/types/contracts";

/** Mirror backend diagnosis_interview.py interview limits. */
export const MAX_INTERVIEW_ROUNDS = 5;
export const MAX_QUESTIONS_PER_TURN = 2;
export const MIN_ANSWER_LENGTH = 8;

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
