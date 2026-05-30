"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { useSearchParams } from "next/navigation";

import { useArtifactChrome } from "@/components/layout/ArtifactChromeContext";
import {
  MissionBanner,
  MentorDrawer,
  NodeDrawer,
  TutorDrawer,
  VerticalSpine,
  VerticalSpineShell,
  VerticalSpineSkeleton,
} from "@/components/roadmap";
import { clearAdaptiveSession, getAdaptiveSession } from "@/lib/adaptive-session";
import { getRoadmap, patchRoadmapChecklist, syncRoadmap } from "@/lib/api-client";
import { clearForgeGraph, getForgeGraph } from "@/lib/forge-session";
import { computeTrailStudySummary } from "@/lib/trail-study-summary";
import type {
  ForgeGraphNode,
  PlanUpdateResponse,
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
  const { setChrome, clearChrome } = useArtifactChrome();

  const [roadmap, setRoadmap] = useState<RoadmapResponse | null>(null);
  const [planUpdate, setPlanUpdate] = useState<PlanUpdateResponse | null>(null);
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
    try {
      if (adaptiveMode) {
        const adaptiveSession = getAdaptiveSession();
        if (adaptiveSession) {
          setRoadmap(adaptiveSession.roadmap);
          setPlanUpdate(adaptiveSession.plan);
          setHighlightNodeId(adaptiveSession.nodeId);
          setSelectedNodeId(adaptiveSession.nodeId);
          return;
        }
        setAdaptiveSessionMissing(true);
      }

      const forgeGraph = getForgeGraph();
      if (forgeGraph?.length) {
        await syncRoadmap(forgeGraphToSyncNodes(forgeGraph));
        clearForgeGraph();
      }
      const data = await getRoadmap();
      setRoadmap(data);
      setPlanUpdate(null);
      if (nodeFromQuery) {
        setHighlightNodeId(nodeFromQuery);
        setSelectedNodeId(nodeFromQuery);
      } else {
        setHighlightNodeId(null);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Falha ao carregar trilha");
    } finally {
      setLoading(false);
    }
  }, [adaptiveMode, nodeFromQuery]);

  useEffect(() => {
    void loadRoadmap();
  }, [loadRoadmap]);

  useEffect(() => {
    if (prevAdaptiveMode.current === true && !adaptiveMode) {
      clearAdaptiveSession();
    }
    prevAdaptiveMode.current = adaptiveMode;
  }, [adaptiveMode]);

  useEffect(() => {
    setChrome({
      onOpenMentor: openMentor,
      trailSummary: roadmap ? computeTrailStudySummary(roadmap.nodes) : null,
    });
    return () => clearChrome();
  }, [roadmap, openMentor, setChrome, clearChrome]);

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
        </div>

        {adaptiveSessionMissing && (
          <p
            className="mx-auto mt-4 max-w-lg rounded-md border border-warning/30 bg-warning/10 p-3 text-center text-sm text-warning"
            data-testid="adaptive-session-missing"
          >
            Sessão adaptativa não encontrada — mostrando a trilha atual do servidor. Refaça a
            validação para gerar uma nova ramificação.
          </p>
        )}

        {planUpdate && showingAdaptiveView && <MissionBanner plan={planUpdate} />}

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
