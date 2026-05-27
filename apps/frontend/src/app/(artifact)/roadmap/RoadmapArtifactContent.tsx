"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { useSearchParams } from "next/navigation";

import { MissionBanner, MentorDrawer, NodeDrawer, VerticalSpine, VerticalSpineShell } from "@/components/roadmap";
import { clearAdaptiveSession, getAdaptiveSession } from "@/lib/adaptive-session";
import { getRoadmap, syncRoadmap } from "@/lib/api-client";
import { clearForgeGraph, getForgeGraph } from "@/lib/forge-session";
import { getStoredDiagnosis } from "@/lib/onboarding-session";
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

  const [roadmap, setRoadmap] = useState<RoadmapResponse | null>(null);
  const [planUpdate, setPlanUpdate] = useState<PlanUpdateResponse | null>(null);
  const [highlightNodeId, setHighlightNodeId] = useState<string | null>(null);
  const [selectedNodeId, setSelectedNodeId] = useState<string | null>(null);
  const [mentorOpen, setMentorOpen] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [adaptiveSessionMissing, setAdaptiveSessionMissing] = useState(false);

  const showingAdaptiveView = adaptiveMode && !adaptiveSessionMissing;

  const trackName =
    getStoredDiagnosis()?.profile.label ??
    roadmap?.track.title ??
    "Backend Developer";

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

  const selectedNode: RoadmapNode | null =
    roadmap?.nodes.find((node) => node.node_id === selectedNodeId) ?? null;

  return (
    <VerticalSpineShell>
      <main
        className="min-h-screen pb-16"
        data-screen={showingAdaptiveView ? "adaptive-state" : "vertical-roadmap"}
        data-mode="artifact"
        data-testid="vertical-roadmap"
      >
        <div className="mx-auto max-w-3xl px-4 pt-10 text-center">
          <p className="text-xs uppercase tracking-widest text-text-muted">Artefato · Trilha</p>
          <h1 className="mt-2 text-3xl font-semibold text-text-primary">{trackName}</h1>
          <p className="mt-2 text-sm text-text-secondary">
            {showingAdaptiveView
              ? "A trilha reagiu ao seu desempenho — revise o nó destacado antes de avançar."
              : "Clique em um nó para ver status, referências e validar mastery."}
          </p>
        </div>

        {adaptiveSessionMissing && (
          <p
            className="mx-auto mt-6 max-w-lg rounded-md border border-warning/30 bg-warning/10 p-3 text-center text-sm text-warning"
            data-testid="adaptive-session-missing"
          >
            Sessão adaptativa não encontrada — mostrando a trilha atual do servidor. Refaça a
            validação para gerar uma nova ramificação.
          </p>
        )}

        {planUpdate && showingAdaptiveView && <MissionBanner plan={planUpdate} />}

        {loading && (
          <p className="mt-12 text-center text-sm text-text-muted animate-pulse">
            Carregando trilha…
          </p>
        )}

        {error && (
          <p className="mx-auto mt-8 max-w-lg rounded-md border border-danger/30 bg-danger/10 p-3 text-center text-sm text-danger">
            {error}
          </p>
        )}

        {roadmap && !loading && (
          <>
            <div className="mx-auto mt-8 flex max-w-3xl justify-center px-4">
              <button
                type="button"
                onClick={() => setMentorOpen(true)}
                className="inline-flex items-center gap-3 rounded-md border border-border bg-surface px-4 py-3 text-left shadow-sm transition hover:border-accent/40 hover:bg-surface-elevated"
                data-testid="mentor-cta"
              >
                <span className="flex h-10 w-10 items-center justify-center rounded-full bg-gradient-to-br from-sky-400 to-indigo-500 text-sm font-semibold text-white">
                  RT
                </span>
                <span>
                  <span className="block text-sm font-medium text-text-primary">
                    Mentor contextual
                  </span>
                  <span className="block text-xs text-text-muted">
                    Sabe onde você errou · chat com memória da trilha
                  </span>
                </span>
              </button>
            </div>
            <VerticalSpine
              categories={roadmap.categories}
              nodes={roadmap.nodes}
              selectedNodeId={selectedNodeId ?? highlightNodeId}
              onSelectNode={setSelectedNodeId}
            />
          </>
        )}

        <NodeDrawer
          node={selectedNode}
          onClose={() => setSelectedNodeId(null)}
          onOpenMentor={() => {
            setMentorOpen(true);
          }}
        />

        <MentorDrawer
          open={mentorOpen}
          onClose={() => setMentorOpen(false)}
          node={selectedNode}
        />
      </main>
    </VerticalSpineShell>
  );
}
