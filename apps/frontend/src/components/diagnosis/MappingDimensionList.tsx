"use client";

import { useTranslations } from "next-intl";

import type {
  RubricDimensionKey,
  RubricDimensionStatus,
  RubricMapItem,
} from "@/types/contracts";

import { isMappingItemDone } from "@/lib/diagnosis-stream";
import { DIMENSION_COPY_KEYS } from "@/lib/profile-dimensions";

const STATUS_STYLES: Record<
  RubricDimensionStatus | "active" | "analyzing",
  { dot: string; label: string; description: string }
> = {
  mapped: {
    dot: "bg-accent-mint",
    label: "text-accent-mint",
    description: "text-text-muted",
  },
  needs_clarification: {
    dot: "bg-warning",
    label: "text-text-primary",
    description: "text-text-secondary",
  },
  pending: {
    dot: "bg-border",
    label: "text-text-muted",
    description: "text-text-muted",
  },
  active: {
    dot: "bg-accent animate-pulse",
    label: "text-text-primary",
    description: "text-text-secondary",
  },
  analyzing: {
    dot: "bg-accent animate-pulse ring-2 ring-accent/30",
    label: "text-accent",
    description: "text-accent/80",
  },
};

function resolveStatus(
  item: RubricMapItem,
  activeKeys: Set<RubricDimensionKey>,
  analyzingKey: RubricDimensionKey | null,
  streaming: boolean,
): RubricDimensionStatus | "active" | "analyzing" {
  if (isMappingItemDone(item)) return "mapped";
  if (activeKeys.has(item.rubric_key)) return "active";
  if (streaming && analyzingKey === item.rubric_key) return "analyzing";
  if (item.status !== "pending" || item.note.trim().length > 0) return item.status;
  return item.status;
}

type MappingDimensionListProps = {
  items: RubricMapItem[];
  activeKeys: Set<RubricDimensionKey>;
  analyzingKey: RubricDimensionKey | null;
  streaming: boolean;
};

export function MappingDimensionList({
  items,
  activeKeys,
  analyzingKey,
  streaming,
}: MappingDimensionListProps) {
  const t = useTranslations("diagnosis");

  return (
    <ul className="mt-3 space-y-3">
      {items.map((item) => {
        const status = resolveStatus(item, activeKeys, analyzingKey, streaming);
        const styles = STATUS_STYLES[status];
        const copy = DIMENSION_COPY_KEYS[item.rubric_key];
        const note = item.note.trim();

        const descriptionText =
          status === "analyzing"
            ? t("analyzing")
            : !streaming && note.length > 0
              ? note
              : copy
                ? t(copy.hint)
                : item.description;

        return (
          <li key={item.rubric_key} className="flex gap-2.5">
            <span className={`mt-1.5 h-2 w-2 shrink-0 rounded-full ${styles.dot}`} />
            <div className="min-w-0">
              <div className={`text-sm font-medium ${styles.label}`}>
                {copy ? t(copy.label) : item.label}
              </div>
              <div className={`mt-0.5 text-xs leading-snug ${styles.description}`}>
                {descriptionText}
              </div>
            </div>
          </li>
        );
      })}
    </ul>
  );
}
