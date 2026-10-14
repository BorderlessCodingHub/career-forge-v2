"use client";

import { useTranslations } from "next-intl";

type Values = Record<string, string | number>;

export function useWelcomeText() {
  const t = useTranslations("welcome");
  const text = (key: string, values?: Values) =>
    (t as unknown as (key: string, values?: Values) => string)(key, values);
  const raw = <T,>(key: string): T => (t as unknown as { raw: (key: string) => T }).raw(key);
  const list = <T,>(key: string): T[] => {
    const value = raw<T[] | Record<string, T>>(key);
    return Array.isArray(value) ? value : Object.values(value);
  };
  return { text, raw, list };
}
