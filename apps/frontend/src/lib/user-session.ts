/** User session + JWT access token (ADR-003 / CAR-57). */

import { hasEmailProvider } from "@/lib/jwt";
import { readString, writeString } from "@/lib/session/storage";

const USER_ID_KEY = "career-forge.user-id";
const ACCESS_TOKEN_KEY = "career-forge.access-token";

function sameOriginApiBase(): string {
  return (process.env.NEXT_PUBLIC_BASE_PATH ?? "").replace(/\/$/, "");
}

function resolveBackendUrl(): string {
  const fromEnv =
    process.env.NEXT_PUBLIC_BACKEND_URL?.trim() ||
    process.env.NEXT_PUBLIC_API_URL?.trim();
  if (fromEnv) return fromEnv.replace(/\/$/, "");
  return sameOriginApiBase();
}

/**
 * Returns the persisted anonymous user id. Client-only — throws during SSR so
 * server code cannot silently fall back to the demo seed user.
 */
export function getUserId(): string {
  if (typeof window === "undefined") {
    throw new Error("getUserId() is client-only and cannot run during SSR");
  }
  const stored = readString(USER_ID_KEY, "local");
  if (stored) return stored;
  const generated = `user-${crypto.randomUUID().slice(0, 8)}`;
  writeString(USER_ID_KEY, generated, "local");
  return generated;
}

export function getAccessToken(): string | null {
  if (typeof window === "undefined") return null;
  return readString(ACCESS_TOKEN_KEY, "local");
}

function setAccessToken(token: string, externalId: string): void {
  writeString(ACCESS_TOKEN_KEY, token, "local");
  writeString(USER_ID_KEY, externalId, "local");
}

/** Adopt an owner session from a resume deep-link (CAR-27). Overwrites local JWT. */
export function adoptSession(accessToken: string, externalId: string): void {
  if (typeof window === "undefined") {
    throw new Error("adoptSession() is client-only");
  }
  setAccessToken(accessToken, externalId);
}

/** Store email JWT after OTP verify (CAR-57). */
export function setSessionFromOtp(accessToken: string, externalId: string): void {
  adoptSession(accessToken, externalId);
}

export function hasEmailIdentity(): boolean {
  return hasEmailProvider(getAccessToken());
}

let migrationMintInFlight: Promise<string> | null = null;

/**
 * Migration-only: mint anon JWT for OTP promote when a legacy session has no token.
 * Happy path uses OTP verify with ``external_id`` — never calls anon mint (CAR-57).
 */
export async function ensureMigrationAccessToken(): Promise<string> {
  if (typeof window === "undefined") {
    throw new Error("ensureMigrationAccessToken() is client-only");
  }
  const existing = getAccessToken();
  if (existing) return existing;
  if (migrationMintInFlight) return migrationMintInFlight;

  migrationMintInFlight = (async () => {
    const externalId = getUserId();
    const backendUrl = resolveBackendUrl();
    const res = await fetch(`${backendUrl}/auth/anon/mint`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ external_id: externalId }),
    });
    if (!res.ok) {
      const detail = await res.text().catch(() => res.statusText);
      throw new Error(`Failed to mint migration token: ${res.status} ${detail}`);
    }
    const data = (await res.json()) as {
      access_token: string;
      external_id: string;
    };
    setAccessToken(data.access_token, data.external_id);
    return data.access_token;
  })();

  try {
    return await migrationMintInFlight;
  } finally {
    migrationMintInFlight = null;
  }
}

/**
 * Return Bearer JWT for authenticated API calls. Requires email identity on the
 * product loop — complete the identity gate first (CAR-57).
 */
export async function ensureAccessToken(): Promise<string> {
  if (typeof window === "undefined") {
    throw new Error("ensureAccessToken() is client-only");
  }
  const existing = getAccessToken();
  if (existing && hasEmailProvider(existing)) return existing;
  throw new Error("Email identity required — complete the sign-in gate first.");
}
