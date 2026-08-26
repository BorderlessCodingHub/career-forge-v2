import { describe, expect, it } from "vitest";

import { buildLearnHref, parseCanonicalMarkdown } from "./canonical-content";

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
});
