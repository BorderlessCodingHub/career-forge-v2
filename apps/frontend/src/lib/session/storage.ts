type StorageKind = "session" | "local";

function getStorage(kind: StorageKind): Storage | null {
  if (typeof window === "undefined") return null;
  return kind === "session" ? window.sessionStorage : window.localStorage;
}

export function readJson<T>(key: string, kind: StorageKind = "session"): T | null {
  const storage = getStorage(kind);
  if (!storage) return null;
  const raw = storage.getItem(key);
  if (!raw) return null;
  try {
    return JSON.parse(raw) as T;
  } catch {
    return null;
  }
}

export function writeJson(key: string, value: unknown, kind: StorageKind = "session"): void {
  const storage = getStorage(kind);
  if (!storage) return;
  storage.setItem(key, JSON.stringify(value));
}

export function readString(key: string, kind: StorageKind = "session"): string | null {
  const storage = getStorage(kind);
  if (!storage) return null;
  return storage.getItem(key);
}

export function writeString(key: string, value: string, kind: StorageKind = "session"): void {
  const storage = getStorage(kind);
  if (!storage) return;
  storage.setItem(key, value);
}

export function removeItem(key: string, kind: StorageKind = "session"): void {
  const storage = getStorage(kind);
  if (!storage) return;
  storage.removeItem(key);
}

export function removeItems(keys: string[], kind: StorageKind = "session"): void {
  keys.forEach((key) => removeItem(key, kind));
}

const CAREER_FORGE_PREFIXES = ["career-forge.", "career-forge:"] as const;

function keyMatchesCareerForgePrefix(key: string): boolean {
  return CAREER_FORGE_PREFIXES.some((prefix) => key.startsWith(prefix));
}

/** Wipe all career-forge.* and career-forge: keys from local + session storage. */
export function clearCareerForgeStorage(): void {
  for (const kind of ["local", "session"] as const) {
    const storage = getStorage(kind);
    if (!storage) continue;
    const keys: string[] = [];
    for (let i = 0; i < storage.length; i += 1) {
      const key = storage.key(i);
      if (key && keyMatchesCareerForgePrefix(key)) {
        keys.push(key);
      }
    }
    keys.forEach((key) => storage.removeItem(key));
  }
}
