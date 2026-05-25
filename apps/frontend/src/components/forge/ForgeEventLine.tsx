import type { RoadmapForgeEvent } from "@/types/contracts";

import { ForgeStep } from "./ForgeStep";

type ForgeEventLineProps = {
  event: RoadmapForgeEvent;
  index: number;
};

export function ForgeEventLine({ event, index }: ForgeEventLineProps) {
  if (event.type === "reasoning_delta") {
    return (
      <ForgeStep step={`${index + 1} · ${event.step}`}>
        <p className="text-text-primary">{event.text}</p>
      </ForgeStep>
    );
  }

  if (event.type === "artifact_found") {
    return (
      <ForgeStep step={`${index + 1} · evidência`}>
        <p className="font-medium text-accent-mint">{event.label}</p>
        <p className="mt-1 text-text-secondary">{event.detail}</p>
      </ForgeStep>
    );
  }

  if (event.type === "node_updated") {
    return (
      <ForgeStep step={`${index + 1} · nó`}>
        <p className="text-text-primary">
          <span className="text-accent">{event.node.node_id}</span>
          {event.node.mastery_score != null && (
            <span className="text-text-muted">
              {" "}
              · {event.node.mastery_score}% mastery
            </span>
          )}
        </p>
      </ForgeStep>
    );
  }

  if (event.type === "step_complete") {
    return (
      <ForgeStep step={`${index + 1} · concluído`}>
        <p className="text-success">Etapa {event.step} finalizada</p>
      </ForgeStep>
    );
  }

  if (event.type === "graph_ready") {
    return (
      <ForgeStep step={`${index + 1} · pronto`}>
        <p className="text-success">
          Trilha forjada — {event.graph.length} nós no grafo acumulado
        </p>
      </ForgeStep>
    );
  }

  if (event.type === "error") {
    return (
      <ForgeStep step={`${index + 1} · erro`}>
        <p className="text-danger">{event.message}</p>
      </ForgeStep>
    );
  }

  return null;
}
