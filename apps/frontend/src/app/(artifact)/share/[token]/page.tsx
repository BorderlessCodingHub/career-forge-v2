"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useEffect, useState } from "react";

import { fetchSharedForge } from "@/lib/api-client";
import type { RoadmapResponse } from "@/types/contracts";

export default function ShareForgePage() {
  const params = useParams<{ token: string }>();
  const token = params.token;
  const [roadmap, setRoadmap] = useState<RoadmapResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!token) return;
    let cancelled = false;
    (async () => {
      try {
        const data = await fetchSharedForge(token);
        if (!cancelled) setRoadmap(data);
      } catch (err) {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : "Share link unavailable");
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [token]);

  return (
    <main
      className="min-h-screen grid-dots px-4 py-10"
      data-screen="share-readonly"
    >
      <div className="mx-auto max-w-2xl space-y-6">
        <div>
          <p className="text-sm text-text-secondary">Shared roadmap · read-only</p>
          <h1 className="mt-1 text-3xl font-semibold text-text-primary">
            {roadmap?.track.title ?? "Shared forge"}
          </h1>
          <p className="mt-2 text-text-secondary">
            This view does not adopt the owner session. Start your own forge from
            home.
          </p>
        </div>

        {loading ? <p className="text-text-secondary">Loading…</p> : null}
        {error ? (
          <p className="text-sm text-red-400" data-testid="share-error">
            {error}
          </p>
        ) : null}

        {roadmap ? (
          <ol className="space-y-3" data-testid="share-node-list">
            {roadmap.nodes.map((node) => (
              <li
                key={node.node_id}
                className="rounded-md border border-border bg-surface px-4 py-3"
              >
                <p className="font-medium text-text-primary">{node.title}</p>
                <p className="mt-1 text-sm text-text-secondary">
                  {node.status} · {node.mastery_score}%
                </p>
                {node.rationale ? (
                  <p className="mt-2 text-sm text-text-secondary">{node.rationale}</p>
                ) : null}
              </li>
            ))}
          </ol>
        ) : null}

        <Link href="/" className="inline-block text-sm text-accent">
          Go to Career Forge home
        </Link>
      </div>
    </main>
  );
}
