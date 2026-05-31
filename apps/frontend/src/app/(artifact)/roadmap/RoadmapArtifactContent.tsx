"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { useSearchParams } from "next/navigation";

import {
  getTrailChecklistProgressPct,
  MentorDrawer,
  NodeDrawer,
  TutorDrawer,
  VerticalSpine,
  VerticalSpineShell,
  VerticalSpineSkeleton,
} from "@/components/roadmap";
import { TrailProgressRing } from "@/components/ui/TrailProgressRing";
import { clearAdaptiveSession, getAdaptiveSession } from "@/lib/adaptive-session";
import { getRoadmap, patchRoadmapChecklist, syncRoadmap } from "@/lib/api-client";
import { clearForgeGraph, getForgeGraph } from "@/lib/forge-session";
import type {
  ForgeGraphNode,
  RoadmapNode,
  RoadmapResponse,
  RoadmapSyncNode,
} from "@/types/contracts";

function forgeGraphToSyncNodes(graph: ForgeGraphNode[]): RoadmapSyncNode[] {
  return graph.map((node) => ({
    ...node,
    title: node.title ?? node.node_id,
  }));
}

export default function RoadmapArtifactPageContent() {
  const searchParams = useSearchParams();
  const adaptiveMode = searchParams.get("adaptive") === "1";
  const nodeFromQuery = searchParams.get("node");
  const prevAdaptiveMode = useRef<boolean | null>(null);

  const [roadmap, setRoadmap] = useState<RoadmapResponse | null>(null);
  const [highlightNodeId, setHighlightNodeId] = useState<string | null>(null);
  const [selectedNodeId, setSelectedNodeId] = useState<string | null>(null);
  const [mentorOpen, setMentorOpen] = useState(false);
  const [tutorOpen, setTutorOpen] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [adaptiveSessionMissing, setAdaptiveSessionMissing] = useState(false);

  const showingAdaptiveView = adaptiveMode && !adaptiveSessionMissing;

  const openMentor = useCallback(() => {
    setMentorOpen(true);
  }, []);

  const openTutor = useCallback(() => {
    setTutorOpen(true);
  }, []);

  const closeDrawer = useCallback(() => {
    const closingNodeId = selectedNodeId;
    setSelectedNodeId(null);
    if (!closingNodeId) return;
    requestAnimationFrame(() => {
      const trigger = document.querySelector<HTMLButtonElement>(
        `[data-testid="roadmap-node-${closingNodeId}"]`,
      );
      trigger?.focus();
    });
  }, [selectedNodeId]);

  const loadRoadmap = useCallback(async () => {
    setLoading(true);
    setError(null);
    setAdaptiveSessionMissing(false);

    const adaptiveSession = adaptiveMode ? getAdaptiveSession() : null;
    if (adaptiveMode && !adaptiveSession) {
      setAdaptiveSessionMissing(true);
    }

    try {
      // Never re-sync the forge graph in adaptive mode — the recalibrated user
      // graph is already persisted server-side and a re-sync would overwrite it.
      if (!adaptiveMode) {
        const forgeGraph = getForgeGraph();
        if (forgeGraph?.length) {
          await syncRoadmap(forgeGraphToSyncNodes(forgeGraph));
          clearForgeGraph();
        }
      }

      // Always read fresh server state so async-injected remediation tasks + gaps
      // (HAC-67/68/69) show up, even in adaptive mode — the snapshot only picked
      // the highlighted node. HAC-72.
      const data = await getRoadmap();
      setRoadmap(data);

      if (adaptiveSession) {
        setHighlightNodeId(adaptiveSession.nodeId);
        setSelectedNodeId(adaptiveSession.nodeId);
      } else if (nodeFromQuery) {
        setHighlightNodeId(nodeFromQuery);
        setSelectedNodeId(nodeFromQuery);
      } else {
        setHighlightNodeId(null);
      }
    } catch (err) {
      if (adaptiveSession) {
        // Fallback to the client snapshot if the server is unreachable.
        setRoadmap(adaptiveSession.roadmap);
        setHighlightNodeId(adaptiveSession.nodeId);
        setSelectedNodeId(adaptiveSession.nodeId);
      } else {
        setError(err instanceof Error ? err.message : "Falha ao carregar trilha");
      }
    } finally {
      setLoading(false);
    }
  }, [adaptiveMode, nodeFromQuery]);

  useEffect(() => {
    void loadRoadmap();
  }, [loadRoadmap]);

  // Adaptive mode: the gap classifier runs async after the mock submit, so the
  // remediation tasks + focos land server-side a few seconds later. Poll briefly
  // to surface them without forcing a manual navigation back to /roadmap. HAC-72.
  useEffect(() => {
    if (!adaptiveMode) return;
    let cancelled = false;
    const timers: ReturnType<typeof setTimeout>[] = [];
    const refresh = async () => {
      try {
        const data = await getRoadmap();
        if (!cancelled) setRoadmap(data);
      } catch {
        /* keep current state on transient errors */
      }
    };
    [4000, 9000, 14000].forEach((ms) => timers.push(setTimeout(refresh, ms)));
    return () => {
      cancelled = true;
      timers.forEach(clearTimeout);
    };
  }, [adaptiveMode]);

  useEffect(() => {
    if (prevAdaptiveMode.current === true && !adaptiveMode) {
      clearAdaptiveSession();
    }
    prevAdaptiveMode.current = adaptiveMode;
  }, [adaptiveMode]);

  const trailProgressPct = roadmap ? getTrailChecklistProgressPct(roadmap.nodes) : null;

  const selectedNode: RoadmapNode | null =
    roadmap?.nodes.find((node) => node.node_id === selectedNodeId) ?? null;

  const handleChecklistToggle = useCallback(
    async (
      nodeId: string,
      itemType: "task" | "reference",
      itemId: string,
      done: boolean,
    ) => {
      if (adaptiveMode && !adaptiveSessionMissing) {
        setRoadmap((current) => {
          if (!current) return current;
          return {
            ...current,
            nodes: current.nodes.map((node) => {
              if (node.node_id !== nodeId) return node;
              const updateItems = (items: RoadmapNode["tasks"]) =>
                items.map((item) =>
                  item.id === itemId ? { ...item, done } : item,
                );
              const tasks =
                itemType === "task" ? updateItems(node.tasks) : node.tasks;
              const references =
                itemType === "reference"
                  ? updateItems(node.references)
                  : node.references;
              const checklist_completed = [...tasks, ...references].filter(
                (item) => item.done,
              ).length;
              return {
                ...node,
                tasks,
                references,
                checklist_completed,
                checklist_total: tasks.length + references.length,
              };
            }),
          };
        });
        return;
      }

      const updated = await patchRoadmapChecklist(nodeId, {
        item_type: itemType,
        item_id: itemId,
        done,
      });
      setRoadmap(updated);
    },
    [adaptiveMode, adaptiveSessionMissing],
  );

  return (
    <VerticalSpineShell>
      <main
        className="min-h-screen pb-16"
        data-screen={showingAdaptiveView ? "adaptive-state" : "vertical-roadmap"}
        data-mode="artifact"
        data-testid="vertical-roadmap"
      >
        <div className="mx-auto max-w-3xl px-4 pt-6 text-center">
          <p className="text-xs uppercase tracking-widest text-text-muted">Artefato · Trilha</p>
          <p className="mt-2 text-sm text-text-secondary">
            {showingAdaptiveView
              ? "A trilha reagiu ao seu desempenho — revise o nó destacado antes de avançar."
              : "Clique em um nó para ver status, referências e validar mastery."}
          </p>
          {trailProgressPct != null && (
            <div className="mt-4 flex flex-col items-center gap-1.5">
              <TrailProgressRing percent={trailProgressPct} />
              <p className="text-[10px] uppercase tracking-widest text-text-muted">
                Progresso de estudo
              </p>
            </div>
          )}
        </div>

        {loading && <VerticalSpineSkeleton />}

        {error && (
          <p className="mx-auto mt-6 max-w-lg rounded-md border border-danger/30 bg-danger/10 p-3 text-center text-sm text-danger">
            {error}
          </p>
        )}

        {roadmap && !loading && (
          <VerticalSpine
            categories={roadmap.categories}
            nodes={roadmap.nodes}
            selectedNodeId={selectedNodeId ?? highlightNodeId}
            onSelectNode={setSelectedNodeId}
          />
        )}

        <NodeDrawer
          node={selectedNode}
          categories={roadmap?.categories}
          onClose={closeDrawer}
          onOpenMentor={openMentor}
          onOpenTutor={openTutor}
          onChecklistToggle={handleChecklistToggle}
        />

        <MentorDrawer
          open={mentorOpen}
          onClose={() => setMentorOpen(false)}
          node={selectedNode}
        />

        <TutorDrawer
          open={tutorOpen}
          onClose={() => setTutorOpen(false)}
          node={selectedNode}
        />
      </main>
    </VerticalSpineShell>
  );
}
