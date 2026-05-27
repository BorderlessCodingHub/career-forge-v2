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
        <MarkdownText text={event.detail} />
        {event.sources && event.sources.length > 0 && (
          <div className="mt-3 grid gap-2">
            {event.sources.map((source) => (
              <a
                key={`${source.url}-${source.title}`}
                href={source.url}
                target="_blank"
                rel="noreferrer"
                className="block rounded-md border border-border bg-surface/60 p-3 transition hover:border-accent/60 hover:bg-surface-elevated"
              >
                <span className="text-sm font-medium text-text-primary">
                  {source.title}
                </span>
                <span className="mt-1 block text-xs text-accent-mint">
                  {hostname(source.url)}
                </span>
                {source.snippet && (
                  <p className="mt-1 line-clamp-2 text-xs text-text-muted">
                    {stripMarkdownLinks(source.snippet)}
                  </p>
                )}
              </a>
            ))}
          </div>
        )}
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

function MarkdownText({ text }: { text: string }) {
  const lines = text.split(/\n+/).map((line) => line.trim()).filter(Boolean);
  return (
    <div className="mt-1 space-y-2 text-text-secondary">
      {lines.map((line, index) => (
        <p key={`${line}-${index}`}>
          <MarkdownInline text={stripMarkdownLinks(line)} />
        </p>
      ))}
    </div>
  );
}

function MarkdownInline({ text }: { text: string }) {
  const parts = text.split(/(\*\*[^*]+\*\*)/g);
  return (
    <>
      {parts.map((part, index) => {
        if (part.startsWith("**") && part.endsWith("**")) {
          return (
            <strong key={`${part}-${index}`} className="font-semibold text-text-primary">
              {part.slice(2, -2)}
            </strong>
          );
        }
        return <span key={`${part}-${index}`}>{part}</span>;
      })}
    </>
  );
}

function stripMarkdownLinks(text: string): string {
  return text
    .replace(/\(\[([^\]]+)\]\([^)]+\)\)/g, "$1")
    .replace(/\[([^\]]+)\]\([^)]+\)/g, "$1")
    .replace(/https?:\/\/\S+/g, "")
    .trim();
}

function hostname(url: string): string {
  try {
    return new URL(url).hostname.replace(/^www\./, "");
  } catch {
    return url;
  }
}
