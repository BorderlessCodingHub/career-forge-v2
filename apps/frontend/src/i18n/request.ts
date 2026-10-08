import { cookies } from "next/headers";
import { getRequestConfig } from "next-intl/server";

import { LOCALE_COOKIE, mergeMessages, resolveLocale, type MessageTree } from "@/lib/locale";

import en from "../../messages/en.json";
import ptBR from "../../messages/pt-BR.json";

export default getRequestConfig(async () => {
  const store = await Promise.resolve(cookies());
  const locale = resolveLocale(store.get(LOCALE_COOKIE)?.value);
  const messages =
    locale === "pt-BR"
      ? mergeMessages(en as MessageTree, ptBR as MessageTree)
      : en;

  return { locale, messages };
});
