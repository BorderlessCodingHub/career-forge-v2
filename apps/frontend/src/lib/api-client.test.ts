import { beforeEach, describe, expect, it, vi } from "vitest";

function createMemoryStorage(): Storage {
  const map = new Map<string, string>();
  return {
    get length() {
      return map.size;
    },
    clear: () => map.clear(),
    getItem: (key) => map.get(key) ?? null,
    key: (index) => Array.from(map.keys())[index] ?? null,
    removeItem: (key) => map.delete(key),
    setItem: (key, value) => map.set(key, value),
  } as Storage;
}

describe("verifyOtp", () => {
  beforeEach(() => {
    vi.resetModules();
    const localStorage = createMemoryStorage();
    const sessionStorage = createMemoryStorage();
    vi.stubGlobal("window", { localStorage, sessionStorage });
    vi.stubGlobal("localStorage", localStorage);
    vi.stubGlobal("sessionStorage", sessionStorage);
  });

  it("sends external_id alongside a stored bearer token", async () => {
    localStorage.setItem("career-forge.access-token", "stale-token");
    localStorage.setItem("career-forge.user-id", "user-stale-device");
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: true,
        status: 200,
        json: async () => ({
          status: "promoted",
          access_token: "fresh-token",
          token_type: "bearer",
          external_id: "user-stale-device",
          provider: "email",
          email: "pilot@example.com",
        }),
      }),
    );

    const { verifyOtp } = await import("./api-client");
    await verifyOtp("pilot@example.com", "123456");

    expect(fetch).toHaveBeenCalledWith(
      expect.stringContaining("/auth/otp/verify"),
      expect.objectContaining({
        headers: {
          "Content-Type": "application/json",
          Authorization: "Bearer stale-token",
        },
        body: JSON.stringify({
          email: "pilot@example.com",
          code: "123456",
          external_id: "user-stale-device",
        }),
      }),
    );
  });

  it("clears a stored bearer token after a 401", async () => {
    localStorage.setItem("career-forge.access-token", "stale-token");
    localStorage.setItem("career-forge.user-id", "user-stale-device");
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: false,
        status: 401,
        statusText: "Unauthorized",
        json: async () => ({ detail: "Invalid token" }),
      }),
    );

    const { verifyOtp } = await import("./api-client");
    await expect(verifyOtp("pilot@example.com", "123456")).rejects.toThrow();

    expect(localStorage.getItem("career-forge.access-token")).toBeNull();
    expect(localStorage.getItem("career-forge.user-id")).toBe("user-stale-device");
  });

  it("loads the authenticated live Reference embed allowlist", async () => {
    const learnerToken = `header.${Buffer.from(
      JSON.stringify({ provider: "email", exp: Math.floor(Date.now() / 1000) + 3600 }),
    ).toString("base64url")}.signature`;
    localStorage.setItem("career-forge.access-token", learnerToken);
    localStorage.setItem("career-forge.user-id", "learner-id");
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: true,
        status: 200,
        json: async () => ({ hosts: ["developer.mozilla.org"] }),
      }),
    );

    const { getReferenceEmbedHosts } = await import("./api-client");
    await expect(getReferenceEmbedHosts()).resolves.toEqual(["developer.mozilla.org"]);
    expect(fetch).toHaveBeenCalledWith(
      expect.stringContaining("/reference/embed-hosts"),
      expect.objectContaining({
        headers: expect.objectContaining({ Authorization: `Bearer ${learnerToken}` }),
      }),
    );
  });
});

