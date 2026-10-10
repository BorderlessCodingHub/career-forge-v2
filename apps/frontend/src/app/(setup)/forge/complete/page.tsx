"use client";

import { useTranslations } from "next-intl";
import Link from "next/link";
import { useEffect, useRef, useState } from "react";

import { ProductEntryGate } from "@/components/auth";
import { StreamReveal } from "@/components/forge";
import { Button } from "@/components/ui";
import {
  absoluteAppUrl,
  emailResumeLink,
  getRoadmap,
  listForges,
  mintResumeLink,
} from "@/lib/api-client";
import { getForgeGraph, setForgeGraph, type ForgeGraphNode } from "@/lib/forge-session";

function ForgeCompleteContent() {
  const t = useTranslations("forge");
  const [graph, setGraph] = useState<ForgeGraphNode[] | null>(null);
  const [graphChecked, setGraphChecked] = useState(false);
  const [revealed, setRevealed] = useState(0);
  const [resumeUrl, setResumeUrl] = useState<string | null>(null);
  const [resumeError, setResumeError] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);
  const [emailSent, setEmailSent] = useState(false);
  const [emailSendBusy, setEmailSendBusy] = useState(false);
  const [emailSendError, setEmailSendError] = useState<string | null>(null);
  const [resumePublicId, setResumePublicId] = useState<string | null>(null);
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
    const loaded = getForgeGraph();
    if (loaded?.length) {
      setGraph(loaded);
      setGraphChecked(true);
      return;
    }
    let cancelled = false;
    void getRoadmap()
      .then((roadmap) => {
        if (cancelled) return;
        const nodes: ForgeGraphNode[] = roadmap.nodes.map((node) => ({
          node_id: node.node_id,
          title: node.title,
          status: node.status,
          mastery_score: node.mastery_score,
          priority: node.priority,
          rationale: node.rationale,
          prerequisites: node.prerequisites,
        }));
        if (nodes.length) {
          setForgeGraph(nodes);
          setGraph(nodes);
        } else {
          setGraph(null);
        }
      })
      .catch(() => {
        if (!cancelled) setGraph(null);
      })
      .finally(() => {
        if (!cancelled) setGraphChecked(true);
      });
    return () => {
      cancelled = true;
    };
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
            setResumeError(t("resumeUnavailable"));
          }
          return;
        }
        const minted = await mintResumeLink(target.public_id);
        if (!cancelled) {
          setResumePublicId(target.public_id);
          setResumeUrl(absoluteAppUrl(minted.path));
        }
      } catch (err) {
        if (!cancelled) {
          setResumeError(
            err instanceof Error ? err.message : t("mintFailed"),
          );
        }
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [graph, t]);

  if (!graphChecked) {
    return (
      <main className="min-h-screen grid-dots p-8">
        <p className="text-text-secondary">{t("loadingTrail")}</p>
      </main>
    );
  }

  if (!graph?.length) {
    return (
      <main className="min-h-screen grid-dots p-8">
        <p className="text-text-secondary">{t("noGraph")}</p>
        <Link href="/forge" className="mt-4 inline-block text-accent">
          {t("backToForge")}
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
          {t("revealTitle")}
        </h1>
        <p className="mt-2 text-text-secondary">{t("revealLead")}</p>

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
                {t("exploreTrail")}
              </Button>
            </Link>

            <div
              className="rounded-md border border-border bg-surface px-4 py-3"
              data-testid="forge-resume-copy"
            >
              <p className="text-sm font-medium text-text-primary">
                {t("saveResume")}
              </p>
              <p className="mt-1 text-sm text-text-secondary">{t("resumeHint")}</p>
              {resumeUrl ? (
                <div className="mt-3 space-y-2">
                  <div className="flex flex-col gap-2 sm:flex-row sm:items-center">
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
                      {copied ? t("copied") : t("copyResume")}
                    </Button>
                  </div>
                  {resumePublicId ? (
                    <div className="space-y-1">
                      <Button
                        variant="ghost"
                        data-testid="forge-resume-email-btn"
                        disabled={emailSendBusy || emailSent}
                        onClick={() => {
                          void (async () => {
                            setEmailSendBusy(true);
                            setEmailSendError(null);
                            try {
                              const res = await emailResumeLink(resumePublicId);
                              setEmailSent(true);
                              setResumeUrl(absoluteAppUrl(res.path));
                            } catch (err) {
                              setEmailSendError(
                                err instanceof Error
                                  ? err.message
                                  : t("emailFailed"),
                              );
                            } finally {
                              setEmailSendBusy(false);
                            }
                          })();
                        }}
                      >
                        {emailSent
                          ? t("emailSent")
                          : emailSendBusy
                            ? t("sending")
                            : t("emailLink")}
                      </Button>
                      {emailSendError ? (
                        <p
                          className="text-sm text-red-400"
                          data-testid="forge-resume-email-error"
                        >
                          {emailSendError}
                        </p>
                      ) : null}
                    </div>
                  ) : null}
                </div>
              ) : (
                <p className="mt-2 text-sm text-text-secondary">
                  {resumeError ?? t("preparingResume")}
                </p>
              )}
            </div>
          </div>
        )}
      </div>
    </main>
  );
}

export default function ForgeCompletePage() {
  return (
    <ProductEntryGate>
      <ForgeCompleteContent />
    </ProductEntryGate>
  );
}
