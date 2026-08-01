"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

import { Button } from "@/components/ui";
import {
  absoluteAppUrl,
  getMyProfile,
  listForges,
  mintResumeLink,
  mintShareLink,
  openForge,
  revokeShareLink,
  startForgeRunFromProfile,
  updateForgeTitle,
} from "@/lib/api-client";
import { hydrateOnboardingFromProfile } from "@/lib/profile-reuse";
import { setForgeRunId } from "@/lib/forge-session";
import type { ForgeArtifactSummary } from "@/types/contracts";

export default function ForgesListPage() {
  const router = useRouter();
  const [items, setItems] = useState<ForgeArtifactSummary[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [busyId, setBusyId] = useState<string | null>(null);
  const [copied, setCopied] = useState<string | null>(null);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editTitle, setEditTitle] = useState("");
  const [hasDiagnosis, setHasDiagnosis] = useState(false);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const [res, profile] = await Promise.all([
          listForges(),
          getMyProfile().catch(() => null),
        ]);
        if (!cancelled) {
          setItems(res.items);
          setHasDiagnosis(Boolean(profile?.has_diagnosis));
        }
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

  async function handleRevoke(publicId: string) {
    setBusyId(`${publicId}-revoke`);
    setError(null);
    try {
      await revokeShareLink(publicId);
      setCopied(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to revoke share");
    } finally {
      setBusyId(null);
    }
  }

  async function handleSaveTitle(publicId: string) {
    const next = editTitle.trim();
    if (!next) {
      setError("Title must not be empty");
      return;
    }
    setBusyId(`${publicId}-title`);
    setError(null);
    try {
      const updated = await updateForgeTitle(publicId, next);
      setItems((prev) =>
        prev.map((item) => (item.public_id === publicId ? updated : item)),
      );
      setEditingId(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to rename forge");
    } finally {
      setBusyId(null);
    }
  }

  async function handleReforgeFromProfile() {
    setBusyId("reforge");
    setError(null);
    try {
      const profile = await getMyProfile();
      if (!profile.has_diagnosis || !profile.diagnosis) {
        setError("No saved diagnosis to reuse.");
        setBusyId(null);
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
      setBusyId(null);
      setError(
        err instanceof Error ? err.message : "Failed to start forge from profile",
      );
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
              Open a saved roadmap, rename it, or manage share / resume links.
            </p>
          </div>
          <Link href="/" className="text-sm text-accent">
            Home
          </Link>
        </div>

        {hasDiagnosis ? (
          <div className="rounded-md border border-border bg-surface px-4 py-3">
            <p className="text-sm text-text-secondary">
              Reuse your last diagnosis without re-interviewing.
            </p>
            <Button
              className="mt-2"
              variant="ghost"
              data-testid="forges-reforge-profile"
              disabled={busyId !== null}
              onClick={() => void handleReforgeFromProfile()}
            >
              Forge again from last diagnosis
            </Button>
          </div>
        ) : null}

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
                <div className="min-w-0 flex-1">
                  {editingId === item.public_id ? (
                    <div className="flex flex-wrap items-center gap-2">
                      <input
                        className="min-w-0 flex-1 rounded-md border border-border bg-bg px-2 py-1 text-sm text-text-primary"
                        value={editTitle}
                        data-testid={`forge-title-input-${item.public_id}`}
                        onChange={(e) => setEditTitle(e.target.value)}
                        maxLength={200}
                      />
                      <Button
                        data-testid={`forge-title-save-${item.public_id}`}
                        disabled={busyId !== null}
                        onClick={() => void handleSaveTitle(item.public_id)}
                      >
                        Save
                      </Button>
                      <Button
                        variant="ghost"
                        disabled={busyId !== null}
                        onClick={() => setEditingId(null)}
                      >
                        Cancel
                      </Button>
                    </div>
                  ) : (
                    <p className="font-medium text-text-primary">
                      {item.title}
                      {item.is_active ? (
                        <span className="ml-2 text-xs text-accent-mint">
                          active
                        </span>
                      ) : null}
                    </p>
                  )}
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
                  {editingId !== item.public_id ? (
                    <Button
                      variant="ghost"
                      data-testid={`forge-rename-${item.public_id}`}
                      disabled={busyId !== null}
                      onClick={() => {
                        setEditingId(item.public_id);
                        setEditTitle(item.title);
                      }}
                    >
                      Rename
                    </Button>
                  ) : null}
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
                    data-testid={`forge-revoke-${item.public_id}`}
                    disabled={busyId !== null}
                    onClick={() => void handleRevoke(item.public_id)}
                  >
                    Revoke share
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
