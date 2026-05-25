import type { DiagnosisResponse } from "@/types/contracts";

const GOAL_KEY = "career-forge.goal";
const MOTIVATION_KEY = "career-forge.motivation";
const YEARS_XP_KEY = "career-forge.years-xp";
const CV_ATTACHMENT_KEY = "career-forge.cv-attachment";
const ANSWERS_KEY = "career-forge.answers";
const DIAGNOSIS_KEY = "career-forge.diagnosis";

export type YearsXpRange = "0-1" | "1-3" | "3-5" | "5+";

export type CvAttachment = {
  filename: string;
  size: number;
  mimeType: string;
  dataBase64: string;
};

function readJson<T>(key: string): T | null {
  if (typeof window === "undefined") return null;
  const raw = window.sessionStorage.getItem(key);
  if (!raw) return null;
  try {
    return JSON.parse(raw) as T;
  } catch {
    return null;
  }
}

function writeJson(key: string, value: unknown) {
  if (typeof window === "undefined") return;
  window.sessionStorage.setItem(key, JSON.stringify(value));
}

export function getSelectedGoal(): string | null {
  if (typeof window === "undefined") return null;
  return window.sessionStorage.getItem(GOAL_KEY);
}

export function setSelectedGoal(goalId: string) {
  if (typeof window === "undefined") return;
  window.sessionStorage.setItem(GOAL_KEY, goalId);
}

export function getMotivation(): string {
  if (typeof window === "undefined") return "";
  return window.sessionStorage.getItem(MOTIVATION_KEY) ?? "";
}

export function setMotivation(value: string) {
  if (typeof window === "undefined") return;
  window.sessionStorage.setItem(MOTIVATION_KEY, value);
}

export function getYearsXp(): YearsXpRange | null {
  if (typeof window === "undefined") return null;
  const raw = window.sessionStorage.getItem(YEARS_XP_KEY);
  if (raw === "0-1" || raw === "1-3" || raw === "3-5" || raw === "5+") return raw;
  return null;
}

export function setYearsXp(value: YearsXpRange) {
  if (typeof window === "undefined") return;
  window.sessionStorage.setItem(YEARS_XP_KEY, value);
}

export function getCvAttachment(): CvAttachment | null {
  return readJson<CvAttachment>(CV_ATTACHMENT_KEY);
}

export function setCvAttachment(attachment: CvAttachment) {
  writeJson(CV_ATTACHMENT_KEY, attachment);
}

export function clearCvAttachment() {
  if (typeof window === "undefined") return;
  window.sessionStorage.removeItem(CV_ATTACHMENT_KEY);
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
  if (typeof window === "undefined") return;
  [
    GOAL_KEY,
    MOTIVATION_KEY,
    YEARS_XP_KEY,
    CV_ATTACHMENT_KEY,
    ANSWERS_KEY,
    DIAGNOSIS_KEY,
  ].forEach((key) => window.sessionStorage.removeItem(key));
}
