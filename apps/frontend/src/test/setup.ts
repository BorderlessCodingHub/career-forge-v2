import { vi } from "vitest";

vi.mock("next-intl", async () => {
  const en = (await import("../../messages/en.json")).default as Record<
    string,
    Record<string, string>
  >;
  return {
    useLocale: () => "en",
    useTranslations: (namespace: string) => {
      return (key: string, values?: Record<string, string | number>) => {
        const bag = en[namespace] ?? {};
        let text = bag[key] ?? key;
        if (values) {
          for (const [name, value] of Object.entries(values)) {
            text = text.replaceAll(`{${name}}`, String(value));
          }
        }
        return text;
      };
    },
    NextIntlClientProvider: ({ children }: { children: unknown }) => children,
  };
});
