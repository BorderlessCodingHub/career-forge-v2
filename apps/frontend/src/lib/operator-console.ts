export type OperatorDeskId = "access" | "content";

export type OperatorDesk = {
  id: OperatorDeskId;
  label: "Access" | "Content";
};

export type OperatorMe = {
  email: string;
  operator_id: number;
  desk_roles: "access" | "editor" | "both";
  desks: OperatorDeskId[];
};

export type OperatorSeat = {
  email: string;
};

export type OperatorCostPool = {
  year_month: string;
  estimated_cost_brl: number;
  budget_brl: number;
  billable_runs: number;
  forge_runs: number;
};

export type OperatorLearnerAccess = {
  email: string;
  operator_membership_label: "base" | "psp" | null;
  membership_label: string;
  membership_entitled: boolean;
  billing_entitled: boolean;
  stripe_subscription_status: string | null;
  stripe_billing_locked: boolean;
};

export type OperatorAccessPatch = {
  operator_membership_label?: "base" | "psp" | null;
  billing_entitled?: boolean;
};

export type OperatorAccessAuditEntry = {
  id: number;
  actor_type: string;
  operator_id: number | null;
  actor_email: string | null;
  learner_email: string;
  field: string;
  before: unknown;
  after: unknown;
  action: string;
  created_at: string;
};

const OPERATOR_DESKS: readonly OperatorDesk[] = [
  { id: "access", label: "Access" },
  { id: "content", label: "Content" },
];

function apiBase(): string {
  // Operator auth is deliberately same-origin: its HttpOnly cookie is scoped to
  // /career-forge/operator and Next rewrites /operator/* to the backend.
  return (process.env.NEXT_PUBLIC_BASE_PATH ?? "").replace(/\/$/, "");
}

export function operatorApiUrl(path: string): string {
  return `${apiBase()}${path}`;
}

async function operatorFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(operatorApiUrl(path), {
    ...init,
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
      ...init?.headers,
    },
  });
  if (!response.ok) {
    let message = response.status === 401 ? "Operator session required." : "Operator request failed.";
    try {
      const body = (await response.json()) as { detail?: string | { message?: string } };
      if (typeof body.detail === "string") message = body.detail;
      if (body.detail && typeof body.detail === "object" && body.detail.message) {
        message = body.detail.message;
      }
    } catch {
      // Keep the status-derived message.
    }
    throw new OperatorApiError(response.status, message);
  }
  if (response.status === 204) return undefined as T;
  return response.json() as Promise<T>;
}

export class OperatorApiError extends Error {
  constructor(
    readonly status: number,
    message: string,
  ) {
    super(message);
    this.name = "OperatorApiError";
  }
}

export function visibleOperatorDesks(grants: readonly OperatorDeskId[]): OperatorDesk[] {
  const held = new Set(grants);
  return OPERATOR_DESKS.filter((desk) => held.has(desk.id));
}

export function getOperatorMe(): Promise<OperatorMe> {
  return operatorFetch<OperatorMe>("/operator/me");
}

export async function getOperatorSeats(): Promise<OperatorSeat[]> {
  const body = await operatorFetch<{ seats: OperatorSeat[] }>("/operator/seats");
  return body.seats;
}

export function requestOperatorOtp(email: string): Promise<{ expires_in: number }> {
  return operatorFetch("/operator/auth/otp/request", {
    method: "POST",
    body: JSON.stringify({ email }),
  });
}

export function verifyOperatorOtp(email: string, code: string): Promise<OperatorMe> {
  return operatorFetch<OperatorMe>("/operator/auth/otp/verify", {
    method: "POST",
    body: JSON.stringify({ email, code }),
  });
}

export function signOutOperator(): Promise<void> {
  return operatorFetch<void>("/operator/auth/sign-out", { method: "POST" });
}

export function getOperatorCostPool(): Promise<OperatorCostPool> {
  return operatorFetch<OperatorCostPool>("/operator/access/cost-pool");
}

function learnerAccessPath(email: string): string {
  return `/operator/access/learners/${encodeURIComponent(email.trim().toLowerCase())}`;
}

export function getOperatorLearnerAccess(email: string): Promise<OperatorLearnerAccess> {
  return operatorFetch<OperatorLearnerAccess>(learnerAccessPath(email));
}

export function patchOperatorLearnerAccess(
  email: string,
  patch: OperatorAccessPatch,
): Promise<OperatorLearnerAccess> {
  return operatorFetch<OperatorLearnerAccess>(learnerAccessPath(email), {
    method: "PATCH",
    body: JSON.stringify(patch),
  });
}

export async function getOperatorLearnerAccessAudit(
  email: string,
): Promise<OperatorAccessAuditEntry[]> {
  const body = await operatorFetch<{ entries: OperatorAccessAuditEntry[] }>(
    `${learnerAccessPath(email)}/audit`,
  );
  return body.entries;
}
