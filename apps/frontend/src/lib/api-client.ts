import type { DiagnosisResponse, RoadmapResponse, RoadmapSyncNode } from "@/types/contracts";

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

export type ForgeRunResponse = {
  run_id: string;
  status: string;
  events: Array<Record<string, unknown>>;
  output: Record<string, unknown> | null;
};

export async function startForgeRun(
  diagnosis: DiagnosisResponse,
  userId = "demo-ana",
): Promise<ForgeRunResponse> {
  return apiFetch<ForgeRunResponse>("/forge", {
    method: "POST",
    body: JSON.stringify({ user_id: userId, diagnosis }),
  });
}

export function forgeStreamUrl(runId: string): string {
  return `${backendUrl}/forge/${runId}/stream`;
}

export async function getRoadmap(userId = "demo-ana"): Promise<RoadmapResponse> {
  return apiFetch<RoadmapResponse>(`/roadmap/?user_id=${encodeURIComponent(userId)}`);
}

export async function syncRoadmap(
  nodes: RoadmapSyncNode[],
  userId = "demo-ana",
): Promise<RoadmapResponse> {
  return apiFetch<RoadmapResponse>("/roadmap/sync", {
    method: "POST",
    body: JSON.stringify({ user_id: userId, nodes }),
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
