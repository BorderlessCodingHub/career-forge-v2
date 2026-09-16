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

describe("signInWithPassword", () => {
  beforeEach(() => {
    vi.resetModules();
    const localStorage = createMemoryStorage();
    const sessionStorage = createMemoryStorage();
    vi.stubGlobal("window", { localStorage, sessionStorage });
    vi.stubGlobal("localStorage", localStorage);
    vi.stubGlobal("sessionStorage", sessionStorage);
  });

  it("stores the Career Forge JWT from POST /auth/signin", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: true,
        status: 200,
        json: async () => ({
          access_token: "cf-jwt",
          token_type: "bearer",
          external_id: "user-signin",
          provider: "email",
          expires_in: 3600,
        }),
      }),
    );

    const { signInWithPassword } = await import("./api-client");
    await signInWithPassword("ada@example.com", "secret-pass");

    expect(fetch).toHaveBeenCalledWith(
      expect.stringContaining("/auth/signin"),
      expect.objectContaining({
        body: JSON.stringify({
          email: "ada@example.com",
          password: "secret-pass",
        }),
      }),
    );
    const calledUrl = String(vi.mocked(fetch).mock.calls[0]?.[0]);
    expect(calledUrl).not.toContain("api.borderlesscoding.com");
    expect(localStorage.getItem("career-forge.access-token")).toBe("cf-jwt");
    expect(localStorage.getItem("career-forge.user-id")).toBe("user-signin");
  });

  it("maps signin 401 429 and 503 to distinct copy", async () => {
    const cases: Array<[number, string]> = [
      [401, "Invalid email or password"],
      [429, "Too many sign-in attempts. Try again later."],
      [503, "Sign-in is temporarily unavailable. Try again in a moment."],
    ];
    for (const [status, copy] of cases) {
      vi.resetModules();
      vi.stubGlobal(
        "fetch",
        vi.fn().mockResolvedValue({
          ok: false,
          status,
          statusText: "Error",
          json: async () => ({ detail: "upstream leak" }),
        }),
      );
      const { signInWithPassword } = await import("./api-client");
      await expect(signInWithPassword("ada@example.com", "x")).rejects.toThrow(copy);
    }
  });

  it("maps unexpected signin status to generic 401 copy without leaking detail", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: false,
        status: 403,
        statusText: "Forbidden",
        json: async () => ({ detail: "upstream leak" }),
      }),
    );
    const { signInWithPassword } = await import("./api-client");
    await expect(signInWithPassword("ada@example.com", "x")).rejects.toThrow(
      "Invalid email or password",
    );
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
              message: "Subscribe to start diagnosis and forge your roadmap",
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
});
