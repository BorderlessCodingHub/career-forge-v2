"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { MoreHorizontal } from "lucide-react";
import { useEffect, useId, useRef, useState } from "react";

import { Button } from "@/components/ui";
import { PaywallPanel } from "@/components/billing/PaywallPanel";
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
import { isPaywallError, type PaywallError } from "@/lib/paywall";
import type { ForgeArtifactSummary } from "@/types/contracts";

/** Mirrors backend `artifact_title()` — default titles count as untitled. */
function defaultArtifactTitle(goalId: string | null | undefined): string {
  return goalId ? `Roadmap · ${goalId}` : "Roadmap";
}

function isUntitledTitle(
  title: string,
  goalId: string | null | undefined,
): boolean {
  return title === defaultArtifactTitle(goalId);
}

function forgeDisplayTitle(item: ForgeArtifactSummary): string {
  if (isUntitledTitle(item.title, item.goal_id)) {
    return item.goal_id ?? "Roadmap";
  }
  return item.title;
}

function forgeMetaLine(item: ForgeArtifactSummary): string {
  const date = new Date(item.created_at).toLocaleString();
  if (isUntitledTitle(item.title, item.goal_id)) {
    return date;
  }
  return `${item.goal_id ?? "—"} · ${date}`;
}

type ForgeOverflowMenuProps = {
  publicId: string;
  open: boolean;
  onOpenChange: (open: boolean) => void;
  busy: boolean;
  copiedShare: boolean;
  copiedResume: boolean;
  onShare: () => void;
  onResume: () => void;
  onRevoke: () => void;
};

function ForgeOverflowMenu({
  publicId,
  open,
  onOpenChange,
  busy,
  copiedShare,
  copiedResume,
  onShare,
  onResume,
  onRevoke,
}: ForgeOverflowMenuProps) {
  const menuId = useId();
  const rootRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!open) return;

    function onPointerDown(event: MouseEvent) {
      if (!rootRef.current?.contains(event.target as Node)) {
        onOpenChange(false);
      }
    }

    function onKeyDown(event: KeyboardEvent) {
      if (event.key === "Escape") {
        onOpenChange(false);
      }
    }

    document.addEventListener("mousedown", onPointerDown);
    document.addEventListener("keydown", onKeyDown);
    return () => {
      document.removeEventListener("mousedown", onPointerDown);
      document.removeEventListener("keydown", onKeyDown);
    };
  }, [open, onOpenChange]);

  return (
    <div className="relative" ref={rootRef}>
      <Button
        type="button"
        variant="ghost"
        className="px-2"
        aria-expanded={open}
        aria-haspopup="menu"
        aria-controls={menuId}
        aria-label="More forge actions"
        data-testid={`forge-overflow-${publicId}`}
        disabled={busy}
        onClick={() => onOpenChange(!open)}
      >
        <MoreHorizontal className="h-4 w-4" aria-hidden />
      </Button>
      {open ? (
        <div
          id={menuId}
          role="menu"
          className="absolute right-0 z-20 mt-1 min-w-[11rem] rounded-md border border-border bg-surface py-1 shadow-lg"
        >
          <button
            type="button"
            role="menuitem"
            className="block w-full px-3 py-2 text-left text-sm text-text-secondary hover:bg-bg hover:text-text-primary disabled:opacity-45"
            data-testid={`forge-share-${publicId}`}
            disabled={busy}
            onClick={() => {
              onShare();
            }}
          >
            {copiedShare ? "Share copied" : "Copy share"}
          </button>
          <button
            type="button"
            role="menuitem"
            className="block w-full px-3 py-2 text-left text-sm text-text-secondary hover:bg-bg hover:text-text-primary disabled:opacity-45"
            data-testid={`forge-resume-${publicId}`}
            disabled={busy}
            onClick={() => {
              onResume();
            }}
          >
            {copiedResume ? "Resume copied" : "Copy resume"}
          </button>
          <button
            type="button"
            role="menuitem"
            className="block w-full px-3 py-2 text-left text-sm text-text-secondary hover:bg-bg hover:text-text-primary disabled:opacity-45"
            data-testid={`forge-revoke-${publicId}`}
            disabled={busy}
            onClick={() => {
              onRevoke();
              onOpenChange(false);
            }}
          >
            Revoke share
          </button>
        </div>
      ) : null}
    </div>
  );
}

export default function ForgesListPage() {
  const router = useRouter();
  const [items, setItems] = useState<ForgeArtifactSummary[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [paywall, setPaywall] = useState<PaywallError | null>(null);
  const [loading, setLoading] = useState(true);
  const [busyId, setBusyId] = useState<string | null>(null);
  const [copied, setCopied] = useState<string | null>(null);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editTitle, setEditTitle] = useState("");
  const [hasDiagnosis, setHasDiagnosis] = useState(false);
  const [menuOpenId, setMenuOpenId] = useState<string | null>(null);

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
    setMenuOpenId(null);
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
    setPaywall(null);
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
      if (isPaywallError(err)) {
        setPaywall(err);
        return;
      }
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
              Scan and open a saved roadmap. Rename anytime; share and resume
              live in the row menu.
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
        {paywall ? (
          <PaywallPanel checkoutAvailable={paywall.checkoutAvailable} />
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
              <div className="flex items-start justify-between gap-3">
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
                      <span className="truncate">{forgeDisplayTitle(item)}</span>
                      {item.is_active ? (
                        <span className="ml-2 align-middle text-xs font-medium text-accent-mint">
                          active
                        </span>
                      ) : null}
                    </p>
                  )}
                  <p className="mt-0.5 text-sm text-text-secondary">
                    {forgeMetaLine(item)}
                  </p>
                </div>
                <div className="flex shrink-0 items-center gap-2">
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
                        setMenuOpenId(null);
                        setEditingId(item.public_id);
                        setEditTitle(item.title);
                      }}
                    >
                      Rename
                    </Button>
                  ) : null}
                  {editingId !== item.public_id ? (
                    <ForgeOverflowMenu
                      publicId={item.public_id}
                      open={menuOpenId === item.public_id}
                      onOpenChange={(open) =>
                        setMenuOpenId(open ? item.public_id : null)
                      }
                      busy={busyId !== null}
                      copiedShare={copied === `${item.public_id}-share`}
                      copiedResume={copied === `${item.public_id}-resume`}
                      onShare={() => void copyLink(item.public_id, "share")}
                      onResume={() => void copyLink(item.public_id, "resume")}
                      onRevoke={() => void handleRevoke(item.public_id)}
                    />
                  ) : null}
                </div>
              </div>
            </li>
          ))}
        </ul>
      </div>
    </main>
  );
}
