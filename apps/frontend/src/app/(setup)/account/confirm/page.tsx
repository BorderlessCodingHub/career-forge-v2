"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useRef, useState } from "react";
import { useTranslations } from "next-intl";

import { IdentityGateShell } from "@/components/auth/IdentityGateShell";
import { Button } from "@/components/ui";
import { confirmCareerForgeEmail } from "@/lib/api-client";
import { isExpiredAccountLink } from "@/lib/account-link";

type Phase = "working" | "expired" | "failed";

export default function ConfirmCareerForgeAccountPage() {
  const t = useTranslations("identity");
  const router = useRouter();
  const ranRef = useRef(false);
  const tokenRef = useRef("");
  const [phase, setPhase] = useState<Phase>("working");

  async function openAccount(token: string) {
    setPhase("working");
    try {
      await confirmCareerForgeEmail(token);
      router.push("/");
    } catch (err) {
      setPhase(isExpiredAccountLink(err) ? "expired" : "failed");
    }
  }

  useEffect(() => {
    if (ranRef.current) return;
    ranRef.current = true;
    const token = new URLSearchParams(window.location.search).get("token") ?? "";
    tokenRef.current = token;
    if (!token) {
      setPhase("expired");
      return;
    }
    void openAccount(token);
    // The link is consumed once on arrival. Retry is an explicit button.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <IdentityGateShell screen="account-confirm">
      <div className="mx-auto max-w-md rounded-md border border-border bg-surface px-6 py-8">
        {phase === "expired" ? (
          <>
            <p className="text-sm text-text-primary" data-testid="account-link-expired">
              {t("linkExpired")}
            </p>
            <Link
              href="/?account=signup"
              className="mt-4 inline-block text-sm text-accent underline-offset-2 hover:underline"
              data-testid="account-link-again"
            >
              {t("createAccountAgain")}
            </Link>
          </>
        ) : phase === "failed" ? (
          <>
            <p className="text-sm text-text-primary" data-testid="account-link-failed">
              {t("couldNotOpenAccount")}
            </p>
            <Button
              type="button"
              className="mt-4 w-full"
              data-testid="account-link-retry"
              onClick={() => void openAccount(tokenRef.current)}
            >
              {t("tryAgain")}
            </Button>
          </>
        ) : (
          <p className="text-sm text-text-secondary" data-testid="account-link-working">
            {t("openingAccount")}
          </p>
        )}
      </div>
    </IdentityGateShell>
  );
}
