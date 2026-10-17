import type { Block, Inline } from "./types";

export function link(href: string, label: string): Inline {
  return { kind: "link", href, label };
}

export function para(...parts: Array<string | Inline>): Block {
  return {
    kind: "p",
    parts: parts.map((part) => (typeof part === "string" ? { kind: "text", text: part } : part)),
  };
}

export function list(...items: string[]): Block {
  return { kind: "ul", items };
}
