import type {
  DiagnosisResponse,
  MentorContextSnapshot,
  MentorMessage,
  MentorRunResponse,
  RoadmapResponse,
  RoadmapSyncNode,
  ValidationQuestionsResponse,
  ValidationRunResponse,
} from "@/types/contracts";
import { getUserId } from "@/lib/user-session";

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
    body: JSON.stringify({ user_id: getUserId(), ...payload }),
  });
}

export type ForgeRunResponse = {
  run_id: string;
  status: string;
  events: Array<Record<string, unknown>>;
  output: Record<string, unknown> | null;
};

export async function startForgeRun(
  diagnosis: DiagnosisResponse,
  userId?: string,
): Promise<ForgeRunResponse> {
  const resolvedUserId = userId ?? getUserId();
  return apiFetch<ForgeRunResponse>("/forge", {
    method: "POST",
    body: JSON.stringify({ user_id: resolvedUserId, diagnosis }),
  });
}

export function forgeStreamUrl(runId: string): string {
  return `${backendUrl}/forge/${runId}/stream`;
}

export async function getRoadmap(userId?: string): Promise<RoadmapResponse> {
  const resolvedUserId = userId ?? getUserId();
  return apiFetch<RoadmapResponse>(
    `/roadmap/?user_id=${encodeURIComponent(resolvedUserId)}`,
  );
}

export async function syncRoadmap(
  nodes: RoadmapSyncNode[],
  userId?: string,
): Promise<RoadmapResponse> {
  const resolvedUserId = userId ?? getUserId();
  return apiFetch<RoadmapResponse>("/roadmap/sync", {
    method: "POST",
    body: JSON.stringify({ user_id: resolvedUserId, nodes }),
  });
}

export async function getValidationQuestions(
  nodeId: string,
): Promise<ValidationQuestionsResponse> {
  return apiFetch<ValidationQuestionsResponse>(
    `/validation/questions?node_id=${encodeURIComponent(nodeId)}`,
  );
}

export type SubmitValidationPayload = {
  user_id?: string;
  node_id: string;
  node_title: string;
  rubric: string[];
  answers: Array<{ question_id: string; answer: string }>;
};

export async function submitValidation(
  payload: SubmitValidationPayload,
  userId?: string,
): Promise<ValidationRunResponse> {
  const resolvedUserId = userId ?? getUserId();
  return apiFetch<ValidationRunResponse>("/validation", {
    method: "POST",
    body: JSON.stringify({ user_id: resolvedUserId, ...payload }),
  });
}

export type DemoValidationSummary = {
  node_id: string;
  score: number;
  passed: boolean;
  feedback?: string | null;
};

export type DemoAnaResponse = {
  user_id: string;
  display_name: string;
  diagnosis: DiagnosisResponse;
  roadmap: RoadmapResponse;
  validations: DemoValidationSummary[];
  pitch_node_id: string;
};

export async function getDemoAna(): Promise<DemoAnaResponse> {
  return apiFetch<DemoAnaResponse>("/demo/ana");
}

export type SendMentorMessagePayload = {
  user_id?: string;
  message: string;
  node_id?: string | null;
  node_title?: string | null;
  history?: MentorMessage[];
};

export async function getMentorContext(
  nodeId?: string | null,
  userId?: string,
): Promise<MentorContextSnapshot> {
  const resolvedUserId = userId ?? getUserId();
  const params = new URLSearchParams({ user_id: resolvedUserId });
  if (nodeId) params.set("node_id", nodeId);
  return apiFetch<MentorContextSnapshot>(`/mentor/context?${params.toString()}`);
}

export async function sendMentorMessage(
  payload: SendMentorMessagePayload,
  userId?: string,
): Promise<MentorRunResponse> {
  const resolvedUserId = userId ?? getUserId();
  return apiFetch<MentorRunResponse>("/mentor", {
    method: "POST",
    body: JSON.stringify({ user_id: resolvedUserId, ...payload }),
  });
}

export async function* streamForgeEvents(
  runId: string,
): AsyncGenerator<Record<string, unknown>> {
  const res = await fetch(forgeStreamUrl(runId), {
    headers: { Accept: "text/event-stream" },
  });
  if (!res.ok || !res.body) {
    throw new Error(`Forge stream failed: ${res.status}`);
  }

  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });
    const parts = buffer.split("\n\n");
    buffer = parts.pop() ?? "";
    for (const part of parts) {
      const line = part
        .split("\n")
        .find((row) => row.startsWith("data:"));
      if (!line) continue;
      const json = line.replace(/^data:\s*/, "");
      try {
        yield JSON.parse(json) as Record<string, unknown>;
      } catch {
        /* skip malformed chunk */
      }
    }
  }
}

export { backendUrl };
