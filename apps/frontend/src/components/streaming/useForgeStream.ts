"use client";

import { useCallback, useState } from "react";
import { subscribeForgeStream } from "@/lib/sse";
import type { RoadmapForgeEvent } from "@/types/contracts";

export function useForgeStream(url: string) {
  const [events, setEvents] = useState<RoadmapForgeEvent[]>([]);

  const start = useCallback(() => {
    return subscribeForgeStream(url, (event) => {
      setEvents((prev) => [...prev, event]);
    });
  }, [url]);

  return { events, start };
}
