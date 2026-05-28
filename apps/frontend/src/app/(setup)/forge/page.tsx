"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useCallback, useEffect, useRef, useState } from "react";

import { ForgeEventLine, ForgeTimeline } from "@/components/forge";
import { Button } from "@/components/ui";
import { startForgeRunFromProfile, streamForgeRun } from "@/lib/api-client";
import {
  extractGraphFromEvents,
  getForgeRunId,
  setForgeGraph,
  setForgeRunId,
  clearForgeSession,
} from "@/lib/forge-session";
import type { RoadmapForgeEvent } from "@/types/contracts";

export default function ForgePage() {
  const router = useRouter();
  const [events, setEvents] = useState<RoadmapForgeEvent[]>([]);
  const [status, setStatus] = useState<"idle" | "starting" | "streaming" | "done" | "error">(
    "idle",
  );
  const [error, setError] = useState<string | null>(null);
  const [elapsedSec, setElapsedSec] = useState(0);
  const startedRef = useRef(false);
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const finishForge = useCallback(
    (collected: RoadmapForgeEvent[]) => {
      const graph = extractGraphFromEvents(collected);
      if (graph) setForgeGraph(graph);
      setStatus("done");
      if (timerRef.current) clearInterval(timerRef.current);
    },
    [],
  );

  const connectStream = useCallback(
    async (runId: string) => {
      setStatus("streaming");

      const collected = await streamForgeRun(runId, {
        onEvent: (event) => {
          setEvents((previous) => [...previous, event]);
        },
        onComplete: (allEvents) => {
          finishForge(allEvents);
        },
        onError: (message) => {
          setError(message);
        },
      });

      if (collected.length > 0 && !collected.some((event) => event.type === "graph_ready")) {
        finishForge(collected);
      }
    },
    [finishForge],
  );

  const startForge = useCallback(async (forceNewRun = false) => {
    setStatus("starting");
    setError(null);
    setEvents([]);
    timerRef.current = setInterval(() => setElapsedSec((s) => s + 1), 1000);

    try {
      const existingRunId = forceNewRun ? null : getForgeRunId();
      const runId = existingRunId
        ? existingRunId
        : (await startForgeRunFromProfile()).run_id;

      if (!existingRunId) {
        setForgeRunId(runId);
      }

      await connectStream(runId);
    } catch (err) {
      const message =
        err instanceof Error ? err.message : "Falha ao iniciar forge";
      if (message.includes("404")) {
        router.replace("/onboarding/edit");
        return;
      }
      setError(message);
      setStatus("error");
      if (timerRef.current) clearInterval(timerRef.current);
    }
  }, [connectStream, router]);

  useEffect(() => {
    if (startedRef.current) return;
    startedRef.current = true;
    void startForge();
    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
    };
  }, [startForge]);

  const completedSteps = events.filter(
    (e) => e.type === "step_complete" || e.type === "graph_ready",
  ).length;

  return (
    <main
      className="min-h-screen grid-dots px-4 py-10"
      data-screen="forge-stream"
    >
      <div className="mx-auto max-w-3xl">
        <div className="mb-8">
          <p className="text-xs uppercase tracking-widest text-text-muted">
            Live Roadmap Forge
          </p>
          <h1 className="mt-2 text-3xl font-semibold text-text-primary">
            Forjando sua trilha personalizada
          </h1>
          <p className="mt-2 text-sm text-text-secondary">
            Timeline ao vivo — sem preview de grafo durante o stream.
          </p>
          <div className="mt-4 flex gap-4 text-xs text-text-muted">
            <span>{elapsedSec}s</span>
            <span>{completedSteps} etapas concluídas</span>
            <span className="capitalize">{status}</span>
          </div>
          {status === "done" && (
            <p className="mt-3 text-sm text-accent-mint">
              Plano pronto — revise o resultado e avance quando quiser.
            </p>
          )}
        </div>

        {error && (
          <p className="mb-4 rounded-md border border-danger/30 bg-danger/10 p-3 text-sm text-danger">
            {error}
          </p>
        )}

        <ForgeTimeline>
          {events.map((event, index) => (
            <ForgeEventLine key={`${event.type}-${index}`} event={event} index={index} />
          ))}
          {(status === "starting" || status === "streaming") && events.length === 0 && (
            <li className="font-mono text-sm text-accent-mint animate-pulse">
              Conectando ao stream SSE…
            </li>
          )}
        </ForgeTimeline>

        {status === "error" && (
          <div className="mt-8 flex gap-4">
            <Button
              onClick={() => {
                clearForgeSession();
                void startForge(true);
              }}
            >
              Tentar novamente
            </Button>
            <Link href="/onboarding/edit">
              <Button variant="ghost">Voltar ao diagnóstico</Button>
            </Link>
          </div>
        )}

        {status === "done" && (
          <div className="mt-8 flex flex-wrap gap-4">
            <Link href="/forge/complete">
              <Button>Ver roadmap →</Button>
            </Link>
            <Link href="/onboarding/edit">
              <Button variant="ghost">Voltar ao diagnóstico</Button>
            </Link>
          </div>
        )}
      </div>
    </main>
  );
}
