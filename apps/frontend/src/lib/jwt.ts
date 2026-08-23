/** Decode JWT payload client-side (no signature verify — UI hints only). */

export function readJwtProvider(token: string | null): string | null {
  if (!token) return null;
  try {
    const part = token.split(".")[1];
    if (!part) return null;
    const json = atob(part.replace(/-/g, "+").replace(/_/g, "/"));
    const payload = JSON.parse(json) as { provider?: unknown };
    return typeof payload.provider === "string" ? payload.provider : null;
  } catch {
    return null;
  }
}

export function hasEmailProvider(token: string | null): boolean {
  return readJwtProvider(token) === "email";
}
