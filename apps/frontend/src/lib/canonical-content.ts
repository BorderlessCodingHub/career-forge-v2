export type CanonicalBlock =
  | { type: "heading"; level: 1 | 2 | 3; text: string }
  | { type: "paragraph"; text: string }
  | { type: "list"; items: string[] }
  | { type: "code"; text: string };

export function buildLearnHref(skillId: string): string {
  return `/learn/${encodeURIComponent(skillId)}`;
}

export function parseCanonicalMarkdown(markdown: string): CanonicalBlock[] {
  const blocks: CanonicalBlock[] = [];
  const chunks = markdown.replace(/\r\n/g, "\n").split(/```/);

  chunks.forEach((chunk, index) => {
    if (index % 2 === 1) {
      const body = chunk.replace(/^[^\n]*\n/, "").replace(/\n$/, "");
      if (body.trim()) {
        blocks.push({ type: "code", text: body });
      }
      return;
    }

    let listItems: string[] = [];
    const flushList = () => {
      if (listItems.length > 0) {
        blocks.push({ type: "list", items: listItems });
        listItems = [];
      }
    };

    for (const rawLine of chunk.split("\n")) {
      const line = rawLine.trimEnd();
      const trimmed = line.trim();
      if (!trimmed) {
        flushList();
        continue;
      }
      const heading = trimmed.match(/^(#{1,3})\s+(.+)$/);
      if (heading) {
        flushList();
        const level = heading[1].length as 1 | 2 | 3;
        blocks.push({ type: "heading", level, text: heading[2] });
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
  });

  return blocks;
}
