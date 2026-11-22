"use client";

import Link from "next/link";
import { useTranslations } from "next-intl";

import { FUNDAMENTALS_ENTRY_HREF } from "@/lib/fundamentals";

const linkClass =
  "inline-flex h-9 items-center rounded-md border border-border px-3 text-xs font-medium text-text-secondary transition hover:border-accent/40 hover:bg-surface hover:text-text-primary";

export function FundamentalsLink() {
  const t = useTranslations("chrome");
  return (
    <Link href={FUNDAMENTALS_ENTRY_HREF} className={linkClass} data-testid="fundamentals-link">
      {t("fundamentals")}
    </Link>
  );
}
