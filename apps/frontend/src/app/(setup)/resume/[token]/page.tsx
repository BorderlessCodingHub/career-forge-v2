"use client";

import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import { useEffect, useRef, useState } from "react";

import { Button } from "@/components/ui";
import { consumeResumeLink, listForges, openForge } from "@/lib/api-client";
import { adoptSession, getAccessToken, getUserId } from "@/lib/user-session";
import type { ResumeConsumeResponse } from "@/types/contracts";

type Phase =
  | { status: "working" }
  | { status: "conflict"; pending: ResumeConsumeResponse; localCount: number }
  | { status: "done" }
  | { status: "failed"; message: string };

async function openActiveOrNewest(): Promise<void> {
  const { items } = await listForges();
  const target = items.find((item) => item.is_active) ?? items[0];
  if (target) {
    await openForge(target.public_id);
  }
}

export default function ResumeForgePage() {
  const params = useParams<{ token: string }>();
  const token = params.token;
  const router = useRouter();
  const [phase, setPhase] = useState<Phase>({ status: "working" });
  const ranRef = useRef(false);

  useEffect(() => {
    if (!token || ranRef.current) return;
    ranRef.current = true;
    let cancelled = false;

    (async () => {
      try {
        let localHasForges = false;
        let localExternalId: string | null = null;
        if (getAccessToken()) {
          try {
            localExternalId = getUserId();
            const { items } = await listForges();
            localHasForges = items.length > 0;
          } catch {
            localHasForges = false;
          }
        }

        const session = await consumeResumeLink(token);
        if (cancelled) return;

        const conflict =
          localHasForges &&
          localExternalId !== null &&
          localExternalId !== session.external_id;

        if (conflict) {
          setPhase({
            status: "conflict",
            pending: session,
            localCount: 1,
          });
          // Refresh local count for copy (best-effort).
          try {
            const { items } = await listForges();
            if (!cancelled) {
              setPhase({
                status: "conflict",
                pending: session,
                localCount: items.length,
              });
            }
          } catch {
            /* keep count=1 */
          }
          return;
        }

        adoptSession(session.access_token, session.external_id);
        await openActiveOrNewest();
        if (cancelled) return;
        setPhase({ status: "done" });
        router.replace("/roadmap");
      } catch (err) {
        if (cancelled) return;
        setPhase({
          status: "failed",
          message:
            err instanceof Error ? err.message : "Resume link unavailable",
        });
      }
    })();

    return () => {
      cancelled = true;
    };
  }, [token, router]);

  async function handleSwitchToResume(pending: ResumeConsumeResponse) {
    setPhase({ status: "working" });
    try {
      adoptSession(pending.access_token, pending.external_id);
      await openActiveOrNewest();
      setPhase({ status: "done" });
      router.replace("/roadmap");
    } catch (err) {
      setPhase({
        status: "failed",
        message:
          err instanceof Error ? err.message : "Failed to switch session",
      });
    }
  }

  function handleKeepLocal() {
    router.replace("/forges");
  }

  return (
    <main
      className="min-h-screen grid-dots flex items-center justify-center px-4 py-10"
      data-screen="resume-consume"
    >
      <div className="mx-auto max-w-md space-y-4 text-center">
        {phase.status === "working" ? (
          <p className="text-text-secondary" data-testid="resume-working">
            Restoring your session…
          </p>
        ) : null}

        {phase.status === "conflict" ? (
          <div className="space-y-4 text-left" data-testid="resume-conflict">
            <h1 className="text-2xl font-semibold text-text-primary text-center">
              Session conflict
            </h1>
            <p className="text-text-secondary text-center">
              This browser already has {phase.localCount} saved forge
              {phase.localCount === 1 ? "" : "s"} for a different account. Keep
              your local session, or switch to the resume link owner.
            </p>
            <div className="flex flex-col gap-3 sm:flex-row sm:justify-center">
              <Button
                data-testid="resume-keep-local"
                onClick={handleKeepLocal}
              >
                Keep local session
              </Button>
              <Button
                variant="ghost"
                data-testid="resume-switch"
                onClick={() => void handleSwitchToResume(phase.pending)}
              >
                Switch to resume
              </Button>
            </div>
          </div>
        ) : null}

        {phase.status === "failed" ? (
          <>
            <h1 className="text-2xl font-semibold text-text-primary">
              Resume link unavailable
            </h1>
            <p className="text-text-secondary" data-testid="resume-error">
              {phase.message ??
                "This link may have already been used or expired (~7 days)."}
            </p>
            <Link href="/">
              <Button data-testid="resume-home">Go home</Button>
            </Link>
          </>
        ) : null}
      </div>
    </main>
  );
}
