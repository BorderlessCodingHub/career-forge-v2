/** Decode JWT payload client-side (no signature verify — UI hints only). */

type JwtPayload = {
  provider?: unknown;
  exp?: unknown;
};

function readJwtPayload(token: string | null): JwtPayload | null {
  if (!token) return null;
  try {
    const part = token.split(".")[1];
    if (!part) return null;
    const b64 = part.replace(/-/g, "+").replace(/_/g, "/");
    const padded = b64 + "=".repeat((4 - (b64.length % 4)) % 4);
    const json = atob(padded);
    return JSON.parse(json) as JwtPayload;
  } catch {
    return null;
  }
}

export function readJwtProvider(token: string | null): string | null {
  const provider = readJwtPayload(token)?.provider;
  return typeof provider === "string" ? provider : null;
}

function isUnexpired(exp: unknown, nowSec = Date.now() / 1000): boolean {
  return typeof exp === "number" && Number.isFinite(exp) && exp > nowSec;
}

/** Email identity usable for the product gate — provider=email and unexpired. */
export function hasEmailProvider(token: string | null): boolean {
  const payload = readJwtPayload(token);
  if (!payload || payload.provider !== "email") return false;
  return isUnexpired(payload.exp);
}
