import { afterEach, describe, expect, it, vi } from "vitest";

vi.mock("@/lib/user-session", () => ({
  ensureAccessToken: async () => "tok",
  getAccessToken: () => "tok",
  clearAccessToken: () => undefined,
  getUserId: () => "user-1",
  setSessionFromOtp: () => undefined,
}));

import { FeedbackLimitError, submitLearnerFeedback } from "@/lib/api-client";

afterEach(() => {
  vi.unstubAllGlobals();
});

describe("submitLearnerFeedback", () => {
  it("sends the locale cookie and treats 429 as the note limit", async () => {
    const fetchMock = vi.fn(async () => new Response(null, { status: 429 }));
    vi.stubGlobal("fetch", fetchMock);

    await expect(
      submitLearnerFeedback({ message: "hello", path: "/roadmap" }),
    ).rejects.toBeInstanceOf(FeedbackLimitError);

    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining("/me/feedback"),
      expect.objectContaining({
        method: "POST",
        credentials: "include",
      }),
    );
    const body = JSON.parse(String(fetchMock.mock.calls[0]?.[1]?.body));
    expect(body).toEqual({ message: "hello", path: "/roadmap" });
    expect(body.email).toBeUndefined();
  });
});
