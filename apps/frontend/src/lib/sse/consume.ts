import { parseSseBlock } from "@/lib/sse/parse";
import {
  QUOTA_EXHAUSTED_COPY,
  isQuotaExhaustedMessage,
} from "@/lib/quota";

type SseHandler<T> = (eventName: string, payload: T) => void;

function detailFromErrorBody(body: { detail?: unknown }): string | null {
  const detail = body.detail;
  if (typeof detail === "string") return detail;
  if (
    detail &&
    typeof detail === "object" &&
    "message" in detail &&
    typeof (detail as { message: unknown }).message === "string"
  ) {
    return (detail as { message: string }).message;
  }
  return null;
}

export async function consumeFetchEventStream<T>(
  url: string,
  init: RequestInit,
  onMessage: SseHandler<T>,
  parsePayload: (raw: unknown) => T | null,
): Promise<void> {
  const response = await fetch(url, {
    ...init,
    headers: {
      Accept: "text/event-stream",
      ...init.headers,
    },
  });

  if (!response.ok || !response.body) {
    let detail = `${response.status} ${response.statusText}`;
    try {
      const body = (await response.json()) as { detail?: unknown };
      detail = detailFromErrorBody(body) ?? detail;
    } catch {
      // ignore parse errors
    }
    if (response.status === 429 || isQuotaExhaustedMessage(detail)) {
      throw new Error(QUOTA_EXHAUSTED_COPY);
    }
    throw new Error(`SSE request failed: ${detail}`);
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });
    const parts = buffer.split("\n\n");
    buffer = parts.pop() ?? "";

    for (const part of parts) {
      const message = parseSseBlock(part);
      if (!message) continue;

      let raw: unknown;
      try {
        raw = JSON.parse(message.data);
      } catch {
        continue;
      }

      const payload = parsePayload(raw);
      if (payload === null) continue;
      onMessage(message.event, payload);
    }
  }
}
