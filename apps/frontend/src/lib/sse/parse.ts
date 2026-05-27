export type SseMessage = {
  event: string;
  data: string;
};

export function parseSseBlock(block: string): SseMessage | null {
  const lines = block.split("\n");
  let event = "message";
  let data: string | null = null;

  for (const line of lines) {
    if (line.startsWith("event:")) {
      event = line.slice("event:".length).trim();
    } else if (line.startsWith("data:")) {
      data = line.slice("data:".length).trim();
    }
  }

  if (data === null) return null;
  return { event, data };
}

export function parseSseJson<T>(block: string): T | null {
  const message = parseSseBlock(block);
  if (!message) return null;
  try {
    return JSON.parse(message.data) as T;
  } catch {
    return null;
  }
}
