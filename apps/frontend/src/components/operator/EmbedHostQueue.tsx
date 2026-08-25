"use client";

import { useCallback, useEffect, useState } from "react";

import {
  addOperatorEmbedHost,
  getOperatorEmbedHosts,
  removeOperatorEmbedHost,
  type OperatorEmbedHostQueue,
  type OperatorPendingEmbedHost,
} from "@/lib/operator-console";
import {
  REFERENCE_PREVIEW_REFERRER_POLICY,
  REFERENCE_PREVIEW_SANDBOX,
} from "@/lib/reference-viewer";

const EMPTY_QUEUE: OperatorEmbedHostQueue = { pending: [], liberated: [] };

export function EmbedHostQueue() {
  const [queue, setQueue] = useState<OperatorEmbedHostQueue>(EMPTY_QUEUE);
  const [preview, setPreview] = useState<OperatorPendingEmbedHost | null>(null);
  const [previewLoaded, setPreviewLoaded] = useState(false);
  const [previewConfirmed, setPreviewConfirmed] = useState(false);
  const [busyHost, setBusyHost] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadQueue = useCallback(async () => {
    const next = await getOperatorEmbedHosts();
    setQueue(next);
    setPreview(null);
    setPreviewLoaded(false);
    setPreviewConfirmed(false);
  }, []);

  useEffect(() => {
    loadQueue()
      .catch((cause) =>
        setError(cause instanceof Error ? cause.message : "Could not load embed queue."),
      )
      .finally(() => setLoading(false));
  }, [loadQueue]);

  async function liberate(host: string) {
    if (!previewLoaded || !previewConfirmed || preview?.host !== host) return;
    setBusyHost(host);
    setError(null);
    try {
      await addOperatorEmbedHost(host);
      await loadQueue();
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Could not liberate this host.");
    } finally {
      setBusyHost(null);
    }
  }

  async function revoke(host: string) {
    setBusyHost(host);
    setError(null);
    try {
      await removeOperatorEmbedHost(host);
      await loadQueue();
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Could not revoke this host.");
    } finally {
      setBusyHost(null);
    }
  }

  return (
    <section className="mt-8 border-t border-border pt-8" data-testid="operator-embed-queue">
      <p className="font-mono text-xs uppercase tracking-[0.18em] text-accent-mint">
        Reference embed proof
      </p>
      <h3 className="mt-2 text-xl font-semibold text-text-primary">Live host queue</h3>
      <p className="mt-2 max-w-2xl text-sm leading-6 text-text-secondary">
        Preview a source learners actually received. Liberate its hostname only after
        verifying the page in the sandboxed frame.
      </p>

      {error ? (
        <p className="mt-4 text-sm text-red-300" role="alert">
          {error}
        </p>
      ) : null}

      {loading ? (
        <div className="mt-5 h-24 animate-pulse rounded-card border border-border bg-surface" />
      ) : (
        <div className="mt-5 grid gap-5 xl:grid-cols-2">
          <div>
            <h4 className="text-sm font-semibold text-text-primary">Pending</h4>
            <ul className="mt-2 space-y-2" data-testid="operator-embed-pending">
              {queue.pending.map((item) => (
                <li
                  key={item.host}
                  className="rounded-lg border border-border bg-surface p-3"
                >
                  <p className="font-mono text-sm text-text-primary">{item.host}</p>
                  <p className="mt-1 truncate text-xs text-text-muted">
                    {item.distinct_url_count} distinct URL
                    {item.distinct_url_count === 1 ? "" : "s"} · {item.sample_url}
                  </p>
                  <div className="mt-3 flex gap-2">
                    <button
                      type="button"
                      className="rounded-md border border-border px-3 py-1.5 text-xs text-text-secondary hover:border-accent-mint"
                      data-testid={`operator-embed-preview-${item.host}`}
                      onClick={() => {
                        setPreview(item);
                        setPreviewLoaded(false);
                        setPreviewConfirmed(false);
                      }}
                    >
                      Preview sample
                    </button>
                    <button
                      type="button"
                      disabled={
                        busyHost === item.host ||
                        !previewLoaded ||
                        !previewConfirmed ||
                        preview?.host !== item.host
                      }
                      className="rounded-md bg-accent px-3 py-1.5 text-xs font-semibold text-white disabled:cursor-not-allowed disabled:opacity-40"
                      data-testid={`operator-embed-liberate-${item.host}`}
                      onClick={() => void liberate(item.host)}
                    >
                      Liberate
                    </button>
                  </div>
                </li>
              ))}
              {queue.pending.length === 0 ? (
                <li className="text-sm text-text-muted">No pending learner hosts.</li>
              ) : null}
            </ul>
          </div>

          <div>
            <h4 className="text-sm font-semibold text-text-primary">Liberated</h4>
            <ul className="mt-2 space-y-2" data-testid="operator-embed-liberated">
              {queue.liberated.map((item) => (
                <li
                  key={item.host}
                  className="flex items-center justify-between gap-3 rounded-lg border border-border bg-surface p-3"
                >
                  <span className="font-mono text-sm text-text-primary">{item.host}</span>
                  <button
                    type="button"
                    disabled={busyHost === item.host}
                    className="rounded-md border border-red-900 px-3 py-1.5 text-xs text-red-300 disabled:opacity-40"
                    data-testid={`operator-embed-revoke-${item.host}`}
                    onClick={() => void revoke(item.host)}
                  >
                    Revoke
                  </button>
                </li>
              ))}
              {queue.liberated.length === 0 ? (
                <li className="text-sm text-text-muted">No liberated hosts.</li>
              ) : null}
            </ul>
          </div>
        </div>
      )}

      {preview ? (
        <div className="mt-5 overflow-hidden rounded-xl border border-border bg-surface">
          <div className="border-b border-border px-4 py-3">
            <p className="font-mono text-xs text-text-secondary">{preview.sample_url}</p>
          </div>
          <iframe
            key={preview.sample_url}
            src={preview.sample_url}
            title={`Embed proof for ${preview.host}`}
            className="h-[60vh] min-h-[28rem] w-full bg-white"
            sandbox={REFERENCE_PREVIEW_SANDBOX}
            referrerPolicy={REFERENCE_PREVIEW_REFERRER_POLICY}
            data-testid="operator-embed-preview-frame"
            onLoad={() => setPreviewLoaded(true)}
          />
          <label className="flex items-center gap-2 border-t border-border px-4 py-3 text-sm text-text-secondary">
            <input
              type="checkbox"
              checked={previewConfirmed}
              disabled={!previewLoaded}
              className="h-4 w-4 accent-accent-mint"
              data-testid="operator-embed-preview-confirmed"
              onChange={(event) => setPreviewConfirmed(event.target.checked)}
            />
            I verified that the sample page is visible in this preview.
          </label>
        </div>
      ) : null}
    </section>
  );
}
