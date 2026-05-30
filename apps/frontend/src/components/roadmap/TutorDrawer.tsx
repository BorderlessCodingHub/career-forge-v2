"use client";

import { useCallback, useEffect, useState } from "react";

import { Button } from "@/components/ui";
import { getTutorContext, sendTutorMessage } from "@/lib/api-client";
import type { RoadmapNode, TutorContext, TutorMessage } from "@/types/contracts";

type TutorDrawerProps = {
  open: boolean;
  onClose: () => void;
  node?: RoadmapNode | null;
};

export function TutorDrawer({ open, onClose, node }: TutorDrawerProps) {
  const [messages, setMessages] = useState<TutorMessage[]>([]);
  const [draft, setDraft] = useState("");
  const [context, setContext] = useState<TutorContext | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!open || !node) return;
    setMessages([]);
    void getTutorContext(node.node_id, node.title)
      .then(setContext)
      .catch(() => setContext(null));
  }, [open, node?.node_id, node?.title]);

  const send = useCallback(async () => {
    const text = draft.trim();
    if (!text || loading) return;

    const userMessage: TutorMessage = { role: "user", content: text };
    const nextHistory = [...messages, userMessage];
    setMessages(nextHistory);
    setDraft("");
    setLoading(true);
    setError(null);

    try {
      const response = await sendTutorMessage({
        message: text,
        node_id: node?.node_id,
        node_title: node?.title,
        history: nextHistory.slice(0, -1),
      });
      setContext(response.tutor.context);
      setMessages((current) => [
        ...current,
        { role: "assistant", content: response.tutor.reply },
      ]);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Falha ao falar com o tutor");
      setMessages((current) => current.slice(0, -1));
    } finally {
      setLoading(false);
    }
  }, [draft, loading, messages, node?.node_id, node?.title]);

  if (!open) return null;

  return (
    <>
      <button
        type="button"
        aria-label="Fechar tutor"
        className="fixed inset-0 z-40 bg-black/40"
        onClick={onClose}
        data-testid="tutor-drawer-backdrop"
      />
      <aside
        className="fixed right-0 top-0 z-50 flex h-full w-full max-w-md flex-col border-l border-border bg-surface-elevated shadow-xl"
        data-testid="tutor-drawer"
      >
        <div className="flex items-center justify-between border-b border-border px-6 py-5">
          <div>
            <p className="text-sm font-semibold text-text-primary">Tutor do capítulo</p>
            <p className="text-xs text-accent-mint">
              foco em {node?.title ?? "este capítulo"}
            </p>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="rounded-md px-2 py-1 text-text-muted hover:bg-surface hover:text-text-primary"
          >
            ✕
          </button>
        </div>

        {context && context.key_concepts.length > 0 && (
          <div className="border-b border-border bg-surface px-6 py-3 text-xs text-text-secondary">
            <span className="text-text-muted">Conceitos: </span>
            {context.key_concepts.slice(0, 4).join(" · ")}
            {context.open_gaps.length > 0 && (
              <span className="ml-1 text-warning">· foco: {context.open_gaps[0]}</span>
            )}
          </div>
        )}

        <div className="flex-1 space-y-3 overflow-y-auto px-5 py-5" data-testid="tutor-messages">
          {messages.length === 0 && (
            <p className="rounded-md border border-border bg-surface px-4 py-3 text-sm text-text-secondary">
              Tire dúvidas técnicas sobre {node?.title ?? "este capítulo"}. O tutor responde
              ancorado nos conceitos-chave, nas referências e nas suas lacunas.
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
            <p className="text-sm text-text-muted animate-pulse">Tutor pensando…</p>
          )}
        </div>

        {error && <p className="px-5 pb-2 text-sm text-danger">{error}</p>}

        <div className="border-t border-border px-5 py-4">
          <div className="flex gap-2">
            <input
              value={draft}
              onChange={(event) => setDraft(event.target.value)}
              onKeyDown={(event) => {
                if (event.key === "Enter") void send();
              }}
              placeholder="Pergunte sobre o conteúdo deste capítulo..."
              className="flex-1 rounded-md border border-border bg-surface px-3 py-2 text-sm text-text-primary placeholder:text-text-muted"
              data-testid="tutor-input"
            />
            <Button
              onClick={() => void send()}
              disabled={!draft.trim() || loading}
              data-testid="tutor-send"
            >
              Enviar
            </Button>
          </div>
        </div>
      </aside>
    </>
  );
}
