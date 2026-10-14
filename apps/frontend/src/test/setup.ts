import { vi } from "vitest";

type MessageTree = { [key: string]: string | MessageTree };

function dig(root: unknown, path: string): unknown {
  let cur = root;
  for (const part of path.split(".")) {
    if (cur == null || typeof cur !== "object") return undefined;
    cur = (cur as MessageTree)[part];
  }
  return cur;
}

function activeLocale(): "en" | "pt-BR" {
  return (globalThis as { __cfLocale?: string }).__cfLocale === "pt-BR" ? "pt-BR" : "en";
}

vi.mock("next-intl", async () => {
  const { mergeMessages } = await import("../lib/locale");
  const en = (await import("../../messages/en.json")).default as MessageTree;
  const ptBR = (await import("../../messages/pt-BR.json")).default as MessageTree;

  return {
    useLocale: () => activeLocale(),
    useTranslations: (namespace: string) => {
      const messages = activeLocale() === "pt-BR" ? mergeMessages(en, ptBR) : en;
      const base = namespace ? dig(messages, namespace) : messages;
      const translate = (key: string, values?: Record<string, string | number>) => {
        const found = dig(base, key);
        let text = typeof found === "string" ? found : key;
        if (values) {
          for (const [name, value] of Object.entries(values)) {
            text = text.replaceAll(`{${name}}`, String(value));
          }
        }
        return text;
      };
      translate.raw = (key: string) => dig(base, key);
      translate.has = (key: string) => dig(base, key) !== undefined;
      return translate;
    },
    NextIntlClientProvider: ({ children }: { children: unknown }) => children,
  };
});
