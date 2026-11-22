"use client";

import { LogOut } from "lucide-react";
import { useTranslations } from "next-intl";
import { useEffect, useState } from "react";

import { hasEmailIdentity, signOut } from "@/lib/user-session";

const buttonClass =
  "inline-flex h-9 items-center gap-2 rounded-md border border-border px-3 text-xs font-medium text-text-secondary transition hover:border-accent/40 hover:bg-surface hover:text-text-primary disabled:opacity-50";

const quietClass =
  "inline-flex items-center gap-1.5 text-sm font-medium text-text-secondary transition hover:text-text-primary disabled:opacity-50";

type SignOutButtonProps = {
  className?: string;
  appearance?: "button" | "quiet";
};

export function SignOutButton({ className = "", appearance = "button" }: SignOutButtonProps) {
  const t = useTranslations("chrome");
  const [visible, setVisible] = useState(false);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    setVisible(hasEmailIdentity());
  }, []);

  if (!visible) return null;

  return (
    <button
      type="button"
      className={`${appearance === "quiet" ? quietClass : buttonClass} ${className}`.trim()}
      data-testid="sign-out-button"
      disabled={busy}
      onClick={async () => {
        setBusy(true);
        try {
          await signOut();
        } finally {
          setBusy(false);
        }
      }}
    >
      <LogOut className="h-4 w-4" aria-hidden />
      <span>{t("signOut")}</span>
    </button>
  );
}
