import { describe, expect, it } from "vitest";

import type { RoadmapResponse } from "@/types/contracts";

import {
  buildReferenceViewerHref,
  getReferenceHostname,
  isEmbeddableReferenceUrl,
  resolveReferenceViewer,
} from "./reference-viewer";

const roadmap: RoadmapResponse = {
  track: { id: "rag-engineer", title: "RAG Engineer" },
  categories: [{ id: "foundations", label: "Foundations" }],
  nodes: [
    {
      node_id: "http-basics",
      title: "HTTP basics",
      category: "foundations",
      description: "",
      icon: "code",
      side: "left",
      sort_order: 1,
      prerequisites: [],
      outcomes: [],
      rubric: [],
      status: "em_estudo",
      mastery_score: 20,
      tasks: [],
      references: [
        {
          id: "mdn",
          title: "MDN HTTP",
          url: "https://developer.mozilla.org/en-US/docs/Web/HTTP",
          done: false,
        },
        {
          id: "rfc",
          title: "HTTP Semantics",
          url: "https://www.rfc-editor.org/rfc/rfc9110",
          done: true,
        },
      ],
      checklist_completed: 1,
      checklist_total: 2,
    },
  ],
};

describe("Reference viewer route", () => {
  it("addresses a Reference by Node and checklist item, never by raw URL", () => {
    expect(buildReferenceViewerHref("http basics", "mdn?q=1")).toBe(
      "/reference?node=http+basics&item=mdn%3Fq%3D1",
    );
  });

  it("resolves the selected Reference with its Node and sibling References", () => {
    const resolved = resolveReferenceViewer(roadmap, "http-basics", "mdn");

    expect(resolved).toEqual({
      node: roadmap.nodes[0],
      reference: roadmap.nodes[0].references[0],
      references: roadmap.nodes[0].references,
    });
  });

  it.each([
    [null, "mdn"],
    ["http-basics", null],
    ["missing-node", "mdn"],
    ["http-basics", "missing-item"],
  ])("rejects an invalid Node + Reference address", (nodeId, itemId) => {
    expect(resolveReferenceViewer(roadmap, nodeId, itemId)).toBeNull();
  });

  it("rejects a Reference without a safe HTTP(S) URL", () => {
    const unsafeRoadmap: RoadmapResponse = {
      ...roadmap,
      nodes: [
        {
          ...roadmap.nodes[0],
          references: [
            {
              id: "unsafe",
              title: "Unsafe",
              url: "javascript:alert(1)",
              done: false,
            },
          ],
        },
      ],
    };

    expect(resolveReferenceViewer(unsafeRoadmap, "http-basics", "unsafe")).toBeNull();
  });

  it("defaults every external source to the card until its domain is allowlisted", () => {
    expect(
      isEmbeddableReferenceUrl(
        "https://developer.mozilla.org/en-US/docs/Web/HTTP",
        [],
      ),
    ).toBe(false);
  });

  it("matches allowlisted domains and their subdomains without matching lookalikes", () => {
    const allowedDomains = ["video.example.com"];

    expect(
      isEmbeddableReferenceUrl(
        "https://player.video.example.com/embed/123",
        allowedDomains,
      ),
    ).toBe(true);
    expect(
      isEmbeddableReferenceUrl(
        "https://video.example.com/embed/123",
        allowedDomains,
      ),
    ).toBe(true);
    expect(
      isEmbeddableReferenceUrl(
        "https://video.example.com.evil.test/embed/123",
        allowedDomains,
      ),
    ).toBe(false);
  });

  it("formats a source hostname for the fallback card", () => {
    expect(getReferenceHostname("https://www.roadmap.sh/pdfs/ai.pdf")).toBe(
      "roadmap.sh",
    );
  });
});
