export type CanonicalQuizOption = { key: string; text: string };

export type CanonicalBlock =
  | { type: "heading"; level: 1 | 2 | 3; text: string }
  | { type: "paragraph"; text: string }
  | { type: "list"; items: string[] }
  | { type: "code"; text: string }
  | { type: "figure"; alt: string; src: string }
  | { type: "callout"; label: string; text: string }
  | {
      type: "quiz";
      prompt: string;
      options: CanonicalQuizOption[];
      correct: string;
      why: string;
    };

const SAME_ORIGIN_SRC = /^\/(?!\/)[A-Za-z0-9._/-]+$/;

export function buildLearnHref(skillId: string): string {
  return `/learn/${encodeURIComponent(skillId)}`;
}

function isSafeLearnSrc(src: string): boolean {
  return SAME_ORIGIN_SRC.test(src) && !src.includes("..");
}

function parseCallout(lines: string[]): CanonicalBlock | null {
  const kept = lines.map((line) => line.trim()).filter((line, index) => line.length > 0 || index === 0);
  if (kept.every((line) => !line)) {
    return null;
  }
  const labelMatch = kept[0].match(/^\*\*(.+?)\*\*\s*(.*)$/);
  if (labelMatch) {
    const rest = [labelMatch[2], ...kept.slice(1)].map((part) => part.trim()).filter(Boolean);
    return { type: "callout", label: labelMatch[1], text: rest.join(" ") };
  }
  const text = kept.join(" ").trim();
  if (!text) {
    return null;
  }
  return { type: "callout", label: "", text };
}

function parseQuizFence(raw: string): CanonicalBlock | null {
  const prompt: string[] = [];
  const options: CanonicalQuizOption[] = [];
  let correct = "";
  let why = "";

  for (const rawLine of raw.split("\n")) {
    const line = rawLine.trim();
    if (!line) {
      continue;
    }
    const option = line.match(/^[-*]\s+([A-Z])\)\s+(.+)$/);
    if (option) {
      options.push({ key: option[1], text: option[2] });
      continue;
    }
    const correctMatch = line.match(/^correct:\s*([A-Z])\s*$/i);
    if (correctMatch) {
      correct = correctMatch[1].toUpperCase();
      continue;
    }
    const whyMatch = line.match(/^why:\s+(.+)$/i);
    if (whyMatch) {
      why = whyMatch[1].trim();
      continue;
    }
    prompt.push(line);
  }

  if (options.length < 2 || !why || !options.some((option) => option.key === correct)) {
    return null;
  }

  return {
    type: "quiz",
    prompt: prompt.join(" ").trim(),
    options,
    correct,
    why,
  };
}

export function parseCanonicalMarkdown(markdown: string): CanonicalBlock[] {
  const blocks: CanonicalBlock[] = [];
  const chunks = markdown.replace(/\r\n/g, "\n").split(/```/);

  chunks.forEach((chunk, index) => {
    if (index % 2 === 1) {
      const newline = chunk.indexOf("\n");
      const lang = (newline < 0 ? chunk : chunk.slice(0, newline)).trim();
      const body = (newline < 0 ? "" : chunk.slice(newline + 1)).replace(/\n$/, "");
      if (lang === "quiz") {
        const quiz = parseQuizFence(body);
        if (quiz) {
          blocks.push(quiz);
        }
        return;
      }
      if (body.trim()) {
        blocks.push({ type: "code", text: body });
      }
      return;
    }

    let listItems: string[] = [];
    let quoteLines: string[] = [];

    const flushList = () => {
      if (listItems.length > 0) {
        blocks.push({ type: "list", items: listItems });
        listItems = [];
      }
    };

    const flushQuote = () => {
      const callout = parseCallout(quoteLines);
      quoteLines = [];
      if (callout) {
        blocks.push(callout);
      }
    };

    for (const rawLine of chunk.split("\n")) {
      const line = rawLine.trimEnd();
      const trimmed = line.trim();
      if (!trimmed) {
        flushList();
        flushQuote();
        continue;
      }
      const quote = trimmed.match(/^>\s?(.*)$/);
      if (quote) {
        flushList();
        quoteLines.push(quote[1]);
        continue;
      }
      flushQuote();
      const heading = trimmed.match(/^(#{1,3})\s+(.+)$/);
      if (heading) {
        flushList();
        const level = heading[1].length as 1 | 2 | 3;
        blocks.push({ type: "heading", level, text: heading[2] });
        continue;
      }
      const image = trimmed.match(/^!\[([^\]]*)\]\((.+)\)$/);
      if (image || trimmed.startsWith("![")) {
        flushList();
        const src = image?.[2]?.trim() ?? "";
        const alt = image?.[1] ?? "";
        if (image && isSafeLearnSrc(src)) {
          blocks.push({ type: "figure", alt, src });
        }
        continue;
      }
      const bullet = trimmed.match(/^[-*]\s+(.+)$/);
      if (bullet) {
        listItems.push(bullet[1]);
        continue;
      }
      flushList();
      blocks.push({ type: "paragraph", text: trimmed });
    }
    flushList();
    flushQuote();
  });

  return blocks;
}
