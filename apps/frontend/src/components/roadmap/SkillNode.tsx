import type { RoadmapNode } from "@/types/contracts";

type SkillNodeProps = {
  node: RoadmapNode;
  selected?: boolean;
  onSelect?: (nodeId: string) => void;
};

export function SkillNode({ node, selected = false, onSelect }: SkillNodeProps) {
  const isReview = node.status === "revisar";

  return (
    <button
      type="button"
      data-testid={`roadmap-node-${node.node_id}`}
      data-status={node.status}
      onClick={() => onSelect?.(node.node_id)}
      className={`w-full max-w-[260px] rounded-node border px-4 py-3 text-left transition-all ${
        isReview
          ? "border-warning bg-warning/10 shadow-[0_0_24px_rgba(245,158,11,0.25)]"
          : selected
            ? "border-accent bg-surface-node/90 shadow-[0_0_24px_var(--accent-glow)]"
            : "border-accent/35 bg-surface-node/70 hover:border-accent/60"
      }`}
    >
      <div className="flex items-start justify-between gap-2">
        <p className="text-sm font-semibold text-text-primary">{node.title}</p>
        {isReview && (
          <span
            className="rounded-full bg-warning/20 px-2 py-0.5 text-[10px] font-semibold uppercase tracking-widest text-warning"
            data-testid={`roadmap-node-${node.node_id}-revisar-badge`}
          >
            Revisar
          </span>
        )}
      </div>
      <p className="mt-1 line-clamp-2 text-xs text-text-secondary">{node.description}</p>
    </button>
  );
}
