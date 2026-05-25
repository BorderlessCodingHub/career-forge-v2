import type { RubricDimensionKey, RubricMapItem } from "@/types/contracts";

type DimensionStatus = "mapped" | "active" | "pending";

function mapStatus(
  item: RubricMapItem,
  activeKeys: Set<RubricDimensionKey>,
): DimensionStatus {
  if (item.saturated) return "mapped";
  if (activeKeys.has(item.rubric_key)) return "active";
  if (item.confidence > 0) return "active";
  return "pending";
}

const STATUS_STYLES: Record<
  DimensionStatus,
  { dot: string; label: string; description: string }
> = {
  mapped: {
    dot: "bg-accent-mint",
    label: "text-accent-mint",
    description: "text-text-muted",
  },
  active: {
    dot: "bg-accent animate-pulse",
    label: "text-text-primary",
    description: "text-text-secondary",
  },
  pending: {
    dot: "bg-border",
    label: "text-text-muted",
    description: "text-text-muted",
  },
};

type MappingDimensionListProps = {
  items: RubricMapItem[];
  activeKeys: Set<RubricDimensionKey>;
  loading: boolean;
};

export function MappingDimensionList({
  items,
  activeKeys,
  loading,
}: MappingDimensionListProps) {
  return (
    <ul className="mt-3 space-y-3">
      {items.map((item) => {
        const status = loading ? "pending" : mapStatus(item, activeKeys);
        const styles = STATUS_STYLES[status];
        const showPulse = loading || (status === "active" && !item.saturated);

        return (
          <li key={item.rubric_key} className="flex gap-2.5">
            <span
              className={`mt-1.5 h-2 w-2 shrink-0 rounded-full ${styles.dot} ${
                showPulse ? "animate-pulse" : ""
              }`}
            />
            <div className="min-w-0">
              <div className={`text-sm font-medium ${styles.label}`}>
                {item.label}
              </div>
              <div
                className={`mt-0.5 text-xs leading-snug ${styles.description} ${
                  loading ? "animate-pulse" : ""
                }`}
              >
                {item.description}
              </div>
            </div>
          </li>
        );
      })}
    </ul>
  );
}
