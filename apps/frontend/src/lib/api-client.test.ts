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
      JSON.stringify({ provider: "email" }),
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
