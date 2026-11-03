"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useTranslations } from "next-intl";
import { useEffect, useState } from "react";

import { getMyProfile } from "@/lib/api-client";
import { hasEmailIdentity } from "@/lib/user-session";

const linkClass =
  "text-xs font-medium text-text-secondary underline-offset-2 hover:text-text-primary hover:underline";

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
      {t("link")}
    </Link>
  );
}
