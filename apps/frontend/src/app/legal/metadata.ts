import type { Metadata } from "next";
import { cookies } from "next/headers";

import { legalDocument, type LegalPageId } from "@/content/legal";
import { LOCALE_COOKIE, resolveLocale } from "@/lib/locale";

export async function legalMetadata(page: LegalPageId): Promise<Metadata> {
  const store = await Promise.resolve(cookies());
  const locale = resolveLocale(store.get(LOCALE_COOKIE)?.value);
  const doc = legalDocument(locale, page);
  return {
    title: `${doc.title} · Career Forge`,
    description: doc.description,
  };
}
