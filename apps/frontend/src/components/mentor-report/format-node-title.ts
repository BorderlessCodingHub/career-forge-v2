import { CAREER_GOALS } from "../../lib/onboarding-data";

const NODE_ID_PREFIX = /^node-\d+-/i;
const SLUG_PATTERN = /^[a-z0-9-]+$/i;

/** Display-only title for mentor report cards — never mutates stored node_id. */
export function humanizeNodeId(nodeId: string): string {
  const slug = nodeId.replace(NODE_ID_PREFIX, "").replace(/[-_]+/g, " ").trim();
  if (!slug) return nodeId;
  return slug.replace(/\b\w/g, (char) => char.toUpperCase());
}

export function formatNodeTitleForDisplay(nodeTitle: string, nodeId: string): string {
  const trimmed = nodeTitle.trim();
  if (trimmed && trimmed !== nodeId) return trimmed;
  return humanizeNodeId(nodeId);
}

/** Display-only career goal label for /report Objetivo — never mutates stored goal_id. */
export function formatGoalForDisplay(goal: string): string {
  const trimmed = goal.trim();
  if (!trimmed) return trimmed;
  const mapped = CAREER_GOALS.find((item) => item.id === trimmed)?.title;
  if (mapped) return mapped;
  if (!SLUG_PATTERN.test(trimmed)) return trimmed;
  return humanizeNodeId(trimmed);
}

/** Strip legacy `(node-id)` parentheticals and split dense fallback paragraphs. */
export function formatLegacyMentorSummary(summary: string): string[] {
  const cleaned = summary
    .replace(/\([^)]*node-[^)]*\)/gi, "")
    .replace(/\s+/g, " ")
    .trim();
  if (!cleaned) return [];
  return cleaned
    .split(/(?<=[.!?])\s+/)
    .map((line) => line.trim())
    .filter(Boolean);
}

export function hasStructuredEvidence(entry: {
  strengths: string[];
  gaps: string[];
  recommended_intervention: string;
}): boolean {
  return (
    entry.strengths.length > 0 ||
    entry.gaps.length > 0 ||
    entry.recommended_intervention.trim().length > 0
  );
}
