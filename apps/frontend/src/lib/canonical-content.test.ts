import { readFileSync } from "node:fs";
import { resolve } from "node:path";

import { describe, expect, it } from "vitest";

import { buildLearnHref, parseCanonicalMarkdown } from "./canonical-content";

const PILOT_RAG_SKILLS = [
  "rag-embeddings",
  "rag-chunking",
  "rag-retrieval",
  "rag-eval",
  "rag-production",
] as const;

function stripFrontmatter(raw: string): string {
  const text = raw.replace(/^\uFEFF/, "");
  if (!text.startsWith("---")) {
    return text.trim();
  }
  const closing = text.indexOf("\n---", 3);
  if (closing < 0) {
    return text.trim();
  }
  return text.slice(closing + 4).replace(/^\n+/, "").trim();
}

describe("canonical content", () => {
  it("addresses the in-app learn page by skill_id", () => {
    expect(buildLearnHref("rag-chunking")).toBe("/learn/rag-chunking");
  });

  it("parses headings, lists, and code without HTML", () => {
    const blocks = parseCanonicalMarkdown(
      "# Chunking\n\nSplit documents.\n\n- Fixed size\n- Semantic\n\n```ts\nchunk(doc)\n```\n",
    );

    expect(blocks).toEqual([
      { type: "heading", level: 1, text: "Chunking" },
      { type: "paragraph", text: "Split documents." },
      { type: "list", items: ["Fixed size", "Semantic"] },
      { type: "code", text: "chunk(doc)" },
    ]);
  });

  it.each(PILOT_RAG_SKILLS)("parses pilot body %s into headings and lists", (skillId) => {
    const raw = readFileSync(
      resolve(__dirname, "../../../../data/canonical", `${skillId}.md`),
      "utf8",
    );
    const blocks = parseCanonicalMarkdown(stripFrontmatter(raw));
    expect(blocks.some((block) => block.type === "heading")).toBe(true);
    expect(blocks.some((block) => block.type === "list")).toBe(true);
    expect(blocks.some((block) => block.type === "paragraph")).toBe(true);
  });
});
