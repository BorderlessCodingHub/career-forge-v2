import type {
  CvAttachment,
  DemoAnaResponse,
  DiagnosisConfirmResponse,
  DiagnosisIntake,
  DiagnosisRequest,
  DiagnosisResponse,
  DiagnosisRunResponse,
  DiagnosisStreamEvent,
  ForgeRunResponse,
  InterviewTurnRequest,
  InterviewTurnResponse,
  KnowledgeGapItem,
  MentorContextSnapshot,
  MentorReportResponse,
  MentorRequest,
  MentorRunResponse,
  MockInterviewQuestionsResponse,
  MockInterviewRequest,
  MockInterviewRunResponse,
  TutorContext,
  TutorRequest,
  TutorRunResponse,
  ChecklistToggleRequest,
  RoadmapResponse,
  RoadmapForgeEvent,
  RoadmapSyncNode,
  ValidationQuestionsResponse,
  ValidationRequest,
  ValidationRunResponse,
} from "@/types/contracts";
import { consumeFetchEventStream } from "@/lib/sse/consume";
import { toInterviewCv } from "@/lib/diagnosis-interview";
import {
  applyForgeStreamEvent,
  createInitialForgeStreamState,
  parseForgeStreamEvent,
  type ForgeStreamSideEffects,
} from "@/lib/forge-stream";
import { getUserId } from "@/lib/user-session";

/** Public API base, or "" for same-origin (Next rewrites → API_INTERNAL_URL on the server). */
function resolveBackendUrl(): string {
  const fromEnv =
    process.env.NEXT_PUBLIC_BACKEND_URL?.trim() ||
    process.env.NEXT_PUBLIC_API_URL?.trim();
  if (fromEnv) return fromEnv.replace(/\/$/, "");
  return "";
}

const backendUrl = resolveBackendUrl();

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

function parseDiagnosisStreamEvent(raw: Record<string, unknown>): DiagnosisStreamEvent | null {
  if (typeof raw.type !== "string") return null;
  return raw as DiagnosisStreamEvent;
}

function graphOutputToTurnResponse(
  output: InterviewTurnResponse & { session?: unknown },
): InterviewTurnResponse {
  return {
    session_id: output.session_id,
    status: output.status,
    round_count: output.round_count ?? 0,
    questions: output.questions ?? [],
    mapping_progress: output.mapping_progress ?? [],
    diagnosis: output.diagnosis,
  };
}

export async function getDiagnosisInterviewSession(
  sessionId: string,
): Promise<InterviewTurnResponse> {
  return apiFetch<InterviewTurnResponse>(
    `/diagnosis/interview/${encodeURIComponent(sessionId)}`,
  );
}

async function consumeDiagnosisInterviewStream(
  path: string,
  body: unknown,
  onEvent?: (event: DiagnosisStreamEvent) => void,
): Promise<InterviewTurnResponse> {
  let finalResponse: InterviewTurnResponse | null = null;
  let streamError: Error | null = null;

  try {
    await consumeFetchEventStream<DiagnosisStreamEvent>(
      `${backendUrl}${path}`,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      },
      (_eventName, payload) => {
        onEvent?.(payload);
        if (payload.type === "error") {
          streamError = new Error(payload.message);
          return;
        }
        if (payload.type === "graph_complete") {
          finalResponse = graphOutputToTurnResponse(payload.output);
        }
      },
      (raw) => parseDiagnosisStreamEvent(raw as Record<string, unknown>),
    );
  } catch (cause) {
    const message =
      cause instanceof Error ? cause.message : "Network request failed";
    throw new Error(`Cannot reach API ${backendUrl}${path}: ${message}.`);
  }

  if (streamError) throw streamError;
  if (!finalResponse) {
    throw new Error("Stream terminou sem resposta final do diagnóstico.");
  }
  return finalResponse;
}

export async function streamDiagnosisInterviewStart(
  payload: DiagnosisIntake,
  onEvent?: (event: DiagnosisStreamEvent) => void,
): Promise<InterviewTurnResponse> {
  return consumeDiagnosisInterviewStream(
    "/diagnosis/interview/start/stream",
    { user_id: getUserId(), ...payload },
    onEvent,
  );
}

