export type FundamentalsBlock =
  | { type: "heading"; level: 2 | 3; id: string; text: string }
  | { type: "paragraph"; text: string }
  | { type: "video"; videoId: string };

const YOUTUBE =
  /^https?:\/\/(?:www\.)?(?:youtube\.com\/watch\?(?:.*&)?v=|youtu\.be\/|youtube\.com\/embed\/)([A-Za-z0-9_-]{11})(?:[?&#].*)?$/;

function headingId(text: string): string {
  return text
    .trim()
    .toLowerCase()
    .replace(/[^a-z0-9\s-]/g, "")
    .trim()
    .replace(/\s+/g, "-")
    .replace(/-+/g, "-");
}

export function parseFundamentalsMarkdown(markdown: string): FundamentalsBlock[] {
  const blocks: FundamentalsBlock[] = [];
  for (const chunk of markdown.replace(/\r\n/g, "\n").split(/\n{2,}/)) {
    const text = chunk.trim();
    if (!text) continue;
    const heading = /^(#{2,3})\s+(.+)$/.exec(text);
    if (heading && !text.includes("\n")) {
      const title = heading[2].trim();
      blocks.push({
        type: "heading",
        level: heading[1].length === 2 ? 2 : 3,
        id: headingId(title),
        text: title,
      });
      continue;
    }
    const video = YOUTUBE.exec(text);
    if (video && !text.includes("\n")) {
      blocks.push({ type: "video", videoId: video[1] });
      continue;
    }
    blocks.push({ type: "paragraph", text: text.replace(/\n/g, " ") });
  }
  return blocks;
}
