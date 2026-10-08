"use client";

import { useState } from "react";
import { useLocale } from "next-intl";
import { useTranslations } from "next-intl";
import { useRouter } from "next/navigation";

import { updateMyLocale } from "@/lib/api-client";
import { writeLocaleCookie, type Locale } from "@/lib/locale";
import { hasEmailIdentity } from "@/lib/user-session";

const OPTIONS: { locale: Locale; label: string }[] = [
  { locale: "en", label: "EN" },
  { locale: "pt-BR", label: "PT" },
];

type LocaleSwitchProps = {
  className?: string;
  tone?: "default" | "dark";
};

export function LocaleSwitch({ className = "", tone = "default" }: LocaleSwitchProps) {
  const locale = useLocale();
  const t = useTranslations("chrome");
  const router = useRouter();
  const [pending, setPending] = useState<Locale | null>(null);

  async function choose(next: Locale) {
    if (next === locale || pending) return;
    setPending(next);
    writeLocaleCookie(next);
    try {
      if (hasEmailIdentity()) await updateMyLocale(next);
    } catch {
      // The cookie already selects the catalog. Sign-in retries the write.
    } finally {
      router.refresh();
      setPending(null);
    }
  }

  return (
    <div
      role="group"
      aria-label={t("language")}
      data-testid="locale-switch"
      className={`inline-flex items-center rounded-md border text-[10px] font-semibold ${
        tone === "dark" ? "border-slate-600" : "border-border"
      } ${className}`.trim()}
    >
      {OPTIONS.map((option) => {
        const selected = locale === option.locale;
        return (
          <button
            key={option.locale}
            type="button"
            aria-pressed={selected}
            data-testid={`locale-switch-${option.locale}`}
            disabled={pending !== null}
            className={`px-2 py-1 ${
              selected
                ? tone === "dark"
                  ? "bg-white/10 text-white"
                  : "bg-surface text-text-primary"
                : tone === "dark"
                  ? "text-slate-400"
                  : "text-text-muted"
            }`}
            onClick={() => void choose(option.locale)}
          >
            {option.label}
          </button>
        );
      })}
    </div>
  );
}
