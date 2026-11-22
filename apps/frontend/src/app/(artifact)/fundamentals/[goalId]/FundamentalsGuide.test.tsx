// @vitest-environment jsdom

import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import type { ReactNode } from "react";

import { getFundamentalsGuide, openForge } from "@/lib/api-client";
import { getSelectedGoal, setSelectedGoal } from "@/lib/onboarding-session";

import FundamentalsGuide from "./FundamentalsGuide";

const navigation = vi.hoisted(() => ({
  goalId: "rag-engineer",
  push: vi.fn((href: string) => {
    navigation.goalId = href.split("/").filter(Boolean).pop() ?? navigation.goalId;
  }),
}));

vi.mock("next/navigation", () => ({
  useParams: () => ({ goalId: navigation.goalId }),
  usePathname: () => `/fundamentals/${navigation.goalId}`,
  useRouter: () => ({ push: navigation.push, refresh: vi.fn() }),
}));

vi.mock("next/link", () => ({
  default: ({
    children,
    href,
    ...rest
  }: {
    children: ReactNode;
    href: string;
  }) => (
    <a
      href={href}
      {...rest}
      onClick={(event) => {
        event.preventDefault();
        navigation.push(href);
      }}
    >
      {children}
    </a>
  ),
}));

vi.mock("@/lib/api-client", () => ({
  getFundamentalsGuide: vi.fn(),
  listFundamentals: vi.fn(async () => ({
    goals: [
      { goal_id: "rag-engineer" },
      { goal_id: "agent-engineer" },
      { goal_id: "fine-tuning" },
    ],
  })),
  openForge: vi.fn(),
  syncRoadmap: vi.fn(),
}));

const GUIDE = [
  "A production RAG system retrieves passages first, then asks the model to answer from those passages.",
  "",
  "## Retrieve before the model writes",
  "",
  "The question hits the store first.",
  "",
  "## Watch the retrieval loop",
  "",
  "https://www.youtube.com/watch?v=T-D1OfcDW1M",
  "",
].join("\n");

const AGENT_GUIDE = ["## Choose the next tool", "", "An agent chooses a tool.", ""].join("\n");
const TUNE_GUIDE = [
  "## Tune only what the prompt cannot hold",
  "",
  "A weight update does not put a new fact in the prompt.",
  "",
].join("\n");

afterEach(() => {
  cleanup();
  navigation.goalId = "rag-engineer";
  navigation.push.mockClear();
  vi.mocked(openForge).mockClear();
});

describe("Fundamentals guide", () => {
  it("shows the Goal, the guide, that guide's sections, and plays its YouTube video", async () => {
    vi.mocked(getFundamentalsGuide).mockImplementation(async (goalId, locale) => {
      expect(goalId).toBe("rag-engineer");
      expect(locale).toBe("en");
      return {
        goal_id: "rag-engineer",
        locale: "en",
        body_markdown: GUIDE,
      };
    });

    render(<FundamentalsGuide />);

    expect((await screen.findByTestId("fundamentals-goal")).textContent).toBe(
      "Production RAG & Advanced Retrieval",
    );
    const guide = screen.getByTestId("fundamentals-guide");
    expect(guide.textContent).toContain("The question hits the store first.");
    expect(guide.querySelector("#retrieve-before-the-model-writes")?.textContent).toBe(
      "Retrieve before the model writes",
    );

    const sections = screen.getByTestId("fundamentals-sections");
    const links = [...sections.querySelectorAll("a")].map((link) => ({
      text: link.textContent,
      href: link.getAttribute("href"),
    }));
    expect(links).toEqual([
      {
        text: "Retrieve before the model writes",
        href: "#retrieve-before-the-model-writes",
      },
      {
        text: "Watch the retrieval loop",
        href: "#watch-the-retrieval-loop",
      },
    ]);
    expect(sections.textContent).not.toContain("The question hits the store first.");

    const video = screen.getByTitle("YouTube video");
    expect(video.tagName).toBe("IFRAME");
    expect(video.getAttribute("src")).toBe(
      "https://www.youtube.com/embed/T-D1OfcDW1M",
    );
    expect(guide.contains(video)).toBe(true);
  });

  it("lists published Goals in catalog order and opening another leaves the Roadmap Goal", async () => {
    navigation.goalId = "fine-tuning";
    setSelectedGoal("fine-tuning");
    vi.mocked(getFundamentalsGuide).mockImplementation(async (goalId, locale) => {
      expect(locale).toBe("en");
      const bodies: Record<string, string> = {
        "rag-engineer": GUIDE,
        "agent-engineer": AGENT_GUIDE,
        "fine-tuning": TUNE_GUIDE,
      };
      return {
        goal_id: goalId,
        locale: "en",
        body_markdown: bodies[goalId] ?? GUIDE,
      };
    });

    const view = render(<FundamentalsGuide />);

    const goals = await screen.findByTestId("fundamentals-goals");
    expect(
      [...goals.querySelectorAll("a")].map((link) => ({
        text: link.textContent,
        href: link.getAttribute("href"),
      })),
    ).toEqual([
      {
        text: "Production RAG & Advanced Retrieval",
        href: "/fundamentals/rag-engineer",
      },
      { text: "Agent Engineering", href: "/fundamentals/agent-engineer" },
      { text: "Fine-Tuning & Alignment", href: "/fundamentals/fine-tuning" },
    ]);
    expect(goals.textContent).not.toContain("LLM Evaluation");
    expect((await screen.findByTestId("fundamentals-guide")).textContent).toContain(
      "A weight update does not put a new fact in the prompt.",
    );

    fireEvent.click(screen.getByRole("link", { name: "Agent Engineering" }));
    view.rerender(<FundamentalsGuide />);

    expect((await screen.findByTestId("fundamentals-guide")).textContent).toContain(
      "An agent chooses a tool.",
    );
    expect(screen.getByTestId("fundamentals-goal").textContent).toBe("Agent Engineering");
    expect(getSelectedGoal()).toBe("fine-tuning");
    expect(openForge).not.toHaveBeenCalled();
  });
});
