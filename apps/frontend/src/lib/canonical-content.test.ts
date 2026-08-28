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

  it("parses a same-origin image as a figure", () => {
    const blocks = parseCanonicalMarkdown(
      "See the map.\n\n![Tube map of near](/learn/rag-embeddings-tube.svg)\n",
    );

    expect(blocks).toEqual([
      { type: "paragraph", text: "See the map." },
      {
        type: "figure",
        alt: "Tube map of near",
        src: "/learn/rag-embeddings-tube.svg",
      },
    ]);
  });

  it("drops unsafe image src instead of emitting a figure", () => {
    const blocks = parseCanonicalMarkdown(
      "![x](javascript:alert(1))\n\n![remote](https://evil.example/x.png)\n\n![ok](/learn/ok.svg)\n",
    );

    expect(blocks).toEqual([{ type: "figure", alt: "ok", src: "/learn/ok.svg" }]);
  });

  it("parses a blockquote as a labelled callout", () => {
    const blocks = parseCanonicalMarkdown(
      "> **The win.**\n> Same map, same ruler, re-embed cost.\n",
    );

    expect(blocks).toEqual([
      {
        type: "callout",
        label: "The win.",
        text: "Same map, same ruler, re-embed cost.",
      },
    ]);
  });

  it("parses a quiz fence into prompt, options, and why", () => {
    const blocks = parseCanonicalMarkdown(
      "```quiz\nThe vector of a chunk stores:\n- A) position on the learned map\n- B) a compressed copy of the text\ncorrect: A\nwhy: The vector is a position, not a compression of the text.\n```\n",
    );

    expect(blocks).toEqual([
      {
        type: "quiz",
        prompt: "The vector of a chunk stores:",
        options: [
          { key: "A", text: "position on the learned map" },
          { key: "B", text: "a compressed copy of the text" },
        ],
        correct: "A",
        why: "The vector is a position, not a compression of the text.",
      },
    ]);
  });

  it("drops an incomplete quiz fence instead of emitting a quiz", () => {
    const blocks = parseCanonicalMarkdown(
      "```quiz\nNo options here.\ncorrect: A\nwhy: nope\n```\n\nStill here.\n",
    );

    expect(blocks).toEqual([{ type: "paragraph", text: "Still here." }]);
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
