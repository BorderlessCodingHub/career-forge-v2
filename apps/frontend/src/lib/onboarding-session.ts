import {
  readJson,
  readString,
  removeItem,
  removeItems,
  writeJson,
  writeString,
} from "@/lib/session/storage";
import type { CvAttachment, DiagnosisResponse, YearsXpRange } from "@/types/contracts";

export type { CvAttachment, YearsXpRange } from "@/types/contracts";

const GOAL_KEY = "career-forge.goal";
const MOTIVATION_KEY = "career-forge.motivation";
const YEARS_XP_KEY = "career-forge.years-xp";
const CV_ATTACHMENT_KEY = "career-forge.cv-attachment";
const DIAGNOSIS_SESSION_KEY = "career-forge.diagnosis-session-id";
const ANSWERS_KEY = "career-forge.answers";
const DIAGNOSIS_KEY = "career-forge.diagnosis";

export function getSelectedGoal(): string | null {
  return readString(GOAL_KEY);
}

export function setSelectedGoal(goalId: string) {
  writeString(GOAL_KEY, goalId);
}

export function getMotivation(): string {
  return readString(MOTIVATION_KEY) ?? "";
}

export function setMotivation(value: string) {
  writeString(MOTIVATION_KEY, value);
}

export function getYearsXp(): YearsXpRange | null {
  const raw = readString(YEARS_XP_KEY);
  if (raw === "0-1" || raw === "1-3" || raw === "3-5" || raw === "5+") return raw;
  return null;
}

export function setYearsXp(value: YearsXpRange) {
  writeString(YEARS_XP_KEY, value);
}

export function getCvAttachment(): CvAttachment | null {
  return readJson<CvAttachment>(CV_ATTACHMENT_KEY);
}

export function setCvAttachment(attachment: CvAttachment) {
  writeJson(CV_ATTACHMENT_KEY, attachment);
}

export function clearCvAttachment() {
  removeItem(CV_ATTACHMENT_KEY);
}

export function getDiagnosisSessionId(): string | null {
  return readString(DIAGNOSIS_SESSION_KEY);
}

export function setDiagnosisSessionId(sessionId: string) {
  writeString(DIAGNOSIS_SESSION_KEY, sessionId);
}

export function clearDiagnosisSessionId() {
  removeItem(DIAGNOSIS_SESSION_KEY);
}

export function getAnswers(): Record<string, string> {
  return readJson<Record<string, string>>(ANSWERS_KEY) ?? {};
}

export function setAnswers(answers: Record<string, string>) {
  writeJson(ANSWERS_KEY, answers);
}

export function getStoredDiagnosis(): DiagnosisResponse | null {
  return readJson<DiagnosisResponse>(DIAGNOSIS_KEY);
}

export function setStoredDiagnosis(diagnosis: DiagnosisResponse) {
  writeJson(DIAGNOSIS_KEY, diagnosis);
}

export function clearOnboardingSession() {
  removeItems([
    GOAL_KEY,
    MOTIVATION_KEY,
    YEARS_XP_KEY,
    CV_ATTACHMENT_KEY,
    DIAGNOSIS_SESSION_KEY,
    ANSWERS_KEY,
    DIAGNOSIS_KEY,
  ]);
}
