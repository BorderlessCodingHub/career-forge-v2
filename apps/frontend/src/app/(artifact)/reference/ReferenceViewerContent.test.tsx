// @vitest-environment jsdom

import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import {
  getReferenceEmbedHosts,
  getRoadmap,
  patchRoadmapChecklist,
} from "@/lib/api-client";
import {
  REFERENCE_PREVIEW_REFERRER_POLICY,
  REFERENCE_PREVIEW_SANDBOX,
} from "@/lib/reference-viewer";
import type { RoadmapResponse } from "@/types/contracts";

import ReferenceViewerContent from "./ReferenceViewerContent";

const navigation = vi.hoisted(() => ({
  router: { replace: vi.fn() },
  searchParams: new URLSearchParams(),
}));

vi.mock("next/navigation", () => ({
  useRouter: () => navigation.router,
  useSearchParams: () => navigation.searchParams,
}));

vi.mock("@/lib/api-client", () => ({
  getReferenceEmbedHosts: vi.fn(),
  getRoadmap: vi.fn(),
  patchRoadmapChecklist: vi.fn(),
}));

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
          outcome: "Understand HTTP semantics and request lifecycles.",
          done: false,
        },
        {
          id: "rfc",
          title: "HTTP Semantics",
          url: "https://www.rfc-editor.org/rfc/rfc9110",
          done: false,
        },
      ],
      checklist_completed: 0,
      checklist_total: 2,
    },
  ],
};

beforeEach(() => {
  navigation.router.replace.mockReset();
  navigation.searchParams = new URLSearchParams();
  vi.mocked(getReferenceEmbedHosts).mockReset();
  vi.mocked(getReferenceEmbedHosts).mockResolvedValue([]);
  vi.mocked(getRoadmap).mockReset();
  vi.mocked(patchRoadmapChecklist).mockReset();
});

afterEach(cleanup);

describe("ReferenceViewerContent", () => {
  it("returns an address without Node + item to the Roadmap", async () => {
    render(<ReferenceViewerContent />);

    await waitFor(() =>
      expect(navigation.router.replace).toHaveBeenCalledWith("/roadmap"),
    );
    expect(getRoadmap).not.toHaveBeenCalled();
  });

  it("shows an honest source card instead of a blank iframe for unknown hosts", async () => {
    navigation.searchParams = new URLSearchParams({
      node: "http-basics",
      item: "mdn",
    });
    vi.mocked(getRoadmap).mockResolvedValue(roadmap);

    render(<ReferenceViewerContent />);

    const card = await screen.findByTestId("reference-source-card");
    const hatch = screen.getByTestId("reference-escape-hatch");

    expect(card.textContent).toContain("MDN HTTP");
    expect(card.textContent).toContain("Source: developer.mozilla.org");
    expect(card.textContent).toContain(
      "Understand HTTP semantics and request lifecycles.",
    );
    expect(screen.queryByTestId("reference-preview")).toBeNull();
    expect(hatch.getAttribute("href")).toBe(
      "https://developer.mozilla.org/en-US/docs/Web/HTTP",
    );
    expect(hatch.getAttribute("target")).toBe("_blank");
  });

  it("uses honest fallback copy when the Reference has no outcome", async () => {
    navigation.searchParams = new URLSearchParams({
      node: "http-basics",
      item: "rfc",
    });
    vi.mocked(getRoadmap).mockResolvedValue(roadmap);

    render(<ReferenceViewerContent />);

    const card = await screen.findByTestId("reference-source-card");
    expect(card.textContent).toContain(
      "Preview isn't available for this source. Open the original to continue studying.",
    );
  });

  it("renders the preview when the live learner allowlist contains the host", async () => {
    navigation.searchParams = new URLSearchParams({
      node: "http-basics",
      item: "mdn",
    });
    vi.mocked(getRoadmap).mockResolvedValue(roadmap);
    vi.mocked(getReferenceEmbedHosts).mockResolvedValue(["developer.mozilla.org"]);

    render(<ReferenceViewerContent />);

    const preview = await screen.findByTestId("reference-preview");
    expect(preview.getAttribute("src")).toBe(
      "https://developer.mozilla.org/en-US/docs/Web/HTTP",
    );
    expect(preview.getAttribute("sandbox")).toBe(REFERENCE_PREVIEW_SANDBOX);
    expect(preview.getAttribute("referrerpolicy")).toBe(
      REFERENCE_PREVIEW_REFERRER_POLICY,
    );
    expect(screen.queryByTestId("reference-source-card")).toBeNull();
  });

  it("uses the existing checklist command without marking done on open", async () => {
    navigation.searchParams = new URLSearchParams({
      node: "http-basics",
      item: "mdn",
    });
    vi.mocked(getRoadmap).mockResolvedValue(roadmap);
    vi.mocked(patchRoadmapChecklist).mockResolvedValue({
      ...roadmap,
      nodes: [
        {
          ...roadmap.nodes[0],
          references: [
            { ...roadmap.nodes[0].references[0], done: true },
            roadmap.nodes[0].references[1],
          ],
          checklist_completed: 1,
        },
      ],
    });

    render(<ReferenceViewerContent />);

    const checkbox = await screen.findByTestId("reference-viewer-done-mdn");
    expect((checkbox as HTMLInputElement).checked).toBe(false);
    expect(patchRoadmapChecklist).not.toHaveBeenCalled();

    fireEvent.click(checkbox);

    await waitFor(() =>
      expect(patchRoadmapChecklist).toHaveBeenCalledWith("http-basics", {
        item_type: "reference",
        item_id: "mdn",
        done: true,
      }),
    );
    await waitFor(() => expect((checkbox as HTMLInputElement).checked).toBe(true));
  });
});
