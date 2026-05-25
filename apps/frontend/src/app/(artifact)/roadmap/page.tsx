"use client";

import { useCallback, useEffect, useState } from "react";

import { NodeDrawer, VerticalSpine, VerticalSpineShell } from "@/components/roadmap";
import { getRoadmap, syncRoadmap } from "@/lib/api-client";
import { getForgeGraph } from "@/lib/forge-session";
import { getStoredDiagnosis } from "@/lib/onboarding-session";
import type { RoadmapNode, RoadmapResponse } from "@/types/contracts";

function forgeGraphToSyncNodes(graph: NonNullable<ReturnType<typeof getForgeGraph>>) {
  return graph.map((node) => ({
    node_id: node.node_id,
    title: node.title ?? node.node_id,
    status: node.status,
    mastery_score: node.mastery_score,
    priority: node.priority ?? null,
    rationale: node.rationale ?? null,
  }));
}

export default function RoadmapArtifactPage() {
  const [roadmap, setRoadmap] = useState<RoadmapResponse | null>(null);
  const [selectedNodeId, setSelectedNodeId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  const trackName =
    getStoredDiagnosis()?.profile.label ??
    roadmap?.track.title ??
    "Backend Developer";

  const loadRoadmap = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const forgeGraph = getForgeGraph();
      if (forgeGraph?.length) {
        await syncRoadmap(forgeGraphToSyncNodes(forgeGraph));
      }
      const data = await getRoadmap();
      setRoadmap(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Falha ao carregar trilha");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void loadRoadmap();
  }, [loadRoadmap]);

  const selectedNode: RoadmapNode | null =
    roadmap?.nodes.find((node) => node.node_id === selectedNodeId) ?? null;

  return (
    <VerticalSpineShell>
      <main
        className="min-h-screen pb-16"
        data-screen="vertical-roadmap"
        data-mode="artifact"
        data-testid="vertical-roadmap"
      >
        <div className="mx-auto max-w-3xl px-4 pt-10 text-center">
          <p className="text-xs uppercase tracking-widest text-text-muted">Artefato · Trilha</p>
          <h1 className="mt-2 text-3xl font-semibold text-text-primary">{trackName}</h1>
          <p className="mt-2 text-sm text-text-secondary">
            Clique em um nó para ver status, referências e validar mastery.
          </p>
        </div>

        {loading && (
          <p className="mt-12 text-center text-sm text-text-muted animate-pulse">
            Carregando trilha…
          </p>
        )}

        {error && (
          <p className="mx-auto mt-8 max-w-lg rounded-lg border border-danger/30 bg-danger/10 p-3 text-center text-sm text-danger">
            {error}
          </p>
        )}

        {roadmap && !loading && (
          <VerticalSpine
            categories={roadmap.categories}
            nodes={roadmap.nodes}
            selectedNodeId={selectedNodeId}
            onSelectNode={setSelectedNodeId}
          />
        )}

        <NodeDrawer
          node={selectedNode}
          onClose={() => setSelectedNodeId(null)}
        />
      </main>
    </VerticalSpineShell>
  );
}
