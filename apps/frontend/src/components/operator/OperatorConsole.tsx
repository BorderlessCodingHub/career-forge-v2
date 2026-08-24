"use client";

import { useCallback, useEffect, useMemo, useState } from "react";

import { Button } from "@/components/ui";
import { BrandMark } from "@/components/ui/BrandMark";
import { AccessDesk } from "@/components/operator/AccessDesk";
import { ContentDesk } from "@/components/operator/ContentDesk";
import {
  getOperatorMe,
  getOperatorSeats,
  OperatorApiError,
  requestOperatorOtp,
  signOutOperator,
  verifyOperatorOtp,
  visibleOperatorDesks,
  type OperatorDeskId,
  type OperatorMe,
  type OperatorSeat,
} from "@/lib/operator-console";

type AuthPhase = "email" | "code";

function OperatorBrand() {
  return (
    <div className="flex items-center gap-3">
      <BrandMark size={36} style={{ height: 36, width: "auto" }} />
      <div>
        <p className="text-sm font-semibold text-text-primary">Career Forge</p>
        <p className="text-xs text-text-muted">Operator console</p>
      </div>
    </div>
  );
}

function OperatorLogin({ onVerified }: { onVerified: () => Promise<void> }) {
  const [phase, setPhase] = useState<AuthPhase>("email");
  const [email, setEmail] = useState("");
  const [code, setCode] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function requestCode() {
    const normalized = email.trim();
    if (!normalized) {
      setError("Enter your Operator email.");
      return;
    }
    setBusy(true);
    setError(null);
    try {
      await requestOperatorOtp(normalized);
      setPhase("code");
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Could not send the code.");
    } finally {
      setBusy(false);
    }
  }

  async function verifyCode() {
    setBusy(true);
    setError(null);
    try {
      await verifyOperatorOtp(email.trim(), code);
      await onVerified();
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Could not verify the code.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <main
      className="grid min-h-screen place-items-center bg-dot-grid bg-dots px-4 py-10"
      data-screen="operator-login"
      data-testid="operator-login"
    >
      <section className="w-full max-w-md rounded-card border border-border bg-surface p-7 shadow-2xl">
        <OperatorBrand />
        <p className="mt-8 font-mono text-xs uppercase tracking-[0.18em] text-accent-mint">
          Restricted workspace
        </p>
        <h1 className="mt-2 text-2xl font-semibold text-text-primary">Operator sign in</h1>
        <p className="mt-2 text-sm leading-6 text-text-secondary">
          Use the separate Operator identity. Learner sessions cannot open this console.
        </p>

        <div className="mt-6 space-y-3">
          <label className="block text-xs font-medium uppercase tracking-wide text-text-muted">
            Operator email
            <input
              type="email"
              value={email}
              disabled={busy || phase === "code"}
              autoComplete="email"
              data-testid="operator-email"
              className="mt-2 w-full rounded-md border border-border bg-bg px-3 py-2.5 text-sm normal-case tracking-normal text-text-primary outline-none focus:border-accent-mint"
              placeholder="operator@borderless.com"
              onChange={(event) => setEmail(event.target.value)}
            />
          </label>

          {phase === "code" ? (
            <label className="block text-xs font-medium uppercase tracking-wide text-text-muted">
              6-digit code
              <input
                type="text"
                inputMode="numeric"
                autoComplete="one-time-code"
                maxLength={6}
                value={code}
                disabled={busy}
                data-testid="operator-code"
                className="mt-2 w-full rounded-md border border-border bg-bg px-3 py-2.5 font-mono text-sm tracking-[0.35em] text-text-primary outline-none focus:border-accent-mint"
                placeholder="000000"
                onChange={(event) =>
                  setCode(event.target.value.replace(/\D/g, "").slice(0, 6))
                }
              />
            </label>
          ) : null}

          {error ? (
            <p className="text-sm text-red-400" data-testid="operator-auth-error">
              {error}
            </p>
          ) : null}

          {phase === "email" ? (
            <Button
              className="w-full"
              disabled={busy}
              data-testid="operator-request-code"
              onClick={() => void requestCode()}
            >
              {busy ? "Sending…" : "Send code"}
            </Button>
          ) : (
            <div className="flex gap-2">
              <Button
                className="flex-1"
                disabled={busy || code.length !== 6}
                data-testid="operator-verify-code"
                onClick={() => void verifyCode()}
              >
                {busy ? "Verifying…" : "Open console"}
              </Button>
              <Button
                variant="ghost"
                disabled={busy}
                onClick={() => {
                  setPhase("email");
                  setCode("");
                  setError(null);
                }}
              >
                Change email
              </Button>
            </div>
          )}
        </div>
      </section>
    </main>
  );
}

function DeskRoom({ desk }: { desk: OperatorDeskId }) {
  if (desk === "access") {
    return <AccessDesk />;
  }

  return <ContentDesk />;
}

function OperatorShell({
  me,
  seats,
  onSignOut,
}: {
  me: OperatorMe;
  seats: OperatorSeat[];
  onSignOut: () => Promise<void>;
}) {
  const desks = useMemo(() => visibleOperatorDesks(me.desks), [me.desks]);
  const [activeDesk, setActiveDesk] = useState<OperatorDeskId>(desks[0]?.id ?? "access");

  useEffect(() => {
    if (!desks.some((desk) => desk.id === activeDesk) && desks[0]) {
      setActiveDesk(desks[0].id);
    }
  }, [activeDesk, desks]);

  return (
    <main
      className="min-h-screen bg-bg text-text-primary"
      data-screen="operator-console"
      data-testid="operator-console"
    >
      <header className="flex min-h-16 items-center justify-between gap-4 border-b border-border bg-bg-sidebar px-5 sm:px-8">
        <OperatorBrand />
        <div className="flex items-center gap-3">
          <span className="hidden text-right text-xs text-text-muted sm:block">{me.email}</span>
          <Button variant="ghost" data-testid="operator-sign-out" onClick={() => void onSignOut()}>
            Sign out
          </Button>
        </div>
      </header>

      <div className="grid min-h-[calc(100vh-4rem)] lg:grid-cols-[15rem_1fr]">
        <aside className="border-b border-border bg-bg-sidebar p-5 lg:border-b-0 lg:border-r">
          <p className="font-mono text-[11px] uppercase tracking-[0.18em] text-text-muted">
            Operator seats
          </p>
          <ul className="mt-3 space-y-2" data-testid="operator-seat-list">
            {seats.map((seat) => (
              <li
                key={seat.email}
                className="truncate rounded-md border border-border-soft bg-surface px-3 py-2 text-xs text-text-secondary"
              >
                {seat.email}
              </li>
            ))}
          </ul>
        </aside>

        <div className="bg-dot-grid bg-dots">
          <nav
            className="flex gap-1 border-b border-border bg-surface/95 px-5 pt-3 sm:px-8"
            aria-label="Operator desks"
            role="tablist"
          >
            {desks.map((desk) => (
              <button
                key={desk.id}
                type="button"
                role="tab"
                aria-selected={activeDesk === desk.id}
                data-testid={`operator-tab-${desk.id}`}
                className={`rounded-t-md border-x border-t px-5 py-2.5 text-sm font-medium transition ${
                  activeDesk === desk.id
                    ? "border-accent bg-accent text-white"
                    : "border-transparent text-text-secondary hover:border-border hover:bg-surface-elevated"
                }`}
                onClick={() => setActiveDesk(desk.id)}
              >
                {desk.label}
              </button>
            ))}
          </nav>
          <div className="p-6 sm:p-10">
            <DeskRoom desk={activeDesk} />
          </div>
        </div>
      </div>
    </main>
  );
}

export function OperatorConsole() {
  const [me, setMe] = useState<OperatorMe | null>(null);
  const [seats, setSeats] = useState<OperatorSeat[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadSession = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const current = await getOperatorMe();
      const currentSeats = await getOperatorSeats();
      setMe(current);
      setSeats(currentSeats);
    } catch (cause) {
      setMe(null);
      setSeats([]);
      if (!(cause instanceof OperatorApiError && cause.status === 401)) {
        setError(cause instanceof Error ? cause.message : "Could not load Operator console.");
      }
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void loadSession();
  }, [loadSession]);

  if (loading) {
    return (
      <main className="grid min-h-screen place-items-center bg-dot-grid bg-dots">
        <p className="font-mono text-sm text-text-muted" data-testid="operator-loading">
          Checking Operator session…
        </p>
      </main>
    );
  }

  if (!me) {
    return (
      <>
        {error ? (
          <p className="fixed inset-x-4 top-4 z-10 mx-auto max-w-md rounded-md border border-red-900 bg-red-950 px-4 py-3 text-sm text-red-200">
            {error}
          </p>
        ) : null}
        <OperatorLogin onVerified={loadSession} />
      </>
    );
  }

  return (
    <OperatorShell
      me={me}
      seats={seats}
      onSignOut={async () => {
        await signOutOperator();
        setMe(null);
        setSeats([]);
      }}
    />
  );
}
