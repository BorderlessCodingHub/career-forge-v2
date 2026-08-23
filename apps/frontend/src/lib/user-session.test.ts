import { beforeEach, describe, expect, it, vi } from "vitest";

function createMemoryStorage(): Storage {
  const map = new Map<string, string>();
  return {
    get length() {
      return map.size;
    },
    clear() {
      map.clear();
    },
    getItem(key: string) {
      return map.get(key) ?? null;
    },
    key(index: number) {
      return [...map.keys()][index] ?? null;
    },
    removeItem(key: string) {
      map.delete(key);
    },
    setItem(key: string, value: string) {
      map.set(key, value);
    },
  } as Storage;
}

function installBrowserStorage() {
  const local = createMemoryStorage();
  const session = createMemoryStorage();
  const confirmMock = vi.fn(() => true);
  vi.stubGlobal("window", {
    localStorage: local,
    sessionStorage: session,
    location: { assign: vi.fn() },
    confirm: confirmMock,
  });
  vi.stubGlobal("localStorage", local);
  vi.stubGlobal("sessionStorage", session);
  vi.stubGlobal("confirm", confirmMock);
  return { local, session, confirmMock };
}

describe("clearCareerForgeStorage", () => {
  beforeEach(() => {
    vi.resetModules();
    installBrowserStorage();
  });

  it("removes career-forge dot and colon prefixed keys from both storages", async () => {
    const { clearCareerForgeStorage } = await import("./session/storage");
    localStorage.setItem("career-forge.access-token", "jwt");
    localStorage.setItem("other-app.token", "keep");
    sessionStorage.setItem("career-forge.diagnosis-session-id", "sess-1");
    sessionStorage.setItem("career-forge:adaptive-plan", "{}");

    clearCareerForgeStorage();

    expect(localStorage.getItem("career-forge.access-token")).toBeNull();
    expect(localStorage.getItem("other-app.token")).toBe("keep");
    expect(sessionStorage.getItem("career-forge.diagnosis-session-id")).toBeNull();
    expect(sessionStorage.getItem("career-forge:adaptive-plan")).toBeNull();
  });
});

describe("hasInProgressWork", () => {
  beforeEach(() => {
    vi.resetModules();
    installBrowserStorage();
  });

  it("is true when diagnosis session id exists", async () => {
    const { hasInProgressWork } = await import("./user-session");
    sessionStorage.setItem("career-forge.diagnosis-session-id", "abc");
    expect(hasInProgressWork()).toBe(true);
  });

  it("is true when forge run id exists", async () => {
    const { hasInProgressWork } = await import("./user-session");
    sessionStorage.setItem("career-forge.forge-run-id", "run-1");
    expect(hasInProgressWork()).toBe(true);
  });

  it("is false when neither key exists", async () => {
    const { hasInProgressWork } = await import("./user-session");
    expect(hasInProgressWork()).toBe(false);
  });
});

describe("signOut", () => {
  beforeEach(() => {
    vi.resetModules();
    installBrowserStorage();
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue({ ok: true, status: 204 }));
  });

  it("calls sign-out API then wipes storage and redirects", async () => {
    const { signOut } = await import("./user-session");
    localStorage.setItem("career-forge.access-token", "jwt-token");
    localStorage.setItem("career-forge.user-id", "user-abc");
    sessionStorage.setItem("career-forge.goal", "rag-engineer");

    await signOut({ skipConfirm: true });

    expect(fetch).toHaveBeenCalledWith(
      expect.stringContaining("/auth/sign-out"),
      expect.objectContaining({
        method: "POST",
        headers: { Authorization: "Bearer jwt-token" },
      }),
    );
    expect(localStorage.getItem("career-forge.access-token")).toBeNull();
    expect(sessionStorage.getItem("career-forge.goal")).toBeNull();
    expect(window.location.assign).toHaveBeenCalled();
  });

  it("prompts before sign-out when in-progress work exists", async () => {
    const { confirmMock } = installBrowserStorage();
    const { SIGN_OUT_CONFIRM_MESSAGE, signOut } = await import("./user-session");
    sessionStorage.setItem("career-forge.forge-run-id", "run-1");
    localStorage.setItem("career-forge.access-token", "jwt-token");

    await signOut();

    expect(confirmMock).toHaveBeenCalledWith(SIGN_OUT_CONFIRM_MESSAGE);
  });

  it("aborts when confirm is declined", async () => {
    const { confirmMock } = installBrowserStorage();
    confirmMock.mockReturnValue(false);
    const { signOut } = await import("./user-session");
    sessionStorage.setItem("career-forge.diagnosis-session-id", "sess");
    localStorage.setItem("career-forge.access-token", "jwt-token");

    await signOut();

    expect(fetch).not.toHaveBeenCalled();
    expect(localStorage.getItem("career-forge.access-token")).toBe("jwt-token");
    expect(window.location.assign).not.toHaveBeenCalled();
  });
});
