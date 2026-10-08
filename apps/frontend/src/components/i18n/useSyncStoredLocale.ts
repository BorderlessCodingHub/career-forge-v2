"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";

import { getMyProfile, updateMyLocale } from "@/lib/api-client";
import { readLocaleCookie, syncStoredLocale, writeLocaleCookie } from "@/lib/locale";
import { hasEmailIdentity } from "@/lib/user-session";

export function useSyncStoredLocale(active: boolean) {
  const router = useRouter();

  useEffect(() => {
    if (!active || !hasEmailIdentity()) return;
    void syncStoredLocale({
      readCookie: () => readLocaleCookie(),
      writeCookie: writeLocaleCookie,
      readStored: async () => (await getMyProfile()).ui_locale,
      persist: updateMyLocale,
      refresh: () => router.refresh(),
    }).catch(() => undefined);
  }, [active, router]);
}
