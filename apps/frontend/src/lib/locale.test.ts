import { describe, expect, it, vi } from "vitest";

import {
  LOCALE_COOKIE,
  buildLocaleCookie,
  localeAfterSignIn,
  mergeMessages,
  parseLocaleCookie,
  resolveLocale,
  syncStoredLocale,
} from "./locale";

describe("resolveLocale", () => {
  it("defaults to English when the cookie is missing or unknown", () => {
    expect(resolveLocale(null)).toBe("en");
    expect(resolveLocale(undefined)).toBe("en");
    expect(resolveLocale("fr")).toBe("en");
    expect(resolveLocale("pt")).toBe("en");
  });

  it("keeps an explicit English or Brazilian Portuguese choice", () => {
    expect(resolveLocale("en")).toBe("en");
    expect(resolveLocale("pt-BR")).toBe("pt-BR");
  });
});

describe("parseLocaleCookie", () => {
  it("reads only cf_locale and ignores other cookies", () => {
    expect(parseLocaleCookie("session=abc; cf_locale=pt-BR")).toBe("pt-BR");
    expect(parseLocaleCookie("cf_locale=en")).toBe("en");
    expect(parseLocaleCookie("session=abc")).toBeNull();
    expect(parseLocaleCookie("cf_locale=fr")).toBeNull();
  });
});

describe("buildLocaleCookie", () => {
  it("writes the choice at the site root", () => {
    expect(buildLocaleCookie("pt-BR", false)).toBe(
      `${LOCALE_COOKIE}=pt-BR; Path=/; Max-Age=31536000; SameSite=Lax`,
    );
    expect(buildLocaleCookie("en", true)).toContain("; Secure");
  });
});

describe("localeAfterSignIn", () => {
  it("lets an explicit cookie overwrite the locale stored on the user", () => {
    expect(
      localeAfterSignIn({ explicitCookie: "pt-BR", stored: "en" }),
    ).toEqual({ display: "pt-BR", persist: "pt-BR", writeCookie: null });
    expect(
      localeAfterSignIn({ explicitCookie: "en", stored: "pt-BR" }),
    ).toEqual({ display: "en", persist: "en", writeCookie: null });
  });

  it("copies a stored locale into the cookie when the learner has not chosen", () => {
    expect(localeAfterSignIn({ explicitCookie: null, stored: "pt-BR" })).toEqual({
      display: "pt-BR",
      persist: null,
      writeCookie: "pt-BR",
    });
  });

  it("stays English when nothing is stored and no choice was made", () => {
    expect(localeAfterSignIn({ explicitCookie: null, stored: null })).toEqual({
      display: "en",
      persist: null,
      writeCookie: null,
    });
    expect(localeAfterSignIn({ explicitCookie: "fr", stored: null })).toEqual({
      display: "en",
      persist: null,
      writeCookie: null,
    });
  });
});

describe("mergeMessages", () => {
  it("falls back to English when a pt-BR string is missing or still blank", () => {
    const merged = mergeMessages(
      { chrome: { signOut: "Sign out", language: "Language" } },
      { chrome: { signOut: "Sair", language: "  " } },
    );
    expect(merged).toEqual({
      chrome: { signOut: "Sair", language: "Language" },
    });
  });
});

describe("syncStoredLocale", () => {
  it("persists the cookie and does not refresh when the learner already chose", async () => {
    const persist = vi.fn(async () => {});
    const writeCookie = vi.fn();
    const refresh = vi.fn();
    const readStored = vi.fn(async () => "en");

    await syncStoredLocale({
      readCookie: () => "pt-BR",
      writeCookie,
      readStored,
      persist,
      refresh,
    });

    expect(persist).toHaveBeenCalledWith("pt-BR");
    expect(readStored).not.toHaveBeenCalled();
    expect(writeCookie).not.toHaveBeenCalled();
    expect(refresh).not.toHaveBeenCalled();
  });

  it("writes the stored Brazilian Portuguese locale and refreshes when no cookie exists", async () => {
    const writeCookie = vi.fn();
    const refresh = vi.fn();

    await syncStoredLocale({
      readCookie: () => null,
      writeCookie,
      readStored: async () => "pt-BR",
      persist: vi.fn(async () => {}),
      refresh,
    });

    expect(writeCookie).toHaveBeenCalledWith("pt-BR");
    expect(refresh).toHaveBeenCalledOnce();
  });
});
