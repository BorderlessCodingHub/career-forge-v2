import type { RoadmapNode } from "@/types/contracts";

type SkillNodeProps = {
  node: RoadmapNode;
  selected?: boolean;
  onSelect?: (nodeId: string) => void;
};

export function SkillNode({ node, selected = false, onSelect }: SkillNodeProps) {
  return (
    <button
      type="button"
      data-testid={`roadmap-node-${node.node_id}`}
      onClick={() => onSelect?.(node.node_id)}
      className={`w-full max-w-[260px] rounded-node border px-4 py-3 text-left transition-all ${
        selected
          ? "border-accent bg-surface-node/90 shadow-[0_0_24px_var(--accent-glow)]"
          : "border-accent/35 bg-surface-node/70 hover:border-accent/60"
      }`}
    >
      <p className="text-sm font-semibold text-text-primary">{node.title}</p>
      <p className="mt-1 line-clamp-2 text-xs text-text-secondary">{node.description}</p>
    </button>
  );
}
