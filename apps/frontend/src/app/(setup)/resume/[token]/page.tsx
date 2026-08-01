"use client";

import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import { useEffect, useState } from "react";

import { Button } from "@/components/ui";
import { consumeResumeLink, listForges, openForge } from "@/lib/api-client";
import { adoptSession } from "@/lib/user-session";

export default function ResumeForgePage() {
  const params = useParams<{ token: string }>();
  const token = params.token;
  const router = useRouter();
  const [error, setError] = useState<string | null>(null);
  const [status, setStatus] = useState<"working" | "done" | "failed">("working");

  useEffect(() => {
    if (!token) return;
    let cancelled = false;
    (async () => {
      try {
        const session = await consumeResumeLink(token);
        if (cancelled) return;
        adoptSession(session.access_token, session.external_id);

        const { items } = await listForges();
        const target = items.find((item) => item.is_active) ?? items[0];
        if (target) {
          await openForge(target.public_id);
        }
        if (cancelled) return;
        setStatus("done");
        router.replace("/roadmap");
      } catch (err) {
        if (cancelled) return;
        setStatus("failed");
        setError(err instanceof Error ? err.message : "Resume link unavailable");
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [token, router]);

  return (
    <main
      className="min-h-screen grid-dots flex items-center justify-center px-4 py-10"
      data-screen="resume-consume"
    >
      <div className="mx-auto max-w-md space-y-4 text-center">
        {status === "working" ? (
          <p className="text-text-secondary" data-testid="resume-working">
            Restoring your session…
          </p>
        ) : null}
        {status === "failed" ? (
          <>
            <h1 className="text-2xl font-semibold text-text-primary">
              Resume link unavailable
            </h1>
            <p className="text-text-secondary" data-testid="resume-error">
              {error ??
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
