"use client";

import { useTranslations } from "next-intl";
import { useCallback, useEffect, useState } from "react";

import { Button } from "@/components/ui";
import { MentorAvatar } from "@/components/ui/MentorAvatar";
import { getMentorContext, sendMentorMessage } from "@/lib/api-client";
import type { MentorContextSnapshot, MentorMessage, RoadmapNode } from "@/types/contracts";

type MentorDrawerProps = {
  open: boolean;
  onClose: () => void;
  node?: RoadmapNode | null;
};

export function MentorDrawer({ open, onClose, node }: MentorDrawerProps) {
  const t = useTranslations("mentor");
  const [messages, setMessages] = useState<MentorMessage[]>([]);
  const [draft, setDraft] = useState("");
  const [context, setContext] = useState<MentorContextSnapshot | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!open) return;
    void getMentorContext(node?.node_id)
      .then(setContext)
      .catch(() => setContext(null));
  }, [open, node?.node_id]);

  const send = useCallback(async () => {
    const text = draft.trim();
    if (!text || loading) return;

    const userMessage: MentorMessage = { role: "user", content: text };
    const nextHistory = [...messages, userMessage];
    setMessages(nextHistory);
    setDraft("");
    setLoading(true);
    setError(null);

    try {
      const response = await sendMentorMessage({
        message: text,
        node_id: node?.node_id,
        node_title: node?.title,
        history: nextHistory.slice(0, -1),
      });
      setContext(response.mentor.context_snapshot);
      setMessages((current) => [
        ...current,
        { role: "assistant", content: response.mentor.reply },
      ]);
    } catch (err) {
      setError(err instanceof Error ? err.message : t("failed"));
      setMessages((current) => current.slice(0, -1));
    } finally {
      setLoading(false);
    }
  }, [draft, loading, messages, node?.node_id, node?.title, t]);

  if (!open) return null;

  return (
    <>
      <button
        type="button"
        aria-label={t("close")}
        className="fixed inset-0 z-40 bg-black/40"
        onClick={onClose}
        data-testid="mentor-drawer-backdrop"
      />
      <aside
        className="fixed right-0 top-0 z-50 flex h-full w-full max-w-md flex-col border-l border-border bg-surface-elevated shadow-xl"
        data-testid="mentor-drawer"
      >
        <div className="flex items-center justify-between border-b border-border px-6 py-5">
          <div className="flex items-center gap-3">
            <MentorAvatar className="h-9 w-9 text-sm" />
            <div>
              <p className="text-sm font-semibold text-text-primary">{t("drawerTitle")}</p>
              <p className="text-xs text-accent-mint">
                {t("knowsTrail", { title: node?.title ?? t("overview") })}
              </p>
            </div>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="rounded-md px-2 py-1 text-text-muted hover:bg-surface hover:text-text-primary"
          >
            ✕
          </button>
        </div>

        {context && (
          <div className="border-b border-border bg-surface px-6 py-3 text-xs text-text-secondary">
            {context.validation_count > 0 && (
              <span>{t("validations", { count: context.validation_count })}</span>
            )}
            {context.recent_gaps.length > 0 ? (
              <span>{t("recentGap", { gap: context.recent_gaps[0] })}</span>
            ) : (
              <span>{t("noGaps")}</span>
            )}
          </div>
        )}

        <div className="flex-1 space-y-3 overflow-y-auto px-5 py-5" data-testid="mentor-messages">
          {messages.length === 0 && (
            <p className="rounded-md border border-border bg-surface px-4 py-3 text-sm text-text-secondary">
              {t("empty", { title: node?.title ?? t("yourTrail") })}
            </p>
          )}
          {messages.map((message, index) => (
            <div
              key={`${message.role}-${index}`}
              className={`max-w-[90%] rounded-md px-4 py-3 text-sm ${
                message.role === "user"
                  ? "ml-auto bg-accent/20 text-text-primary"
                  : "mr-auto border border-border bg-surface text-text-secondary"
              }`}
            >
              {message.content}
            </div>
          ))}
          {loading && (
            <p className="text-sm text-text-muted animate-pulse">{t("thinking")}</p>
          )}
        </div>

        {error && (
          <p className="px-5 pb-2 text-sm text-danger">{error}</p>
        )}

        <div className="border-t border-border px-5 py-4">
          <div className="flex gap-2">
            <input
              value={draft}
              onChange={(event) => setDraft(event.target.value)}
              onKeyDown={(event) => {
                if (event.key === "Enter") void send();
              }}
              placeholder={t("placeholder")}
              className="flex-1 rounded-md border border-border bg-surface px-3 py-2 text-sm text-text-primary placeholder:text-text-muted"
              data-testid="mentor-input"
            />
            <Button
              onClick={() => void send()}
              disabled={!draft.trim() || loading}
              data-testid="mentor-send"
            >
              {t("send")}
            </Button>
          </div>
        </div>
      </aside>
    </>
  );
}
