// @vitest-environment jsdom

import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import {
  addOperatorEmbedHost,
  getOperatorEmbedHosts,
  removeOperatorEmbedHost,
} from "@/lib/operator-console";
import {
  REFERENCE_PREVIEW_REFERRER_POLICY,
  REFERENCE_PREVIEW_SANDBOX,
} from "@/lib/reference-viewer";

import { EmbedHostQueue } from "./EmbedHostQueue";

vi.mock("@/lib/operator-console", () => ({
  addOperatorEmbedHost: vi.fn(),
  getOperatorEmbedHosts: vi.fn(),
  removeOperatorEmbedHost: vi.fn(),
}));

beforeEach(() => {
  vi.mocked(addOperatorEmbedHost).mockReset();
  vi.mocked(getOperatorEmbedHosts).mockReset();
  vi.mocked(removeOperatorEmbedHost).mockReset();
  vi.mocked(getOperatorEmbedHosts).mockResolvedValue({
    pending: [
      {
        host: "developer.mozilla.org",
        sample_url: "https://developer.mozilla.org/en-US/docs/Web/HTTP",
        distinct_url_count: 2,
      },
    ],
    liberated: [],
  });
});

afterEach(cleanup);

describe("EmbedHostQueue", () => {
  it("requires the Operator preview before liberating a pending host", async () => {
    vi.mocked(addOperatorEmbedHost).mockResolvedValue({
      host: "developer.mozilla.org",
      created_at: "2026-08-25T16:00:00Z",
    });
    vi.mocked(getOperatorEmbedHosts)
      .mockResolvedValueOnce({
        pending: [
          {
            host: "developer.mozilla.org",
            sample_url: "https://developer.mozilla.org/en-US/docs/Web/HTTP",
            distinct_url_count: 2,
          },
        ],
        liberated: [],
      })
      .mockResolvedValueOnce({
        pending: [],
        liberated: [
          {
            host: "developer.mozilla.org",
            created_at: "2026-08-25T16:00:00Z",
          },
        ],
      });

    render(<EmbedHostQueue />);

    const liberate = await screen.findByTestId(
      "operator-embed-liberate-developer.mozilla.org",
    );
    expect(screen.getByTestId("operator-embed-pending").textContent).toContain(
      "2 distinct URLs",
    );
    expect((liberate as HTMLButtonElement).disabled).toBe(true);

    fireEvent.click(screen.getByTestId("operator-embed-preview-developer.mozilla.org"));
    const preview = screen.getByTestId("operator-embed-preview-frame");
    expect(preview.getAttribute("sandbox")).toBe(REFERENCE_PREVIEW_SANDBOX);
    expect(preview.getAttribute("referrerpolicy")).toBe(
      REFERENCE_PREVIEW_REFERRER_POLICY,
    );
    expect((liberate as HTMLButtonElement).disabled).toBe(true);

    fireEvent.load(preview);
    expect((liberate as HTMLButtonElement).disabled).toBe(true);
    fireEvent.click(screen.getByTestId("operator-embed-preview-confirmed"));
    expect((liberate as HTMLButtonElement).disabled).toBe(false);
    fireEvent.click(liberate);

    await waitFor(() =>
      expect(addOperatorEmbedHost).toHaveBeenCalledWith("developer.mozilla.org"),
    );
    expect(
      (await screen.findByTestId("operator-embed-liberated")).textContent,
    ).toContain("developer.mozilla.org");
  });

  it("revokes a liberated host and refreshes the live queue", async () => {
    vi.mocked(getOperatorEmbedHosts)
      .mockResolvedValueOnce({
        pending: [],
        liberated: [
          {
            host: "developer.mozilla.org",
            created_at: "2026-08-25T16:00:00Z",
          },
        ],
      })
      .mockResolvedValueOnce({
        pending: [
          {
            host: "developer.mozilla.org",
            sample_url: "https://developer.mozilla.org/en-US/docs/Web/HTTP",
            distinct_url_count: 1,
          },
        ],
        liberated: [],
      });

    render(<EmbedHostQueue />);
    fireEvent.click(
      await screen.findByTestId("operator-embed-revoke-developer.mozilla.org"),
    );

    await waitFor(() =>
      expect(removeOperatorEmbedHost).toHaveBeenCalledWith("developer.mozilla.org"),
    );
    expect((await screen.findByTestId("operator-embed-pending")).textContent).toContain(
      "developer.mozilla.org",
    );
  });
});
