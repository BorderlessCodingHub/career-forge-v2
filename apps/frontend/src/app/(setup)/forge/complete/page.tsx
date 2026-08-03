"use client";

import Link from "next/link";
import { useEffect, useRef, useState } from "react";

import { StreamReveal } from "@/components/forge";
import { Button } from "@/components/ui";
import {
  absoluteAppUrl,
  listForges,
  mintResumeLink,
  updateMyEmail,
} from "@/lib/api-client";
import { getForgeGraph, type ForgeGraphNode } from "@/lib/forge-session";

export default function ForgeCompletePage() {
  const [graph, setGraph] = useState<ForgeGraphNode[] | null>(null);
  const [revealed, setRevealed] = useState(0);
  const [resumeUrl, setResumeUrl] = useState<string | null>(null);
  const [resumeError, setResumeError] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);
  const [email, setEmail] = useState("");
  const [emailStatus, setEmailStatus] = useState<
    "idle" | "saving" | "saved" | "error"
  >("idle");
  const [emailError, setEmailError] = useState<string | null>(null);
  const resumeMintedRef = useRef(false);
  const sentinelRef = useRef<HTMLDivElement>(null);
  const autoScrollRef = useRef(true);

  useEffect(() => {
    const handleScroll = () => {
      const { scrollHeight, scrollTop, clientHeight } = document.documentElement;
      autoScrollRef.current = scrollHeight - scrollTop - clientHeight < 150;
    };
    window.addEventListener("scroll", handleScroll, { passive: true });
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  useEffect(() => {
    window.scrollTo(0, 0);
    setGraph(getForgeGraph());
  }, []);

  useEffect(() => {
    if (!graph?.length) return;
    if (revealed >= graph.length) return;
    const timer = setTimeout(() => setRevealed((n) => n + 1), 280);
    return () => clearTimeout(timer);
  }, [graph, revealed]);

  useEffect(() => {
    if (revealed === 0) return;
    if (!autoScrollRef.current) return;
    const { scrollHeight, clientHeight } = document.documentElement;
    if (scrollHeight <= clientHeight) return;
    requestAnimationFrame(() => {
      sentinelRef.current?.scrollIntoView({ behavior: "smooth" });
    });
  }, [revealed]);

  useEffect(() => {
    if (!graph?.length) return;
    if (resumeMintedRef.current) return;
    resumeMintedRef.current = true;
    let cancelled = false;
    (async () => {
      try {
        const { items } = await listForges();
        const target = items.find((item) => item.is_active) ?? items[0];
        if (!target) {
          if (!cancelled) {
            setResumeError("Resume link unavailable — no forge artifact yet.");
          }
          return;
        }
        const minted = await mintResumeLink(target.public_id);
        if (!cancelled) setResumeUrl(absoluteAppUrl(minted.path));
      } catch (err) {
        if (!cancelled) {
          setResumeError(
            err instanceof Error ? err.message : "Failed to mint resume link",
          );
        }
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [graph]);

  async function handleSaveEmail() {
    const next = email.trim();
    if (!next) {
      setEmailError("Enter an email to save.");
      setEmailStatus("error");
      return;
    }
    setEmailStatus("saving");
    setEmailError(null);
    try {
      await updateMyEmail(next);
      setEmailStatus("saved");
    } catch (err) {
      setEmailStatus("error");
      setEmailError(err instanceof Error ? err.message : "Failed to save email");
    }
  }

  if (!graph?.length) {
    return (
      <main className="min-h-screen grid-dots p-8">
        <p className="text-text-secondary">No forged graph yet.</p>
        <Link href="/forge" className="mt-4 inline-block text-accent">
          Back to forge
        </Link>
      </main>
    );
  }

  const done = revealed >= graph.length;

  return (
    <main
      className="min-h-screen grid-dots px-4 py-10"
      data-screen="forge-reveal"
    >
      <div className="mx-auto max-w-2xl">
        <h1 className="text-3xl font-semibold text-text-primary">
          Your trail is ready
        </h1>
        <p className="mt-2 text-text-secondary">
          Each chapter of your plan appears below. Explore the trail and start studying.
        </p>

        <ol className="mt-10 space-y-4">
          {graph.slice(0, revealed).map((node) => (
            <li
              key={node.node_id}
              className="animate-[reveal_400ms_ease-out]"
              style={{ animationFillMode: "backwards" }}
            >
              <div className="rounded-md border border-border bg-surface px-4 py-3">
                <StreamReveal
                  text={`${node.title ?? node.node_id} · ${node.status} · ${node.mastery_score}%`}
                />
              </div>
            </li>
          ))}
        </ol>
        <div ref={sentinelRef} />

        {done && (
          <div className="mt-10 space-y-4">
            <Link href="/roadmap">
              <Button data-testid="forge-to-roadmap">
                Explore vertical trail →
              </Button>
            </Link>

            <div
              className="rounded-md border border-border bg-surface px-4 py-3"
              data-testid="forge-resume-copy"
            >
              <p className="text-sm font-medium text-text-primary">
                Save a resume link
              </p>
              <p className="mt-1 text-sm text-text-secondary">
                Single-use · expires in ~7 days. Copy it now — you will not see
                this link again on this screen.
              </p>
              {resumeUrl ? (
                <div className="mt-3 flex flex-col gap-2 sm:flex-row sm:items-center">
                  <code className="block flex-1 truncate rounded bg-bg px-2 py-1 text-xs text-text-secondary">
                    {resumeUrl}
                  </code>
                  <Button
                    variant="ghost"
                    data-testid="forge-resume-copy-btn"
                    onClick={() => {
                      void navigator.clipboard.writeText(resumeUrl).then(() => {
                        setCopied(true);
                      });
                    }}
                  >
                    {copied ? "Copied" : "Copy resume link"}
                  </Button>
                </div>
              ) : (
                <p className="mt-2 text-sm text-text-secondary">
                  {resumeError ?? "Preparing resume link…"}
                </p>
              )}
            </div>

            <div
              className="rounded-md border border-border bg-surface px-4 py-3"
              data-testid="forge-email-store"
            >
              <p className="text-sm font-medium text-text-primary">
                Optional email (store only)
              </p>
              <p className="mt-1 text-sm text-text-secondary">
                Saved for a future resume delivery. We do not send email yet.
              </p>
              <div className="mt-3 flex flex-col gap-2 sm:flex-row sm:items-center">
                <input
                  type="email"
                  className="min-w-0 flex-1 rounded-md border border-border bg-bg px-3 py-2 text-sm text-text-primary"
                  placeholder="you@example.com"
                  value={email}
                  data-testid="forge-email-input"
                  onChange={(e) => {
                    setEmail(e.target.value);
                    if (emailStatus !== "idle") setEmailStatus("idle");
                  }}
                />
                <Button
                  variant="ghost"
                  data-testid="forge-email-save"
                  disabled={emailStatus === "saving"}
                  onClick={() => void handleSaveEmail()}
                >
                  {emailStatus === "saving"
                    ? "Saving…"
                    : emailStatus === "saved"
                      ? "Saved"
                      : "Save email"}
                </Button>
              </div>
              {emailError ? (
                <p className="mt-2 text-sm text-red-400" data-testid="forge-email-error">
                  {emailError}
                </p>
              ) : null}
            </div>
          </div>
        )}
      </div>
    </main>
  );
}
