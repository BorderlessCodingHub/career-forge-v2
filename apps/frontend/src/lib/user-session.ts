/** Single anonymous user session — no demo toggle in product UI. */

import { readString, writeString } from "@/lib/session/storage";

const USER_ID_KEY = "career-forge.user-id";

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
