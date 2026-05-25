/** Demo vs new-user session — HAC-12 */

export type UserMode = "demo" | "new";

const MODE_KEY = "career-forge.user-mode";
const USER_ID_KEY = "career-forge.user-id";

export const DEMO_USER_ID =
  process.env.NEXT_PUBLIC_DEMO_USER_ID?.trim() || "demo-ana";

function readMode(): UserMode | null {
  if (typeof window === "undefined") return null;
  const raw = window.localStorage.getItem(MODE_KEY);
  return raw === "demo" || raw === "new" ? raw : null;
}

export function getUserMode(): UserMode {
  return readMode() ?? "demo";
}

export function isDemoMode(): boolean {
  return getUserMode() === "demo";
}

export function getUserId(): string {
  if (typeof window === "undefined") return DEMO_USER_ID;
  const mode = getUserMode();
  if (mode === "demo") return DEMO_USER_ID;
  const stored = window.localStorage.getItem(USER_ID_KEY);
  if (stored) return stored;
  const generated = `user-${crypto.randomUUID().slice(0, 8)}`;
  window.localStorage.setItem(USER_ID_KEY, generated);
  return generated;
}

export function setDemoMode(): void {
  if (typeof window === "undefined") return;
  window.localStorage.setItem(MODE_KEY, "demo");
  window.localStorage.removeItem(USER_ID_KEY);
}

export function setNewUserMode(): string {
  if (typeof window === "undefined") return DEMO_USER_ID;
  const userId = `user-${crypto.randomUUID().slice(0, 8)}`;
  window.localStorage.setItem(MODE_KEY, "new");
  window.localStorage.setItem(USER_ID_KEY, userId);
  return userId;
}

export function clearUserSession(): void {
  if (typeof window === "undefined") return;
  window.localStorage.removeItem(MODE_KEY);
  window.localStorage.removeItem(USER_ID_KEY);
}
