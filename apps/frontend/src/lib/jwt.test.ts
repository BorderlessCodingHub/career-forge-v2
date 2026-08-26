import { describe, expect, it } from "vitest";

import { hasEmailProvider } from "./jwt";

function unsignedJwt(payload: Record<string, unknown>): string {
  const body = btoa(JSON.stringify(payload));
  return `eyJhbGciOiJub25lIn0.${body}.sig`;
}

describe("hasEmailProvider", () => {
  it("is true for an unexpired email JWT", () => {
    const token = unsignedJwt({
      provider: "email",
      exp: Math.floor(Date.now() / 1000) + 3600,
    });
    expect(hasEmailProvider(token)).toBe(true);
  });

  it("is false for an expired email JWT", () => {
    const token = unsignedJwt({
      provider: "email",
      exp: Math.floor(Date.now() / 1000) - 10,
    });
    expect(hasEmailProvider(token)).toBe(false);
  });

  it("is false for a malformed token", () => {
    expect(hasEmailProvider("not-a-jwt")).toBe(false);
  });

  it("is false when provider is email but exp is missing", () => {
    expect(hasEmailProvider(unsignedJwt({ provider: "email" }))).toBe(false);
  });
});
