import type { RoadmapForgeEvent } from "@/types/contracts";

export function StreamEventList({ events }: { events: RoadmapForgeEvent[] }) {
  return (
    <ul className="space-y-2 font-mono text-xs text-text-secondary">
      {events.map((event, index) => (
        <li key={`${event.type}-${index}`}>{event.type}</li>
      ))}
    </ul>
  );
}
