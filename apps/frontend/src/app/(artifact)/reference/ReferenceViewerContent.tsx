"use client";

import { ExternalLink, Link2 } from "lucide-react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { useTranslations } from "next-intl";
import { useEffect, useMemo, useState } from "react";

import {
  getReferenceEmbedHosts,
  getRoadmap,
  patchRoadmapChecklist,
  recordRoadmapPresence,
} from "@/lib/api-client";
import {
  buildReferenceViewerHref,
  getReferenceHostname,
  isEmbeddableReferenceUrl,
  REFERENCE_PREVIEW_REFERRER_POLICY,
  REFERENCE_PREVIEW_SANDBOX,
  resolveReferenceViewer,
} from "@/lib/reference-viewer";
import type { RoadmapResponse } from "@/types/contracts";

export default function ReferenceViewerContent() {
  const t = useTranslations("reference");
  const router = useRouter();
  const searchParams = useSearchParams();
  const nodeId = searchParams.get("node");
  const itemId = searchParams.get("item");

  const [roadmap, setRoadmap] = useState<RoadmapResponse | null>(null);
  const [allowedDomains, setAllowedDomains] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);
  const [pending, setPending] = useState(false);
  const [error, setError] = useState<"load" | "update" | null>(null);

  const resolved = useMemo(
    () => (roadmap ? resolveReferenceViewer(roadmap, nodeId, itemId) : null),
    [itemId, nodeId, roadmap],
  );

  useEffect(() => {
    if (!nodeId || !itemId) {
      router.replace("/roadmap");
      return;
    }

    let cancelled = false;
    setLoading(true);
    setError(null);

    void Promise.all([
      getRoadmap(),
      getReferenceEmbedHosts().catch(() => []),
    ])
      .then(([data, liveAllowedDomains]) => {
        if (cancelled) return;
        if (!resolveReferenceViewer(data, nodeId, itemId)) {
          router.replace("/roadmap");
          return;
        }
        setRoadmap(data);
        setAllowedDomains(liveAllowedDomains);
        void recordRoadmapPresence();
      })
      .catch(() => {
        if (!cancelled) {
          setError("load");
        }
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, [itemId, nodeId, router]);

  async function toggleDone(done: boolean) {
    if (!resolved) return;
    setPending(true);
    setError(null);
    try {
      const updated = await patchRoadmapChecklist(resolved.node.node_id, {
        item_type: "reference",
        item_id: resolved.reference.id,
        done,
      });
      setRoadmap(updated);
    } catch {
      setError("update");
    } finally {
      setPending(false);
    }
  }

  if (loading || (!resolved && !error)) {
    return (
      <main className="min-h-screen px-4 py-20 text-center" data-screen="reference-viewer">
        <p className="text-sm text-text-muted animate-pulse">{t("loading")}</p>
      </main>
    );
  }

  if (error || !resolved) {
    return (
      <main
        className="mx-auto min-h-screen max-w-3xl px-4 py-16"
        data-screen="reference-viewer"
      >
        <div className="rounded-xl border border-danger/30 bg-danger/10 p-6">
          <h1 className="text-lg font-semibold text-text-primary">
            {t("unavailable")}
          </h1>
          <p className="mt-2 text-sm text-danger">
            {error === "load"
              ? t("failedToLoad")
              : error === "update"
                ? t("failedToUpdate")
                : null}
          </p>
          <Link
            href={nodeId ? `/roadmap?node=${encodeURIComponent(nodeId)}` : "/roadmap"}
            className="mt-5 inline-flex rounded-md bg-accent px-4 py-2 text-sm font-medium text-white transition hover:opacity-90"
          >
            {t("returnToRoadmapAction")}
          </Link>
        </div>
      </main>
    );
  }

  const { node, reference, references } = resolved;
  const canEmbed = isEmbeddableReferenceUrl(reference.url, allowedDomains);
  const sourceHostname = getReferenceHostname(reference.url);
  const cardBody =
    reference.outcome?.trim() || t("previewUnavailable");

  return (
    <main
      className="mx-auto min-h-screen max-w-7xl px-4 py-6 sm:px-6"
      data-screen="reference-viewer"
      data-testid="reference-viewer"
    >
      <div className="mb-4 flex flex-wrap items-start justify-between gap-4">
        <div>
          <Link
            href={`/roadmap?node=${encodeURIComponent(node.node_id)}`}
            className="text-xs font-semibold uppercase tracking-widest text-accent-mint hover:underline"
            data-testid="reference-return-to-node"
          >
            {t("returnToRoadmap")}
          </Link>
          <p className="mt-4 text-xs uppercase tracking-widest text-text-muted">
            {node.title}
          </p>
          <h1 className="mt-1 text-2xl font-semibold text-text-primary">
            {reference.title ?? t("fallbackTitle")}
          </h1>
        </div>

        <label className="flex cursor-pointer items-center gap-3 rounded-lg border border-border bg-surface px-4 py-3 text-sm text-text-primary">
          <input
            type="checkbox"
            className="h-4 w-4 rounded border-border accent-accent-mint"
            checked={reference.done}
            disabled={pending}
            onChange={(event) => void toggleDone(event.target.checked)}
            data-testid={`reference-viewer-done-${reference.id}`}
          />
          {t("markStudied")}
        </label>
      </div>

      <div className="grid gap-4 lg:grid-cols-[minmax(0,1fr)_18rem]">
        <section className="overflow-hidden rounded-xl border border-border bg-surface">
          {canEmbed ? (
            <>
              <div className="flex flex-wrap items-center justify-between gap-3 border-b border-border px-4 py-3">
                <p className="text-xs text-text-secondary">
                  {t("previewBySource")}
                </p>
                <a
                  href={reference.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-sm font-medium text-accent-mint hover:underline"
                  data-testid="reference-escape-hatch"
                >
                  {t("openOriginal")}
                </a>
              </div>
              <iframe
                key={reference.id}
                src={reference.url}
                title={reference.title ?? t("previewTitle")}
                className="h-[70vh] min-h-[32rem] w-full bg-white"
                sandbox={REFERENCE_PREVIEW_SANDBOX}
                referrerPolicy={REFERENCE_PREVIEW_REFERRER_POLICY}
                data-testid="reference-preview"
              />
            </>
          ) : (
            <div
              className="grid min-h-[32rem] place-items-center bg-bg p-6 sm:p-10"
              data-testid="reference-source-card"
            >
              <article className="w-full max-w-xl rounded-xl border border-border bg-surface-elevated p-6 shadow-[0_20px_60px_rgba(0,0,0,0.2)] sm:p-8">
                <div className="flex h-11 w-11 items-center justify-center rounded-lg border border-accent-mint/30 bg-accent-mint/10 text-accent-mint">
                  <Link2 aria-hidden="true" className="h-5 w-5" />
                </div>
                <h2 className="mt-5 text-xl font-semibold text-text-primary">
                  {reference.title ?? t("fallbackTitle")}
                </h2>
                <p
                  className="mt-2 text-sm text-text-muted"
                  data-testid="reference-source-host"
                >
                  {t("source", { host: sourceHostname ?? "" })}
                </p>
                <div className="my-6 h-px bg-border" />
                <p className="text-sm leading-7 text-text-secondary">{cardBody}</p>
                <a
                  href={reference.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="mt-7 inline-flex items-center gap-2 rounded-md bg-accent px-4 py-2.5 text-sm font-semibold text-white transition hover:opacity-90 focus:outline-none focus:ring-2 focus:ring-accent-mint"
                  data-testid="reference-escape-hatch"
                >
                  {t("openOriginalPlain")}
                  <ExternalLink aria-hidden="true" className="h-4 w-4" />
                </a>
              </article>
            </div>
          )}
        </section>

        <aside className="rounded-xl border border-border bg-surface p-4">
          <h2 className="text-xs font-semibold uppercase tracking-widest text-text-muted">
            {t("moreInNode")}
          </h2>
          <ul className="mt-3 space-y-2">
            {references.map((candidate) => {
              const active = candidate.id === reference.id;
              return (
                <li key={candidate.id}>
                  {candidate.url ? (
                    <Link
                      href={buildReferenceViewerHref(node.node_id, candidate.id)}
                      aria-current={active ? "page" : undefined}
                      className={`block rounded-lg border px-3 py-3 text-sm transition ${
                        active
                          ? "border-accent bg-accent/10 text-text-primary"
                          : "border-border text-text-secondary hover:border-accent/60 hover:text-text-primary"
                      }`}
                      data-testid={`reference-sibling-${candidate.id}`}
                    >
                      <span className="font-medium">
                        {candidate.title ?? t("fallbackTitle")}
                      </span>
                      {candidate.done && (
                        <span className="mt-1 block text-xs text-accent-mint">
                          {t("studied")}
                        </span>
                      )}
                    </Link>
                  ) : (
                    <span className="block rounded-lg border border-border px-3 py-3 text-sm text-text-muted">
                      {candidate.title ?? t("fallbackTitle")}
                    </span>
                  )}
                </li>
              );
            })}
          </ul>
        </aside>
      </div>
    </main>
  );
}
