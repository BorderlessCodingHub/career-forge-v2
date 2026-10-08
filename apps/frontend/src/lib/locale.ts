export const LOCALES = ["en", "pt-BR"] as const;

export type Locale = (typeof LOCALES)[number];

export const LOCALE_COOKIE = "cf_locale";

export const DEFAULT_LOCALE: Locale = "en";

export type MessageTree = {
  [key: string]: string | MessageTree;
};

export type LocalePlan = {
  display: Locale;
  persist: Locale | null;
  writeCookie: Locale | null;
};

export function isLocale(raw: string | null | undefined): raw is Locale {
  return (LOCALES as readonly string[]).includes(raw ?? "");
}

export function resolveLocale(raw: string | null | undefined): Locale {
  return isLocale(raw) ? raw : DEFAULT_LOCALE;
}

export function parseLocaleCookie(header: string | null | undefined): Locale | null {
  if (!header) return null;
  for (const part of header.split(";")) {
    const [name, ...rest] = part.trim().split("=");
    if (name !== LOCALE_COOKIE) continue;
    const value = decodeURIComponent(rest.join("="));
    return isLocale(value) ? value : null;
  }
  return null;
}

export function buildLocaleCookie(locale: Locale, secure: boolean): string {
  const suffix = secure ? "; Secure" : "";
  return `${LOCALE_COOKIE}=${locale}; Path=/; Max-Age=31536000; SameSite=Lax${suffix}`;
}

export function readLocaleCookie(): Locale | null {
  if (typeof document === "undefined") return null;
  return parseLocaleCookie(document.cookie);
}

export function writeLocaleCookie(locale: Locale): void {
  const secure =
    typeof location !== "undefined" && location.protocol === "https:";
  document.cookie = buildLocaleCookie(locale, secure);
}

/** Cookie wins. A stored locale is copied into the cookie only when no choice exists. */
export function localeAfterSignIn(input: {
  explicitCookie: string | null | undefined;
  stored: string | null | undefined;
}): LocalePlan {
  const explicit = isLocale(input.explicitCookie) ? input.explicitCookie : null;
  if (explicit) {
    return { display: explicit, persist: explicit, writeCookie: null };
  }
  const stored = isLocale(input.stored) ? input.stored : null;
  if (stored) {
    return { display: stored, persist: null, writeCookie: stored };
  }
  return { display: DEFAULT_LOCALE, persist: null, writeCookie: null };
}

/** Blank or missing pt-BR strings stay English. */
export function mergeMessages(base: MessageTree, overlay: MessageTree): MessageTree {
  const merged: MessageTree = { ...base };
  for (const [key, value] of Object.entries(overlay)) {
    const current = merged[key];
    if (isTree(value) && isTree(current)) {
      merged[key] = mergeMessages(current, value);
      continue;
    }
    if (typeof value === "string" && value.trim() !== "") {
      merged[key] = value;
    }
  }
  return merged;
}

export async function syncStoredLocale(io: {
  readCookie: () => string | null;
  writeCookie: (locale: Locale) => void;
  readStored: () => Promise<string | null | undefined>;
  persist: (locale: Locale) => Promise<void>;
  refresh: () => void;
}): Promise<void> {
  const chosen = localeAfterSignIn({
    explicitCookie: io.readCookie(),
    stored: null,
  });
  if (chosen.persist) {
    await io.persist(chosen.persist);
    return;
  }
  const stored = localeAfterSignIn({
    explicitCookie: null,
    stored: await io.readStored(),
  });
  if (!stored.writeCookie) return;
  io.writeCookie(stored.writeCookie);
  if (stored.display !== DEFAULT_LOCALE) io.refresh();
}

function isTree(value: string | MessageTree | undefined): value is MessageTree {
  return typeof value === "object" && value !== null;
}
