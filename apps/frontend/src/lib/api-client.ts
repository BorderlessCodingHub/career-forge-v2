import type {
  DemoAnaResponse,
  DiagnosisRequest,
  DiagnosisResponse,
  DiagnosisRunResponse,
  ForgeRunResponse,
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

export async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${backendUrl}${path}`, {
    ...init,
    headers: { "Content-Type": "application/json", ...init?.headers },
  });
  if (!res.ok) throw new Error(`API ${path} failed: ${res.status}`);
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
