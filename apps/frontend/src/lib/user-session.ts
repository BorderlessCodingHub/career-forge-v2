/** Single anonymous user session — no demo toggle in product UI. */

const USER_ID_KEY = "career-forge.user-id";

/** Backend demo seed id — dev/API only, not used as default FE session. */
export const DEMO_USER_ID =
  process.env.NEXT_PUBLIC_DEMO_USER_ID?.trim() || "demo-ana";

/**
 * Returns the persisted anonymous user id. Client-only — throws during SSR so
 * server code cannot silently fall back to the demo seed user.
 */
export function getUserId(): string {
  if (typeof window === "undefined") {
    throw new Error("getUserId() is client-only and cannot run during SSR");
  }
  const stored = window.localStorage.getItem(USER_ID_KEY);
  if (stored) return stored;
  const generated = `user-${crypto.randomUUID().slice(0, 8)}`;
  window.localStorage.setItem(USER_ID_KEY, generated);
  return generated;
}

export function clearUserSession(): void {
  if (typeof window === "undefined") return;
  window.localStorage.removeItem(USER_ID_KEY);
}
