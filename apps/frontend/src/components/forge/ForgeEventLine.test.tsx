// @vitest-environment jsdom

import { cleanup, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";

import { ForgeEventLine } from "./ForgeEventLine";

const providerDump =
  "Error code: 402 - {'error': {'message': 'need credits', " +
  "'user_id': 'user_example', " +
  "'url': 'https://openrouter.ai/workspaces/default/keys/" +
  "d".repeat(64) +
  "'}}";

afterEach(() => {
  cleanup();
});

describe("ForgeEventLine", () => {
  it("renders the retry sentence instead of a provider dump", () => {
    render(
      <ForgeEventLine
        event={{ type: "error", message: providerDump }}
        index={0}
      />,
    );

    expect(
      screen.getByText(
        "We couldn't finish your trail just now. Try again in a few minutes.",
      ),
    ).toBeTruthy();
    expect(screen.queryByText(/openrouter/i)).toBeNull();
    expect(screen.queryByText(/Error code/i)).toBeNull();
    expect(screen.queryByText(/user_id/i)).toBeNull();
  });
});