describe("completeBorderlessOAuth", () => {
  beforeEach(() => {
    vi.resetModules();
    const localStorage = createMemoryStorage();
    const sessionStorage = createMemoryStorage();
    vi.stubGlobal("window", { localStorage, sessionStorage });
    vi.stubGlobal("localStorage", localStorage);
    vi.stubGlobal("sessionStorage", sessionStorage);
  });

  it("stores the Career Forge JWT from the code exchange", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: true,
        status: 200,
        json: async () => ({
          access_token: "cf-jwt",
          token_type: "bearer",
          external_id: "user-oauth",
          provider: "email",
          expires_in: 3600,
        }),
      }),
    );

    const { completeBorderlessOAuth } = await import("./api-client");
    await completeBorderlessOAuth("auth-code", "state-1");

    expect(fetch).toHaveBeenCalledWith(
      expect.stringMatching(/\/auth\/borderless\/exchange$/),
      expect.objectContaining({
        method: "POST",
        credentials: "include",
        body: JSON.stringify({ code: "auth-code", state: "state-1" }),
      }),
    );
    const calledUrl = String(vi.mocked(fetch).mock.calls[0]?.[0]);
    expect(calledUrl.startsWith("http")).toBe(false);
    expect(localStorage.getItem("career-forge.access-token")).toBe("cf-jwt");
    expect(localStorage.getItem("career-forge.user-id")).toBe("user-oauth");
  });

  it("keeps a 403 detail and hides other failures behind the status", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: false,
        status: 403,
        json: async () => ({ detail: "Borderless email must be verified" }),
      }),
    );
    const { BorderlessOAuthError, completeBorderlessOAuth } = await import("./api-client");
    await expect(completeBorderlessOAuth("auth-code", "state-1")).rejects.toMatchObject({
      message: "Borderless email must be verified",
      status: 403,
      name: "BorderlessOAuthError",
    });
    expect(BorderlessOAuthError).toBeTruthy();

    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: false,
        status: 400,
        json: async () => ({ detail: "upstream leak" }),
      }),
    );
    const again = await import("./api-client");
    await expect(again.completeBorderlessOAuth("auth-code", "state-1")).rejects.toMatchObject({
      message: "Sign-in with Borderless did not finish",
      status: 400,
    });
  });
});

describe("streamDiagnosisInterviewStart", () => {
  beforeEach(() => {
    vi.resetModules();
    const localStorage = createMemoryStorage();
    const sessionStorage = createMemoryStorage();
    vi.stubGlobal("window", { localStorage, sessionStorage });
    vi.stubGlobal("localStorage", localStorage);
    vi.stubGlobal("sessionStorage", sessionStorage);
  });

  it("rethrows PaywallError on HTTP 402 instead of wrapping as cannot-reach", async () => {
    const learnerToken = `header.${Buffer.from(
      JSON.stringify({
        provider: "email",
        exp: Math.floor(Date.now() / 1000) + 3600,
      }),
    ).toString("base64url")}.signature`;
    localStorage.setItem("career-forge.access-token", learnerToken);
    localStorage.setItem("career-forge.user-id", "learner-id");
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(
        new Response(
          JSON.stringify({
            detail: {
              code: "paywall",
              message: "Your included forge is spent. USD $7/mo continues Career Forge.",
              checkout_available: false,
            },
          }),
          {
            status: 402,
            statusText: "Payment Required",
            headers: { "Content-Type": "application/json" },
          },
        ),
      ),
    );

    const { streamDiagnosisInterviewStart } = await import("./api-client");
    const { PaywallError } = await import("./paywall");
    await expect(
      streamDiagnosisInterviewStart({
        goal_id: "rag-engineer",
        motivation: "I want to build production RAG systems with evals.",
        years_xp: "0-1",
      }),
    ).rejects.toBeInstanceOf(PaywallError);
  });

  it("shows the monthly forge ceiling without offering checkout", async () => {
    const learnerToken = `header.${Buffer.from(
      JSON.stringify({
        provider: "email",
        exp: Math.floor(Date.now() / 1000) + 3600,
      }),
    ).toString("base64url")}.signature`;
    localStorage.setItem("career-forge.access-token", learnerToken);
    localStorage.setItem("career-forge.user-id", "learner-id");
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(
        new Response(
          JSON.stringify({
            detail: {
              code: "monthly_forge_ceiling",
              message:
                "Two forges are already complete this month. The next one waits until next month.",
            },
          }),
          {
            status: 409,
            statusText: "Conflict",
            headers: { "Content-Type": "application/json" },
          },
        ),
      ),
    );

    const { startForgeRunFromProfile } = await import("./api-client");
    const { isPaywallError } = await import("./paywall");
    try {
      await startForgeRunFromProfile();
      throw new Error("expected the ceiling");
    } catch (err) {
      expect(isPaywallError(err)).toBe(false);
      expect(err).toBeInstanceOf(Error);
      expect((err as Error).message).toBe(
        "Two forges are already complete this month. The next one waits until next month.",
      );
    }
  });
});
