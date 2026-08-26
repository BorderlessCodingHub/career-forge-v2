// @vitest-environment jsdom

import { cleanup, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";

import { CtaSection } from "./CtaSection";
import { Navbar } from "./Navbar";

afterEach(cleanup);

describe("welcome brand marks", () => {
  it("renders the Borderless brand mark in the navbar", () => {
    render(<Navbar />);

    const mark = screen.getByTestId("brand-mark");
    expect(mark.getAttribute("src")).toBe("/brand/borderless-logo.svg");
    expect(mark.getAttribute("alt")).toBe("Borderless");
  });

  it("renders the Borderless brand mark in the CTA section", () => {
    render(<CtaSection />);

    const mark = screen.getByTestId("brand-mark");
    expect(mark.getAttribute("src")).toBe("/brand/borderless-logo.svg");
    expect(mark.getAttribute("alt")).toBe("Borderless");
  });
});
