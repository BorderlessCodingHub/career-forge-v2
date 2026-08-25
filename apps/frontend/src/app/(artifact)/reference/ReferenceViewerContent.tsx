"use client";

import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { useEffect, useMemo, useState } from "react";

import { Button } from "@/components/ui";
import { getRoadmap, patchRoadmapChecklist } from "@/lib/api-client";
import {
  buildReferenceViewerHref,
  resolveReferenceViewer,
} from "@/lib/reference-viewer";
import type { RoadmapResponse } from "@/types/contracts";

export default function ReferenceViewerContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const nodeId = searchParams.get("node");
  const itemId = searchParams.get("item");

  const [roadmap, setRoadmap] = useState<RoadmapResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [pending, setPending] = useState(false);
  const [error, setError] = useState<string | null>(null);

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

    void getRoadmap()
      .then((data) => {
        if (cancelled) return;
        if (!resolveReferenceViewer(data, nodeId, itemId)) {
          router.replace("/roadmap");
          return;
        }
        setRoadmap(data);
      })
      .catch((cause) => {
        if (!cancelled) {
          setError(cause instanceof Error ? cause.message : "Failed to load Reference");
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
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Failed to update Reference");
    } finally {
      setPending(false);
    }
  }

  if (loading || (!resolved && !error)) {
    return (
      <main className="min-h-screen px-4 py-20 text-center" data-screen="reference-viewer">
        <p className="text-sm text-text-muted animate-pulse">Loading Reference…</p>
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
            Reference unavailable
          </h1>
          <p className="mt-2 text-sm text-danger">{error}</p>
          <Link href={nodeId ? `/roadmap?node=${encodeURIComponent(nodeId)}` : "/roadmap"}>
            <Button className="mt-5">Return to roadmap</Button>
          </Link>
        </div>
      </main>
    );
  }

  const { node, reference, references } = resolved;

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
            ← Return to roadmap
          </Link>
          <p className="mt-4 text-xs uppercase tracking-widest text-text-muted">
            {node.title}
          </p>
          <h1 className="mt-1 text-2xl font-semibold text-text-primary">
            {reference.title ?? "Reference"}
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
          Mark as studied
        </label>
      </div>

      <div className="grid gap-4 lg:grid-cols-[minmax(0,1fr)_18rem]">
        <section className="overflow-hidden rounded-xl border border-border bg-surface">
          <div className="flex flex-wrap items-center justify-between gap-3 border-b border-border px-4 py-3">
            <p className="text-xs text-text-secondary">
              Preview availability depends on the source site.
            </p>
            <a
              href={reference.url}
              target="_blank"
              rel="noopener noreferrer"
              className="text-sm font-medium text-accent-mint hover:underline"
              data-testid="reference-escape-hatch"
            >
              Open on source site ↗
            </a>
          </div>
          <iframe
            key={reference.id}
            src={reference.url}
            title={reference.title ?? "Reference preview"}
            className="h-[70vh] min-h-[32rem] w-full bg-white"
            sandbox="allow-forms allow-popups allow-scripts"
            referrerPolicy="no-referrer"
            data-testid="reference-preview"
          />
        </section>

        <aside className="rounded-xl border border-border bg-surface p-4">
          <h2 className="text-xs font-semibold uppercase tracking-widest text-text-muted">
            More References in this Node
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
                        {candidate.title ?? "Reference"}
                      </span>
                      {candidate.done && (
                        <span className="mt-1 block text-xs text-accent-mint">
                          Studied
                        </span>
                      )}
                    </Link>
                  ) : (
                    <span className="block rounded-lg border border-border px-3 py-3 text-sm text-text-muted">
                      {candidate.title ?? "Reference"}
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
