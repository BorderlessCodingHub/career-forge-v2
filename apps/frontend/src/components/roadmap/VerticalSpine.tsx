"use client";

import { useEffect, useRef, type ReactNode } from "react";

import type { RoadmapCategory, RoadmapNode } from "@/types/contracts";

import { SkillNode } from "./SkillNode";

type VerticalSpineProps = {
  categories: RoadmapCategory[];
  nodes: RoadmapNode[];
  selectedNodeId?: string | null;
  onSelectNode?: (nodeId: string) => void;
};

function nodesForCategory(nodes: RoadmapNode[], categoryId: string) {
  return nodes.filter((node) => node.category === categoryId);
}

function connectorColorClass(node: RoadmapNode, selected: boolean): string {
  if (node.status === "revisar") return "bg-warning";
  if (selected) return "bg-accent-mint";
  return "bg-border";
}

type SpineConnectorProps = {
  node: RoadmapNode;
  selected: boolean;
};

function SpineConnector({ node, selected }: SpineConnectorProps) {
  return (
    <div
      className={`h-[2px] min-w-6 max-w-[120px] flex-1 transition-colors ${connectorColorClass(node, selected)}`}
      aria-hidden
      data-testid={`roadmap-connector-${node.node_id}`}
    />
  );
}

export function VerticalSpine({
  categories,
  nodes,
  selectedNodeId,
  onSelectNode,
}: VerticalSpineProps) {
  const rowRefs = useRef<Map<string, HTMLLIElement>>(new Map());

  useEffect(() => {
    if (!selectedNodeId) return;
    const row = rowRefs.current.get(selectedNodeId);
    row?.scrollIntoView({ behavior: "smooth", block: "nearest" });
  }, [selectedNodeId]);

  return (
    <div className="relative mx-auto max-w-3xl px-4 py-6" data-testid="vertical-spine">
      <div
        className="absolute bottom-0 left-1/2 top-0 w-px -translate-x-1/2 bg-border"
        aria-hidden
      />
      <div className="space-y-12">
        {categories.map((category) => {
          const categoryNodes = nodesForCategory(nodes, category.id);
          if (!categoryNodes.length) return null;

          return (
            <section key={category.id} className="relative">
              <div className="mb-6 flex justify-center">
                <span className="rounded-full border border-border bg-surface px-4 py-1 text-xs font-medium uppercase tracking-widest text-text-muted">
                  {category.label}
                </span>
              </div>
              <ol className="space-y-8">
                {categoryNodes.map((node) => (
                  <SpineRow
                    key={node.node_id}
                    ref={(element) => {
                      if (element) rowRefs.current.set(node.node_id, element);
                      else rowRefs.current.delete(node.node_id);
                    }}
                    node={node}
                    selected={selectedNodeId === node.node_id}
                    onSelect={onSelectNode}
                  />
                ))}
              </ol>
            </section>
          );
        })}
      </div>
    </div>
  );
}

type SpineRowProps = {
  node: RoadmapNode;
  selected: boolean;
  onSelect?: (nodeId: string) => void;
  ref?: (element: HTMLLIElement | null) => void;
};

function SpineRow({ node, selected, onSelect, ref }: SpineRowProps) {
  const isLeft = node.side === "left";

  return (
    <li ref={ref} className="relative flex items-center" data-side={node.side}>
      <div className="flex min-w-0 flex-1 items-center justify-end">
        {isLeft && (
          <>
            <SkillNode node={node} selected={selected} onSelect={onSelect} />
            <SpineConnector node={node} selected={selected} />
          </>
        )}
      </div>
      <div
        className={`relative z-10 h-3 w-3 shrink-0 rounded-full border-2 transition-colors ${
          selected
            ? "border-accent-mint bg-accent shadow-[0_0_12px_var(--mint-glow)]"
            : "border-border bg-bg"
        }`}
        aria-hidden
      />
      <div className="flex min-w-0 flex-1 items-center justify-start">
        {!isLeft && (
          <>
            <SpineConnector node={node} selected={selected} />
            <SkillNode node={node} selected={selected} onSelect={onSelect} />
          </>
        )}
      </div>
    </li>
  );
}

export function VerticalSpineShell({ children }: { children: ReactNode }) {
  return <div className="grid-dots min-h-full">{children}</div>;
}
