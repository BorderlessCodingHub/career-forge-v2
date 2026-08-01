"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

import { Button } from "@/components/ui";
import {
  absoluteAppUrl,
  listForges,
  mintResumeLink,
  mintShareLink,
  openForge,
} from "@/lib/api-client";
import type { ForgeArtifactSummary } from "@/types/contracts";

export default function ForgesListPage() {
  const router = useRouter();
  const [items, setItems] = useState<ForgeArtifactSummary[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [busyId, setBusyId] = useState<string | null>(null);
  const [copied, setCopied] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const res = await listForges();
        if (!cancelled) setItems(res.items);
      } catch (err) {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : "Failed to load forges");
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, []);

  async function handleOpen(publicId: string) {
    setBusyId(publicId);
    setError(null);
    try {
      await openForge(publicId);
      router.push("/roadmap");
    } catch (err) {
      setBusyId(null);
      setError(err instanceof Error ? err.message : "Failed to open forge");
    }
  }

  async function copyLink(
    publicId: string,
    kind: "share" | "resume",
  ): Promise<void> {
    setBusyId(`${publicId}-${kind}`);
    setError(null);
    try {
      const minted =
        kind === "share"
          ? await mintShareLink(publicId)
          : await mintResumeLink(publicId);
      const url = absoluteAppUrl(minted.path);
      await navigator.clipboard.writeText(url);
      setCopied(`${publicId}-${kind}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to mint link");
    } finally {
      setBusyId(null);
    }
  }

  return (
    <main
      className="min-h-screen grid-dots px-4 py-10"
      data-screen="forges-list"
    >
      <div className="mx-auto max-w-2xl space-y-6">
        <div className="flex items-start justify-between gap-4">
          <div>
            <h1 className="text-3xl font-semibold text-text-primary">
              Your forges
            </h1>
            <p className="mt-2 text-text-secondary">
              Open a saved roadmap, or copy share / resume links.
            </p>
          </div>
          <Link href="/" className="text-sm text-accent">
            Home
          </Link>
        </div>

        {loading ? (
          <p className="text-text-secondary">Loading…</p>
        ) : null}
        {error ? (
          <p className="text-sm text-red-400" data-testid="forges-error">
            {error}
          </p>
        ) : null}
        {!loading && items.length === 0 ? (
          <p className="text-text-secondary">
            No forges yet.{" "}
            <Link href="/" className="text-accent">
              Start a new one
            </Link>
            .
          </p>
        ) : null}

        <ul className="space-y-3">
          {items.map((item) => (
            <li
              key={item.public_id}
              className="rounded-md border border-border bg-surface px-4 py-3"
              data-testid={`forge-row-${item.public_id}`}
            >
              <div className="flex flex-wrap items-start justify-between gap-3">
                <div>
                  <p className="font-medium text-text-primary">
                    {item.title}
                    {item.is_active ? (
                      <span className="ml-2 text-xs text-accent-mint">
                        active
                      </span>
                    ) : null}
                  </p>
                  <p className="mt-0.5 text-sm text-text-secondary">
                    {item.goal_id ?? "—"} ·{" "}
                    {new Date(item.created_at).toLocaleString()}
                  </p>
                </div>
                <div className="flex flex-wrap gap-2">
                  <Button
                    data-testid={`forge-open-${item.public_id}`}
                    disabled={busyId !== null}
                    onClick={() => void handleOpen(item.public_id)}
                  >
                    Open
                  </Button>
                  <Button
                    variant="ghost"
                    data-testid={`forge-share-${item.public_id}`}
                    disabled={busyId !== null}
                    onClick={() => void copyLink(item.public_id, "share")}
                  >
                    {copied === `${item.public_id}-share`
                      ? "Share copied"
                      : "Copy share"}
                  </Button>
                  <Button
                    variant="ghost"
                    data-testid={`forge-resume-${item.public_id}`}
                    disabled={busyId !== null}
                    onClick={() => void copyLink(item.public_id, "resume")}
                  >
                    {copied === `${item.public_id}-resume`
                      ? "Resume copied"
                      : "Copy resume"}
                  </Button>
                </div>
              </div>
            </li>
          ))}
        </ul>
      </div>
    </main>
  );
}
