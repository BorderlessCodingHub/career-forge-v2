import type {
  DemoAnaResponse,
  DiagnosisIntake,
  DiagnosisRequest,
  DiagnosisResponse,
  DiagnosisRunResponse,
  ForgeRunResponse,
  InterviewTurnRequest,
  InterviewTurnResponse,
  MentorContextSnapshot,
  MentorReportResponse,
  MentorRequest,
  MentorRunResponse,
  MockInterviewQuestionsResponse,
  MockInterviewRequest,
  MockInterviewRunResponse,
  RoadmapResponse,
  RoadmapSyncNode,
  ValidationQuestionsResponse,
  ValidationRequest,
  ValidationRunResponse,
} from "@/types/contracts";
import { getUserId } from "@/lib/user-session";

const backendUrl =
  process.env.NEXT_PUBLIC_BACKEND_URL ??
  process.env.NEXT_PUBLIC_API_URL ??
  "http://localhost:8000";

async function readApiErrorMessage(res: Response): Promise<string> {
  try {
    const body = (await res.json()) as { detail?: unknown };
    const detail = body.detail;
    if (typeof detail === "string") return detail;
    if (
      detail &&
      typeof detail === "object" &&
      "message" in detail &&
      typeof detail.message === "string"
    ) {
      return detail.message;
    }
  } catch {
    // ignore JSON parse errors
  }
  return `${res.status} ${res.statusText}`;
}

export async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  let res: Response;
  try {
    res = await fetch(`${backendUrl}${path}`, {
      ...init,
      headers: { "Content-Type": "application/json", ...init?.headers },
    });
  } catch (cause) {
    const origin =
      typeof window !== "undefined" ? window.location.origin : null;
    const corsHint = origin
      ? ` Ensure backend CORS_ORIGINS includes ${origin} (see .env.example).`
      : "";
    const message =
      cause instanceof Error ? cause.message : "Network request failed";
    throw new Error(
      `Cannot reach API ${backendUrl}${path}: ${message}.${corsHint}`,
    );
  }
  if (!res.ok) {
    const message = await readApiErrorMessage(res);
    throw new Error(`API ${path} failed: ${message}`);
  }
  return res.json() as Promise<T>;
}

export async function createDiagnosis(
  payload: DiagnosisRequest,
): Promise<DiagnosisRunResponse> {
  return apiFetch<DiagnosisRunResponse>("/diagnosis", {
    method: "POST",
    body: JSON.stringify({ user_id: getUserId(), ...payload }),
  });
}

export async function startDiagnosisInterview(
  payload: DiagnosisIntake,
): Promise<InterviewTurnResponse> {
  return apiFetch<InterviewTurnResponse>("/diagnosis/interview/start", {
    method: "POST",
    body: JSON.stringify({ user_id: getUserId(), ...payload }),
  });
}

export async function submitDiagnosisTurn(
  sessionId: string,
  payload: InterviewTurnRequest,
): Promise<InterviewTurnResponse> {
  return apiFetch<InterviewTurnResponse>(
    `/diagnosis/interview/${encodeURIComponent(sessionId)}/turn`,
    {
      method: "POST",
      body: JSON.stringify(payload),
    },
  );
}

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

export async function submitValidation(
  payload: ValidationRequest,
  userId?: string,
): Promise<ValidationRunResponse> {
  const resolvedUserId = userId ?? getUserId();
  return apiFetch<ValidationRunResponse>("/validation", {
    method: "POST",
    body: JSON.stringify({ user_id: resolvedUserId, ...payload }),
  });
}

export async function getMockInterviewQuestions(
  nodeId: string,
): Promise<MockInterviewQuestionsResponse> {
  return apiFetch<MockInterviewQuestionsResponse>(
    `/mock-interview/questions?node_id=${encodeURIComponent(nodeId)}`,
  );
}

export async function submitMockInterview(
  payload: MockInterviewRequest,
  userId?: string,
): Promise<MockInterviewRunResponse> {
  const resolvedUserId = userId ?? getUserId();
  return apiFetch<MockInterviewRunResponse>("/mock-interview", {
    method: "POST",
    body: JSON.stringify({ user_id: resolvedUserId, ...payload }),
  });
}

export async function getDemoAna(): Promise<DemoAnaResponse> {
  return apiFetch<DemoAnaResponse>("/demo/ana");
}

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
  payload: MentorRequest,
  userId?: string,
): Promise<MentorRunResponse> {
  const resolvedUserId = userId ?? getUserId();
  return apiFetch<MentorRunResponse>("/mentor", {
    method: "POST",
    body: JSON.stringify({ user_id: resolvedUserId, ...payload }),
  });
}

export async function getMentorReport(userId?: string): Promise<MentorReportResponse> {
  const resolvedUserId = userId ?? getUserId();
  return apiFetch<MentorReportResponse>(
    `/mentor-report?user_id=${encodeURIComponent(resolvedUserId)}`,
  );
}

export { backendUrl };
