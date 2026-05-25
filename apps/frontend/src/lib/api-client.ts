import type { DiagnosisResponse } from "@/types/contracts";

const backendUrl =
  process.env.NEXT_PUBLIC_BACKEND_URL ??
  process.env.NEXT_PUBLIC_API_URL ??
  "http://localhost:8000";

export async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${backendUrl}${path}`, {
    ...init,
    headers: { "Content-Type": "application/json", ...init?.headers },
  });
  if (!res.ok) throw new Error(`API ${path} failed: ${res.status}`);
  return res.json() as Promise<T>;
}

export type DiagnosisRunResponse = {
  run_id: string;
  status: string;
  events: Array<Record<string, unknown>>;
  diagnosis: DiagnosisResponse;
};

export type CreateDiagnosisPayload = {
  user_id?: string;
  goal_id: string;
  motivation: string;
  answers: Record<string, string>;
};

export async function createDiagnosis(
  payload: CreateDiagnosisPayload,
): Promise<DiagnosisRunResponse> {
  return apiFetch<DiagnosisRunResponse>("/diagnosis", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export { backendUrl };
