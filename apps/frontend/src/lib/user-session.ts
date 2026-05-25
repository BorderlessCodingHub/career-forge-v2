/** Single anonymous user session — no demo toggle in product UI. */

import { readString, removeItem, writeString } from "@/lib/session/storage";

const USER_ID_KEY = "career-forge.user-id";

/** Backend demo seed id — dev/API only, not used as default FE session. */
export const DEMO_USER_ID =
  process.env.NEXT_PUBLIC_DEMO_USER_ID?.trim() || "demo-ana";

export function getUserId(): string {
  if (typeof window === "undefined") return DEMO_USER_ID;
  const stored = readString(USER_ID_KEY, "local");
  if (stored) return stored;
  const generated = `user-${crypto.randomUUID().slice(0, 8)}`;
  writeString(USER_ID_KEY, generated, "local");
  return generated;
}
