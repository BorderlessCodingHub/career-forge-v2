"use client";

import { useEffect, useState } from "react";

import {
  getOperatorFeedbackNotes,
  setOperatorFeedbackReplied,
  type OperatorFeedbackNote,
} from "@/lib/operator-console";

function formatWrittenAt(value: string): string {
  return `${new Date(value).toLocaleString("en-GB", {
    dateStyle: "medium",
    timeStyle: "short",
    timeZone: "UTC",
  })} UTC`;
}

export function FeedbackNotes() {
  const [notes, setNotes] = useState<OperatorFeedbackNote[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [savingId, setSavingId] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    void getOperatorFeedbackNotes()
      .then((rows) => {
        if (!cancelled) setNotes(rows);
      })
      .catch(() => {
        if (!cancelled) setError("Product notes could not be loaded.");
      });
    return () => {
      cancelled = true;
    };
  }, []);

  async function toggle(note: OperatorFeedbackNote, replied: boolean) {
    setSavingId(note.id);
    setError(null);
    try {
      const updated = await setOperatorFeedbackReplied(note.id, replied);
      setNotes((current) =>
        (current ?? []).map((row) => (row.id === updated.id ? updated : row)),
      );
    } catch {
      setError("The replied mark was not saved.");
    } finally {
      setSavingId(null);
    }
  }

  return (
    <section data-testid="operator-feedback-notes" aria-label="Product notes">
      <h3 className="text-sm font-medium text-text-primary">Product notes</h3>
      <p className="mt-1 max-w-2xl text-xs leading-5 text-text-muted">
        Reply from your own mail. The reply says the note was read. It promises no fix,
        refund, rerun, or product change.
      </p>
      {error ? (
        <p className="mt-3 text-sm text-warning" role="alert" data-testid="operator-feedback-error">
          {error}
        </p>
      ) : null}
      {notes === null ? (
        <p className="mt-3 text-sm text-text-muted">Loading product notes…</p>
      ) : notes.length === 0 ? (
        <p className="mt-3 text-sm text-text-muted" data-testid="operator-feedback-empty">
          No product notes.
        </p>
      ) : (
        <ul className="mt-3 max-w-4xl divide-y divide-border rounded-card border border-border">
          {notes.map((note) => (
            <li key={note.id} className="px-4 py-3" data-testid="operator-feedback-note">
              <p className="whitespace-pre-wrap text-sm text-text-primary">{note.message}</p>
              <p className="mt-2 text-xs text-text-secondary">
                {note.email} · {formatWrittenAt(note.created_at)}
                {note.path ? ` · ${note.path}` : ""}
              </p>
              <label className="mt-2 inline-flex items-center gap-2 text-xs text-text-secondary">
                <input
                  type="checkbox"
                  checked={note.replied_at !== null}
                  disabled={savingId === note.id}
                  data-testid={`operator-feedback-replied-${note.id}`}
                  onChange={(event) => void toggle(note, event.target.checked)}
                />
                Replied
              </label>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}
