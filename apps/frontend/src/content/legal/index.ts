import type { Locale } from "@/lib/locale";

import { enLegal } from "./en";
import { ptLegal } from "./pt-BR";
import type { LegalDocumentCopy, LegalPack, LegalPageId } from "./types";

export type { Block, LegalDocumentCopy, LegalPageId, LegalPack } from "./types";

export function legalPack(locale: Locale): LegalPack {
  return locale === "pt-BR" ? ptLegal : enLegal;
}

export function legalDocument(locale: Locale, page: LegalPageId): LegalDocumentCopy {
  return legalPack(locale).pages[page];
}
