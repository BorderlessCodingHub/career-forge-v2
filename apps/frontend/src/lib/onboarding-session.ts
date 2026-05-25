import type { DiagnosisResponse } from "@/types/contracts";

const GOAL_KEY = "career-forge.goal";
const MOTIVATION_KEY = "career-forge.motivation";
const ANSWERS_KEY = "career-forge.answers";
const DIAGNOSIS_KEY = "career-forge.diagnosis";

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
  [GOAL_KEY, MOTIVATION_KEY, ANSWERS_KEY, DIAGNOSIS_KEY].forEach((key) =>
    window.sessionStorage.removeItem(key),
  );
}
