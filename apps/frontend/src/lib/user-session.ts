/** Anonymous user session + JWT access token (ADR-003 / CAR-23). */

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

let mintInFlight: Promise<string> | null = null;

/**
 * Ensure a Bearer JWT exists, migrating ``career-forge.user-id`` on first mint.
 */
export async function ensureAccessToken(): Promise<string> {
  if (typeof window === "undefined") {
    throw new Error("ensureAccessToken() is client-only");
  }
  const existing = getAccessToken();
  if (existing) return existing;
  if (mintInFlight) return mintInFlight;

  mintInFlight = (async () => {
    const externalId = getUserId();
    const backendUrl = resolveBackendUrl();
    const res = await fetch(`${backendUrl}/auth/anon/mint`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ external_id: externalId }),
    });
    if (!res.ok) {
      const detail = await res.text().catch(() => res.statusText);
      throw new Error(`Failed to mint auth token: ${res.status} ${detail}`);
    }
    const data = (await res.json()) as {
      access_token: string;
      external_id: string;
    };
    setAccessToken(data.access_token, data.external_id);
    return data.access_token;
  })();

  try {
    return await mintInFlight;
  } finally {
    mintInFlight = null;
  }
}