export async function streamDiagnosisInterviewTurn(
  sessionId: string,
  payload: InterviewTurnRequest,
  onEvent?: (event: DiagnosisStreamEvent) => void,
): Promise<InterviewTurnResponse> {
  return consumeDiagnosisInterviewStream(
    `/diagnosis/interview/${encodeURIComponent(sessionId)}/turn/stream`,
    payload,
    onEvent,
  );
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

export async function confirmDiagnosis(payload: {
  diagnosis: DiagnosisResponse;
  goal_id: string;
  motivation: string;
  years_xp?: DiagnosisIntake["years_xp"];
  cv?: CvAttachment | null;
  answers?: Record<string, string>;
}): Promise<DiagnosisConfirmResponse> {
  const cv = payload.cv ? toInterviewCv(payload.cv) : undefined;
  return apiFetch<DiagnosisConfirmResponse>("/diagnosis/confirm", {
    method: "POST",
    body: JSON.stringify({
      user_id: getUserId(),
      diagnosis: payload.diagnosis,
      goal_id: payload.goal_id,
      motivation: payload.motivation,
      years_xp: payload.years_xp,
      answers: payload.answers,
      cv,
    }),
  });
}

/** HAC-52/57 — enqueue forge from persisted profile (no inline diagnosis). */
export async function startForgeRunFromProfile(
  userId?: string,
): Promise<ForgeRunResponse> {
  const resolvedUserId = userId ?? getUserId();
  return apiFetch<ForgeRunResponse>("/forge", {
    method: "POST",
    body: JSON.stringify({ user_id: resolvedUserId }),
  });
}

/** Legacy inline-diagnosis forge start (demo / tests). */
export async function startForgeRun(
  diagnosis: DiagnosisResponse,
  userId?: string,
  input?: {
    goal_id?: string | null;
    motivation?: string;
    years_xp?: DiagnosisIntake["years_xp"] | null;
    answers?: Record<string, string>;
  },
): Promise<ForgeRunResponse> {
  const resolvedUserId = userId ?? getUserId();
  return apiFetch<ForgeRunResponse>("/forge", {
    method: "POST",
    body: JSON.stringify({ user_id: resolvedUserId, diagnosis, input }),
  });
}

export function forgeStreamUrl(runId: string): string {
  return `${backendUrl}/forge/${runId}/stream`;
}

export async function streamForgeRun(
  runId: string,
  effects: ForgeStreamSideEffects = {},
): Promise<RoadmapForgeEvent[]> {
  let state = createInitialForgeStreamState();
  let streamError: Error | null = null;

  await consumeFetchEventStream<RoadmapForgeEvent>(
    forgeStreamUrl(runId),
    { method: "GET" },
    (_eventName, payload) => {
      if (payload.type === "error") {
        streamError = new Error(payload.message);
        effects.onError?.(payload.message);
        return;
      }
      state = applyForgeStreamEvent(state, payload, effects);
    },
    parseForgeStreamEvent,
  );

  if (streamError) throw streamError;
  return state.events;
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

export async function patchRoadmapChecklist(
  nodeId: string,
  body: Omit<ChecklistToggleRequest, "user_id">,
  userId?: string,
): Promise<RoadmapResponse> {
  const resolvedUserId = userId ?? getUserId();
  return apiFetch<RoadmapResponse>(
    `/roadmap/nodes/${encodeURIComponent(nodeId)}/checklist`,
    {
      method: "PATCH",
      body: JSON.stringify({ user_id: resolvedUserId, ...body }),
    },
  );
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

export async function getKnowledgeGaps(
  nodeId: string,
  userId?: string,
): Promise<KnowledgeGapItem[]> {
  const resolvedUserId = userId ?? getUserId();
  const params = new URLSearchParams({ user_id: resolvedUserId, node_id: nodeId });
  return apiFetch<KnowledgeGapItem[]>(`/knowledge-gaps?${params.toString()}`);
}

export async function getMockInterviewQuestions(
  nodeId: string,
  userId?: string,
): Promise<MockInterviewQuestionsResponse> {
  const resolvedUserId = userId ?? getUserId();
  return apiFetch<MockInterviewQuestionsResponse>(
    `/mock-interview/questions?node_id=${encodeURIComponent(nodeId)}&user_id=${encodeURIComponent(resolvedUserId)}`,
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

export async function getTutorContext(
  nodeId?: string | null,
  nodeTitle?: string | null,
  userId?: string,
): Promise<TutorContext> {
  const resolvedUserId = userId ?? getUserId();
  const params = new URLSearchParams({ user_id: resolvedUserId });
  if (nodeId) params.set("node_id", nodeId);
  if (nodeTitle) params.set("node_title", nodeTitle);
  return apiFetch<TutorContext>(`/tutor/context?${params.toString()}`);
}

export async function sendTutorMessage(
  payload: TutorRequest,
  userId?: string,
): Promise<TutorRunResponse> {
  const resolvedUserId = userId ?? getUserId();
  return apiFetch<TutorRunResponse>("/tutor", {
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
