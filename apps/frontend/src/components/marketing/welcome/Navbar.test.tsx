// @vitest-environment jsdom

import { cleanup, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import { CtaSection } from "./CtaSection";
import { Navbar } from "./Navbar";

afterEach(cleanup);

function renderNavbar() {
  return render(
    <Navbar
      onOpenApplyModal={vi.fn()}
      onOpenSyllabusModal={vi.fn()}
      onOpenStrategyModal={vi.fn()}
    />,
  );
}

describe("welcome brand marks", () => {
  it("renders the Borderless brand mark in the navbar", () => {
    renderNavbar();

    const mark = screen.getByTestId("brand-mark");
    expect(mark.getAttribute("src")).toBe("/brand/borderless-logo.svg");
    expect(mark.getAttribute("alt")).toBe("Borderless");
  });

  it("renders the Borderless brand mark in the CTA section", () => {
    render(<CtaSection onOpenStrategyModal={vi.fn()} />);

    const mark = screen.getByTestId("brand-mark");
    expect(mark.getAttribute("src")).toBe("/brand/borderless-logo.svg");
    expect(mark.getAttribute("alt")).toBe("Borderless");
  });
});
