// @vitest-environment jsdom

import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import type { ReactNode } from "react";

import { IdentityGate } from "./IdentityGate";
import { enterPilot, requestOtp } from "@/lib/api-client";

vi.mock("next/link", () => ({
  default: ({
    children,
    href,
    ...rest
  }: {
    children: ReactNode;
    href: string;
  }) => (
    <a href={href} {...rest}>
      {children}
    </a>
  ),
}));

vi.mock("@/lib/api-client", () => ({
  enterPilot: vi.fn(),
  requestOtp: vi.fn(),
  verifyOtp: vi.fn(),
  OtpEmailOwnedError: class OtpEmailOwnedError extends Error {},
}));

afterEach(() => {
  cleanup();
});

describe("IdentityGate freeze", () => {
  beforeEach(() => {
    vi.mocked(enterPilot).mockResolvedValue({
      status: "promoted",
      access_token: "tok",
      token_type: "bearer",
      external_id: "user-pilot",
      provider: "email",
      expires_in: 3600,
    });
  });

  it("continues via pilot enter without requesting an OTP", async () => {
    const onVerified = vi.fn();
    render(<IdentityGate emailOtpRequired={false} onVerified={onVerified} />);

    fireEvent.change(screen.getByTestId("identity-gate-email"), {
      target: { value: "pilot@example.com" },
    });
    fireEvent.click(screen.getByTestId("identity-gate-continue"));

    await waitFor(() => {
      expect(enterPilot).toHaveBeenCalledWith("pilot@example.com");
      expect(onVerified).toHaveBeenCalled();
    });
    expect(requestOtp).not.toHaveBeenCalled();
    expect(screen.queryByTestId("identity-gate-request")).toBeNull();
  });
});
