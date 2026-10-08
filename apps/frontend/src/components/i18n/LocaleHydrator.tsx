"use client";

import { useSyncStoredLocale } from "@/components/i18n/useSyncStoredLocale";

export function LocaleHydrator() {
  useSyncStoredLocale(true);
  return null;
}
