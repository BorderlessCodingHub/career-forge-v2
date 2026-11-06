"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useTranslations } from "next-intl";
import { useEffect, useState } from "react";

import {
  BorderlessOAuthError,
  completeBorderlessOAuth,
} from "@/lib/api-client";

export default function BorderlessCallbackPage() {
  const t = useTranslations("identity");
  const router = useRouter();
  const [message, setMessage] = useState<string | null>(null);

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const code = params.get("code");
    const state = params.get("state");
    if (params.get("error") || !code || !state) {
      router.replace("/?oauth=failed");
      return;
    }
    let cancelled = false;
    void completeBorderlessOAuth(code, state)
      .then(() => {
        if (!cancelled) router.replace("/");
      })
      .catch((err: unknown) => {
        if (cancelled) return;
        if (
          err instanceof BorderlessOAuthError &&
          (err.status === 403 || err.status === 409)
        ) {
          setMessage(err.message);
          return;
        }
        router.replace("/?oauth=failed");
      });
    return () => {
      cancelled = true;
    };
  }, [router]);

  return (
    <main className="min-h-screen grid-dots flex items-center justify-center p-8">
      <div className="flex flex-col items-center">
        <p className="text-sm text-text-secondary" data-testid="borderless-oauth-callback">
          {message ?? t("borderlessOAuthWorking")}
        </p>
        {message ? (
          <Link
            href="/"
            className="mt-4 text-sm text-accent underline-offset-2 hover:underline"
            data-testid="borderless-oauth-back"
          >
            {t("backToCareerForge")}
          </Link>
        ) : null}
      </div>
    </main>
  );
}
