import type {
  CvAttachment,
  DiagnosisConfirmResponse,
  DiagnosisIntake,
  DiagnosisResponse,
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
  ForgeArtifactListResponse,
  ForgeArtifactSummary,
  ForgeLinkMintResponse,
  ForgeShareRevokeResponse,
  MeEmailUpdateResponse,
  MeProfileResponse,
  OtpEmailOwnedConflict,
  OtpRequestResponse,
  OtpVerifyResponse,
  ResumeConsumeResponse,
  ResumeEmailResponse,
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
import {
  clearAccessToken,
  ensureAccessToken,
  getAccessToken,
  getUserId,
  setSessionFromOtp,
} from "@/lib/user-session";
import {
  QUOTA_EXHAUSTED_COPY,
  isQuotaExhaustedMessage,
  toUserFacingApiError,
} from "@/lib/quota";
import { paywallErrorFromResponse } from "@/lib/paywall";

export { QUOTA_EXHAUSTED_COPY, isQuotaExhaustedMessage };

/** Next basePath for same-origin API calls (see next.config.mjs). */
function sameOriginApiBase(): string {
  return (process.env.NEXT_PUBLIC_BASE_PATH ?? "").replace(/\/$/, "");
}

/** Public API base, or basePath for same-origin (Next rewrites → API_INTERNAL_URL). */
function resolveBackendUrl(): string {
  const fromEnv =
    process.env.NEXT_PUBLIC_BACKEND_URL?.trim() ||
    process.env.NEXT_PUBLIC_API_URL?.trim();
  if (fromEnv) return fromEnv.replace(/\/$/, "");
  // Empty NEXT_PUBLIC_* → browser hits /career-forge/diagnosis/... (rewritten server-side).
  return sameOriginApiBase();
}

const backendUrl = resolveBackendUrl();

async function readApiError(res: Response): Promise<Error> {
  let body: { detail?: unknown } = {};
  try {
    body = (await res.json()) as { detail?: unknown };
  } catch {
    // ignore JSON parse errors
  }
  const paywall = paywallErrorFromResponse(res.status, body);
  if (paywall) return paywall;
  const detail = body.detail;
  let message = `${res.status} ${res.statusText}`;
  if (typeof detail === "string") {
    message = detail;
  } else if (
    detail &&
    typeof detail === "object" &&
    "message" in detail &&
    typeof detail.message === "string"
  ) {
    message = detail.message;
  }
  return new Error(toUserFacingApiError(res.status, message));
}

async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const token = await ensureAccessToken();
  let res: Response;
  try {
    res = await fetch(`${backendUrl}${path}`, {
      ...init,
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
        ...init?.headers,
      },
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
    throw await readApiError(res);
  }
  return res.json() as Promise<T>;
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
  const token = await ensureAccessToken();

  try {
    await consumeFetchEventStream<DiagnosisStreamEvent>(
      `${backendUrl}${path}`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
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
    throw new Error("Stream ended without a final diagnosis response.");
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
  return apiFetch<ForgeRunResponse>("/forge/runs", {
    method: "POST",
    body: JSON.stringify({ user_id: resolvedUserId }),
  });
}

type ForgeStreamTicketResponse = {
  ticket: string;
  expires_in: number;
};

function forgeStreamUrl(runId: string, ticket: string): string {
  const params = new URLSearchParams({ ticket });
  return `${backendUrl}/forge/${runId}/stream?${params.toString()}`;
}

/** CAR-26 — Bearer mint → short-lived ticket for SSE (EventSource-compatible). */
async function mintForgeStreamTicket(
  runId: string,
): Promise<ForgeStreamTicketResponse> {
  return apiFetch<ForgeStreamTicketResponse>(
    `/forge/${runId}/stream-ticket`,
    { method: "POST" },
  );
}

export async function streamForgeRun(
  runId: string,
  effects: ForgeStreamSideEffects = {},
): Promise<RoadmapForgeEvent[]> {
  let state = createInitialForgeStreamState();
  let streamError: Error | null = null;

  const { ticket } = await mintForgeStreamTicket(runId);

  await consumeFetchEventStream<RoadmapForgeEvent>(
    forgeStreamUrl(runId, ticket),
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
  // /roadmap/current avoids App Router page collision on Labs (CAR-30 / CAR-20 pattern).
  return apiFetch<RoadmapResponse>(
    `/roadmap/current?user_id=${encodeURIComponent(resolvedUserId)}`,
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

/** CAR-27 — list historical forge artifacts for the Bearer principal. */
export async function listForges(): Promise<ForgeArtifactListResponse> {
  return apiFetch<ForgeArtifactListResponse>("/me/forges");
}

/** CAR-27 — freeze-before-promote and return live roadmap. */
export async function openForge(publicId: string): Promise<RoadmapResponse> {
  return apiFetch<RoadmapResponse>(`/me/forges/${encodeURIComponent(publicId)}/open`, {
    method: "POST",
  });
}

export async function mintShareLink(publicId: string): Promise<ForgeLinkMintResponse> {
  return apiFetch<ForgeLinkMintResponse>(
    `/me/forges/${encodeURIComponent(publicId)}/share`,
    { method: "POST" },
  );
}

export async function mintResumeLink(publicId: string): Promise<ForgeLinkMintResponse> {
  return apiFetch<ForgeLinkMintResponse>(
    `/me/forges/${encodeURIComponent(publicId)}/resume`,
    { method: "POST" },
  );
}

export async function emailResumeLink(
  publicId: string,
): Promise<ResumeEmailResponse> {
  return apiFetch<ResumeEmailResponse>(
    `/me/forges/${encodeURIComponent(publicId)}/resume/email`,
    { method: "POST" },
  );
}

export async function revokeShareLink(
  publicId: string,
): Promise<ForgeShareRevokeResponse> {
  return apiFetch<ForgeShareRevokeResponse>(
    `/me/forges/${encodeURIComponent(publicId)}/share/revoke`,
    { method: "POST" },
  );
}

export async function updateForgeTitle(
  publicId: string,
  title: string,
): Promise<ForgeArtifactSummary> {
  return apiFetch<ForgeArtifactSummary>(
    `/me/forges/${encodeURIComponent(publicId)}`,
    {
      method: "PATCH",
      body: JSON.stringify({ title }),
    },
  );
}

export async function getMyProfile(): Promise<MeProfileResponse> {
  return apiFetch<MeProfileResponse>("/me/profile");
}

export async function startBillingCheckout(): Promise<string> {
  const body = await apiFetch<{ checkout_url: string }>("/billing/checkout", {
    method: "POST",
  });
  return body.checkout_url;
}

export async function syncBillingSession(
  sessionId: string,
): Promise<{ billing_entitled: boolean }> {
  return apiFetch<{ billing_entitled: boolean }>("/billing/sync", {
    method: "POST",
    body: JSON.stringify({ session_id: sessionId }),
  });
}

export async function updateMyEmail(email: string): Promise<MeEmailUpdateResponse> {
  return apiFetch<MeEmailUpdateResponse>("/me/email", {
    method: "PATCH",
    body: JSON.stringify({ email }),
  });
}

/** Public OTP request — code delivered via mailer (dev: backend logs). */
export async function requestOtp(email: string): Promise<OtpRequestResponse> {
  const res = await fetch(`${backendUrl}/auth/otp/request`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email }),
  });
  if (!res.ok) {
    throw await readApiError(res);
  }
  return res.json() as Promise<OtpRequestResponse>;
}

export class OtpEmailOwnedError extends Error {
  readonly conflict: OtpEmailOwnedConflict;

  constructor(conflict: OtpEmailOwnedConflict) {
    super(conflict.message);
    this.name = "OtpEmailOwnedError";
    this.conflict = conflict;
  }
}

/** Verify OTP — promote anon or mint email JWT via external_id (CAR-57). */
export async function verifyOtp(
  email: string,
  code: string,
): Promise<OtpVerifyResponse> {
  const token = getAccessToken();
  const headers: Record<string, string> = { "Content-Type": "application/json" };
  if (token) headers.Authorization = `Bearer ${token}`;
  const payload: { email: string; code: string; external_id?: string } = {
    email,
    code,
    external_id: getUserId(),
  };

  const res = await fetch(`${backendUrl}/auth/otp/verify`, {
    method: "POST",
    headers,
    body: JSON.stringify(payload),
  });
  if (res.status === 409) {
    try {
      const body = (await res.json()) as { detail?: unknown };
      const detail = body.detail;
      if (
        detail &&
        typeof detail === "object" &&
        "code" in detail &&
        (detail as OtpEmailOwnedConflict).code === "email_owned" &&
        "existing" in detail
      ) {
        throw new OtpEmailOwnedError(detail as OtpEmailOwnedConflict);
      }
    } catch (err) {
      if (err instanceof OtpEmailOwnedError) throw err;
    }
    throw new Error(toUserFacingApiError(409, "email already linked"));
  }
  if (res.status === 401) {
    clearAccessToken();
  }
  if (!res.ok) {
    throw await readApiError(res);
  }
  const data = (await res.json()) as OtpVerifyResponse;
  setSessionFromOtp(data.access_token, data.external_id);
  return data;
}

/** Public share fetch — no identity adoption (Bearer optional). */
export async function fetchSharedForge(token: string): Promise<RoadmapResponse> {
  const res = await fetch(
    `${backendUrl}/public/share/${encodeURIComponent(token)}`,
  );
  if (!res.ok) {
    throw await readApiError(res);
  }
  return res.json() as Promise<RoadmapResponse>;
}

/** Public resume consume — returns owner JWT for adoptSession. */
export async function consumeResumeLink(
  token: string,
): Promise<ResumeConsumeResponse> {
  const res = await fetch(
    `${backendUrl}/public/resume/${encodeURIComponent(token)}`,
    { method: "POST" },
  );
  if (!res.ok) {
    throw await readApiError(res);
  }
  return res.json() as Promise<ResumeConsumeResponse>;
}

/** Absolute app URL for copy-to-clipboard deep-links (respects basePath). */
export function absoluteAppUrl(path: string): string {
  if (typeof window === "undefined") return path;
  const base = (process.env.NEXT_PUBLIC_BASE_PATH ?? "").replace(/\/$/, "");
  const normalized = path.startsWith("/") ? path : `/${path}`;
  return `${window.location.origin}${base}${normalized}`;
}

