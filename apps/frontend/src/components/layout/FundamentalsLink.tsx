"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useTranslations } from "next-intl";
import { useEffect, useState } from "react";

import { listForges, listFundamentals } from "@/lib/api-client";
import { fundamentalsPath, isRoadmapScreen } from "@/lib/fundamentals";

const linkClass =
  "inline-flex h-9 items-center rounded-md border border-border px-3 text-xs font-medium text-text-secondary transition hover:border-accent/40 hover:bg-surface hover:text-text-primary";

async function entryHref(onRoadmap: boolean): Promise<string | null> {
  if (onRoadmap) {
    const { items } = await listForges();
    const active = items.find((item) => item.is_active);
    if (active?.goal_id) return fundamentalsPath(active.goal_id);
  }
  const catalog = await listFundamentals();
  const first = catalog.goals[0]?.goal_id;
  return first ? fundamentalsPath(first) : null;
}

export function FundamentalsLink() {
  const pathname = usePathname();
  const t = useTranslations("chrome");
  const onRoadmap = isRoadmapScreen(pathname);
  const [href, setHref] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    void entryHref(onRoadmap)
      .then((next) => {
        if (!cancelled) setHref(next);
      })
      .catch(() => {
        if (!cancelled) setHref(null);
      });
    return () => {
      cancelled = true;
    };
  }, [onRoadmap]);

  if (!href) return null;

  return (
    <Link href={href} className={linkClass} data-testid="fundamentals-link">
      {t("fundamentals")}
    </Link>
  );
}
