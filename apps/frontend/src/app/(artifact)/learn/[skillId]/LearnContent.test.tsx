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

  it("renders published canonical markdown", async () => {
    render(<LearnContent />);

    expect(await screen.findByTestId("canonical-learn")).toBeTruthy();
    expect(screen.getByRole("heading", { name: "Chunking for RAG" })).toBeTruthy();
    expect(screen.getByText("Split documents for retrieval.")).toBeTruthy();
    expect(screen.getByTestId("learn-return-to-roadmap").getAttribute("href")).toBe(
      "/roadmap",
    );
  });

  it("returns to the Roadmap when the canônico is missing", async () => {
    vi.mocked(getCanonicalContent).mockRejectedValue(new Error("not found"));

    render(<LearnContent />);

    await waitFor(() => {
      expect(navigation.router.replace).toHaveBeenCalledWith("/roadmap");
    });
    expect(screen.queryByTestId("canonical-learn")).toBeNull();
  });
});
