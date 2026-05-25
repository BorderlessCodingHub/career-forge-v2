import type { RoadmapForgeEvent } from "@/types/contracts";

export function subscribeForgeStream(
  url: string,
  onEvent: (event: RoadmapForgeEvent) => void,
): () => void {
  const source = new EventSource(url);
  source.onmessage = (message) => {
    try {
      onEvent(JSON.parse(message.data) as RoadmapForgeEvent);
    } catch {
      // ignore malformed chunks until HAC-18
    }
  };
  return () => source.close();
}
