"use client";

import { useRouter } from "next/navigation";
import { useTranslations } from "next-intl";
import { useEffect, useState } from "react";

import { GoalPicker } from "@/components/diagnosis";
import { PaywallPanel } from "@/components/billing/PaywallPanel";
import { Button } from "@/components/ui";
import {
  getMyProfile,
  listForges,
  openForge,
  startForgeRunFromProfile,
} from "@/lib/api-client";
import { setForgeRunId } from "@/lib/forge-session";
import { hydrateOnboardingFromProfile } from "@/lib/profile-reuse";
import { isPaywallError, type PaywallError } from "@/lib/paywall";
import type { ForgeArtifactSummary } from "@/types/contracts";

type GateState =
  | { status: "loading" }
  | { status: "empty"; hasDiagnosis: boolean }
  | { status: "ready"; items: ForgeArtifactSummary[]; hasDiagnosis: boolean }
  | { status: "new-forge"; items: ForgeArtifactSummary[] }
  | { status: "error"; message: string };

function pickContinueTarget(items: ForgeArtifactSummary[]): ForgeArtifactSummary {
  return items.find((item) => item.is_active) ?? items[0];
}

export function LandingRecoveryGate() {
  const router = useRouter();
  const t = useTranslations("recovery");
  const [state, setState] = useState<GateState>({ status: "loading" });
  const [busy, setBusy] = useState(false);
  const [paywall, setPaywall] = useState<PaywallError | null>(null);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const [{ items }, profile] = await Promise.all([
          listForges(),
          getMyProfile().catch(() => null),
        ]);
        if (cancelled) return;
        const hasDiagnosis = Boolean(profile?.has_diagnosis);
        if (items.length === 0) {
          setState({ status: "empty", hasDiagnosis });
          return;
        }
        setState({ status: "ready", items, hasDiagnosis });
      } catch (err) {
        if (cancelled) return;
        const message = err instanceof Error ? err.message : t("failedLoad");
        // Fail open into goal picker so onboarding still works.
        setState({ status: "error", message });
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [t]);

  async function handleContinue(items: ForgeArtifactSummary[]) {
    const target = pickContinueTarget(items);
    setBusy(true);
    try {
      await openForge(target.public_id);
      router.push("/roadmap");
    } catch (err) {
      setBusy(false);
      setState({
        status: "error",
        message: err instanceof Error ? err.message : t("failedOpen"),
      });
    }
  }

  async function handleReforgeFromProfile() {
    setBusy(true);
    setPaywall(null);
    try {
      const profile = await getMyProfile();
      if (!profile.has_diagnosis || !profile.diagnosis) {
        setBusy(false);
        setState({
          status: "error",
          message: t("noDiagnosis"),
        });
        return;
      }
      const hydrated = hydrateOnboardingFromProfile(profile);
      if (hydrated) {
        router.push("/onboarding/edit");
        return;
      }
      const forge = await startForgeRunFromProfile();
      setForgeRunId(forge.run_id);
      router.push("/forge");
    } catch (err) {
      setBusy(false);
      if (isPaywallError(err)) {
        setPaywall(err);
        return;
      }
      setState({
        status: "error",
        message:
          err instanceof Error
            ? err.message
            : t("failedStart"),
      });
    }
  }

  if (state.status === "loading") {
    return (
      <main className="min-h-screen grid-dots flex items-center justify-center p-8">
        <p className="text-text-secondary" data-testid="landing-recovery-loading">
          {t("checking")}
        </p>
      </main>
    );
  }

  if (state.status === "empty") {
    if (state.hasDiagnosis) {
      return (
        <main
          className="min-h-screen grid-dots px-4 py-16"
          data-screen="landing-recovery"
        >
          <div className="mx-auto max-w-lg space-y-6">
            <div>
              <h1 className="text-3xl font-semibold text-text-primary">
                {t("welcome")}
              </h1>
              <p className="mt-2 text-text-secondary">{t("savedDiagnosis")}</p>
            </div>
            <div className="flex flex-col gap-3 sm:flex-row">
              <Button
                data-testid="landing-reforge-profile"
                disabled={busy}
                onClick={() => void handleReforgeFromProfile()}
              >
                {t("reforge")}
              </Button>
              <Button
                variant="ghost"
                data-testid="landing-new-forge"
                disabled={busy}
                onClick={() => setState({ status: "new-forge", items: [] })}
              >
                {t("newFromScratch")}
              </Button>
            </div>
            {paywall ? (
              <PaywallPanel checkoutAvailable={paywall.checkoutAvailable} />
            ) : null}
          </div>
        </main>
      );
    }
    return <GoalPicker />;
  }

  if (state.status === "new-forge") {
    return <GoalPicker />;
  }

  if (state.status === "error") {
    return (
      <main className="min-h-screen grid-dots p-8" data-screen="landing-recovery">
        <div className="mx-auto max-w-lg space-y-4">
          <p className="text-text-secondary">{state.message}</p>
          <Button
            data-testid="landing-recovery-fallback"
            onClick={() => setState({ status: "empty", hasDiagnosis: false })}
          >
            {t("startNew")}
          </Button>
        </div>
      </main>
    );
  }

  const { items, hasDiagnosis } = state;
  const last = pickContinueTarget(items);

  return (
    <main
      className="min-h-screen grid-dots px-4 py-16"
      data-screen="landing-recovery"
    >
      <div className="mx-auto max-w-lg space-y-6">
        <div>
          <h1 className="text-3xl font-semibold text-text-primary">
            {t("welcome")}
          </h1>
          <p className="mt-2 text-text-secondary">
            {items.length === 1
              ? t("savedOne", { count: items.length })
              : t("savedMany", { count: items.length })}
          </p>
        </div>

        <div className="rounded-md border border-border bg-surface px-4 py-3">
          <p className="text-sm text-text-secondary">{t("lastForge")}</p>
          <p className="mt-1 font-medium text-text-primary">{last.title}</p>
          {last.goal_id ? (
            <p className="mt-0.5 text-sm text-text-secondary">{last.goal_id}</p>
          ) : null}
        </div>

        <div className="flex flex-col gap-3 sm:flex-row sm:flex-wrap">
          <Button
            data-testid="landing-continue"
            disabled={busy}
            onClick={() => void handleContinue(items)}
          >
            {t("continue")}
          </Button>
          <Button
            variant="ghost"
            data-testid="landing-view-all"
            disabled={busy}
            onClick={() => router.push("/forges")}
          >
            {t("viewAll")}
          </Button>
          {hasDiagnosis ? (
            <Button
              variant="ghost"
              data-testid="landing-reforge-profile"
              disabled={busy}
              onClick={() => void handleReforgeFromProfile()}
            >
              {t("reforge")}
            </Button>
          ) : null}
          <Button
            variant="ghost"
            data-testid="landing-new-forge"
            disabled={busy}
            onClick={() => setState({ status: "new-forge", items })}
          >
            {t("newForge")}
          </Button>
        </div>
        {paywall ? (
          <PaywallPanel checkoutAvailable={paywall.checkoutAvailable} />
        ) : null}
      </div>
    </main>
  );
}
