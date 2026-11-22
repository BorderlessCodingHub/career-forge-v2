// @vitest-environment jsdom

import { cleanup, render, screen, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { getCanonicalContent } from "@/lib/api-client";

import LearnContent from "./LearnContent";

const navigation = vi.hoisted(() => ({
  router: { replace: vi.fn() },
  skillId: "rag-chunking",
}));

vi.mock("next/navigation", () => ({
  useRouter: () => navigation.router,
  useParams: () => ({ skillId: navigation.skillId }),
}));

vi.mock("@/lib/api-client", () => ({
  getCanonicalContent: vi.fn(),
}));

afterEach(() => {
  cleanup();
  navigation.router.replace.mockReset();
  navigation.skillId = "rag-chunking";
});

describe("LearnContent", () => {
  beforeEach(() => {
    vi.mocked(getCanonicalContent).mockResolvedValue({
      skill_id: "rag-chunking",
      title: "Chunking for RAG",
      url: null,
      body_markdown: "# Body\n\nSplit documents for retrieval.",
    });
  });

  it("does not present the skill lesson", async () => {
    render(<LearnContent />);

    await waitFor(() => {
      expect(navigation.router.replace).toHaveBeenCalledWith("/roadmap");
    });
    expect(screen.queryByTestId("canonical-learn")).toBeNull();
    expect(screen.queryByRole("heading", { name: "Chunking for RAG" })).toBeNull();
    expect(screen.queryByText("Split documents for retrieval.")).toBeNull();
  });
});
