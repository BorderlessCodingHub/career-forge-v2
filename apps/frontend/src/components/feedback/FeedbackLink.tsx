"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { MessageSquare } from "lucide-react";
import { useTranslations } from "next-intl";
import { useEffect, useState } from "react";

import { getMyProfile } from "@/lib/api-client";
import { hasEmailIdentity } from "@/lib/user-session";

const linkClass =
  "inline-flex h-9 items-center gap-2 rounded-md border border-border px-3 text-xs font-medium text-text-secondary transition hover:border-accent/40 hover:bg-surface hover:text-text-primary";

export function FeedbackLink() {
  const t = useTranslations("feedback");
  const pathname = usePathname();
  const [email, setEmail] = useState<string | null>(null);

  useEffect(() => {
    if (!hasEmailIdentity()) return;
    let cancelled = false;
    void getMyProfile()
      .then((profile) => {
        if (!cancelled) setEmail(profile.email);
      })
      .catch(() => {
        if (!cancelled) setEmail(null);
      });
    return () => {
      cancelled = true;
    };
  }, []);

  if (!email) return null;

  const from =
    pathname && pathname !== "/feedback"
      ? `?from=${encodeURIComponent(pathname)}`
      : "";

  return (
    <Link href={`/feedback${from}`} className={linkClass} data-testid="feedback-link">
      <MessageSquare className="h-4 w-4" aria-hidden />
      <span>{t("link")}</span>
    </Link>
  );
}
