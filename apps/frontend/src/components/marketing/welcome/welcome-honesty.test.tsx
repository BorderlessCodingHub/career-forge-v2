// @vitest-environment jsdom

import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";

import { CtaSection } from "./CtaSection";
import { FaqSection } from "./FaqSection";
import { Footer } from "./Footer";
import { Hero } from "./Hero";
import { Mentors } from "./Mentors";
import { Navbar } from "./Navbar";
import { Pricing } from "./Pricing";
import { RoiCalculator } from "./RoiCalculator";
import { SocialProof } from "./SocialProof";
import { WelcomeShell } from "./WelcomeShell";

afterEach(cleanup);

function isProductEntryHref(href: string | null): boolean {
  return href === "/" || href === "/career-forge" || href === "/career-forge/";
}

describe("welcome honesty — navbar bar (CAR-91)", () => {
  it("shows BASE · PSP included copy and Start diagnosis to product entry", () => {
    render(<Navbar />);

    expect(screen.getByText("BASE · PSP")).toBeTruthy();
    expect(
      screen.getByText(
        "Members: Career Forge is included. Start diagnosis with your member email.",
      ),
    ).toBeTruthy();

    const barCta = screen.getByTestId("welcome-bar-cta");
    expect(barCta.getAttribute("aria-label")).toBe("Start diagnosis");
    expect(barCta.textContent).toMatch(/^Start/);
    expect(isProductEntryHref(barCta.getAttribute("href"))).toBe(true);

    expect(screen.queryByText(/COHORT 12/i)).toBeNull();
    expect(screen.queryByText(/Claim Scholarship/i)).toBeNull();
    expect(screen.queryByText(/Early Bird/i)).toBeNull();
  });

  it("uses Stories and Access nav labels and has no download CTAs", () => {
    render(<Navbar />);

    expect(screen.getAllByText("Stories").length).toBeGreaterThan(0);
    expect(screen.getAllByText("Access").length).toBeGreaterThan(0);
    expect(screen.queryByText("Alumni Success")).toBeNull();
    expect(screen.queryByText("Tuition & Plans")).toBeNull();

    expect(screen.queryByText(/Download/i)).toBeNull();
    expect(screen.getAllByText("12-Week Syllabus").length).toBeGreaterThan(0);
  });

  it("header CTAs do not overlap: shimmer is lg-only and drawer has no Start", () => {
    render(<Navbar />);

    const headerStarts = screen.getAllByTestId("welcome-cta-start");
    expect(headerStarts).toHaveLength(2);
    expect(headerStarts[0].parentElement?.className).toContain("lg:flex");
    expect(headerStarts[0].parentElement?.className).not.toContain("md:flex");
    expect(headerStarts[1].parentElement?.className).toContain("lg:hidden");
    expect(headerStarts[1].textContent?.trim()).toBe("Start here");
    expect(headerStarts[1].getAttribute("aria-label")).toBe("Start diagnosis");

    fireEvent.click(screen.getByRole("button", { name: "Open navigation" }));
    expect(screen.getByText("Live AI Sandbox Demo")).toBeTruthy();
    expect(screen.getAllByTestId("welcome-cta-start")).toHaveLength(2);
  });
});

describe("welcome honesty — hero, proof, pricing", () => {
  it("hero badge and stats are product facts, not cohort theater", () => {
    render(<Hero />);

    expect(screen.getAllByText("BASE · PSP").length).toBeGreaterThan(0);
    expect(screen.getByText("Included for members")).toBeTruthy();
    expect(screen.getByText("4 tracks")).toBeTruthy();
    expect(screen.getByText("Diagnosis")).toBeTruthy();
    expect(screen.getByText("Live Forge")).toBeTruthy();
    expect(screen.queryByText(/8 SEATS/i)).toBeNull();
    expect(screen.queryByText(/SAVE \$500/i)).toBeNull();
    expect(screen.queryByText(/640\+/)).toBeNull();

    expect(screen.queryByText(/Download/i)).toBeNull();
    const curriculum = screen.getByRole("link", {
      name: /See 12-week syllabus/i,
    });
    expect(curriculum.getAttribute("href")).toBe("#curriculum");
    expect(screen.queryByText(/Strategy Call/i)).toBeNull();
  });

  it("social proof credits Borderless employers with local logos", () => {
    render(<SocialProof />);

    expect(
      screen.getByText(/Companies where Borderless BASE & PSP talents work/i),
    ).toBeTruthy();
    expect(screen.queryByText(/LIVE ALUMNI OFFER/i)).toBeNull();
    expect(screen.queryByText(/OpenAI/)).toBeNull();

    for (const name of [
      "Coca-Cola",
      "Apple",
      "Beehiiv",
      "Strike",
      "PayPal",
      "X-Team",
      "Pizza Hut",
      "Accenture",
      "Nubank",
      "BTG Pactual",
    ]) {
      const img = screen.getByAltText(name);
      expect(img.getAttribute("src")).toMatch(/\/welcome\/employers\//);
    }
  });

  it("mentors are the real Borderless team", () => {
    render(<Mentors />);

    expect(screen.getByText("Yuri Pereira")).toBeTruthy();
    expect(screen.getByText("Pedro Alano")).toBeTruthy();
    expect(screen.queryByText("Thiago Dantas")).toBeNull();
    expect(screen.queryByText("Matheus Avi")).toBeNull();
    expect(screen.queryByText("Dr. Marcus Vance")).toBeNull();
    expect(screen.queryByText(/EX-TOP LABS/)).toBeNull();
    expect(screen.queryByText(/GitHub Profile/)).toBeNull();
  });

  it("pricing is BASE/PSP included and External $10–15/mo", () => {
    render(<Pricing />);

    expect(screen.getByText("BASE · PSP")).toBeTruthy();
    expect(screen.getByText("External")).toBeTruthy();
    expect(screen.getByText(/Most common path/i)).toBeTruthy();
    expect(screen.getAllByText("$10–15").length).toBeGreaterThan(0);
    expect(screen.queryByText("$2,999")).toBeNull();
    expect(screen.queryByText(/SAVE \$500/i)).toBeNull();
    expect(screen.queryByText(/GPU/i)).toBeNull();

    const ctas = screen.getAllByRole("link", { name: /Start diagnosis/i });
    expect(ctas.length).toBe(2);
    for (const cta of ctas) {
      expect(isProductEntryHref(cta.getAttribute("href"))).toBe(true);
    }
  });
});

describe("welcome honesty — CTA, FAQ, ROI, shell", () => {
  it("final CTA chips are membership truth and has no Strategy Call", () => {
    render(<CtaSection />);

    expect(screen.getByText(/BASE · PSP included/i)).toBeTruthy();
    expect(screen.getByText(/\$10–15\/mo/)).toBeTruthy();
    expect(screen.queryByText(/April 14/)).toBeNull();
    expect(screen.queryByText(/8 Seats/i)).toBeNull();
    expect(screen.queryByText(/Strategy Call/i)).toBeNull();
  });

  it("FAQ answers membership, start path, and no GPU/job guarantee", () => {
    render(<FaqSection />);

    expect(screen.getByText(/Who is Career Forge for/i)).toBeTruthy();
    expect(screen.getByText(/not a prompt course/i)).toBeTruthy();
    expect(screen.getByText(/How do I start/i)).toBeTruthy();
    expect(screen.getByText(/What does the product do/i)).toBeTruthy();
    expect(screen.getByText(/Do I need a GPU/i)).toBeTruthy();
    expect(screen.getByText(/job or refund guarantee/i)).toBeTruthy();
    expect(screen.queryByText(/\$500 in cloud GPU/i)).toBeNull();
    expect(screen.queryByText(/14-day no-questions-asked/i)).toBeNull();
  });

  it("ROI payback uses $15/mo and drops 640+", () => {
    render(<RoiCalculator />);

    expect(screen.getAllByText(/\$15\/mo/).length).toBeGreaterThan(0);
    expect(screen.queryByText(/640\+/)).toBeNull();
    const cta = screen.getByRole("link", { name: /Start diagnosis/i });
    expect(isProductEntryHref(cta.getAttribute("href"))).toBe(true);
  });

  it("footer chip and conversion links are honest", () => {
    render(<Footer />);

    expect(screen.getByText(/\$10–15/)).toBeTruthy();
    expect(screen.queryByText(/Cohort 12/i)).toBeNull();
    expect(screen.getByRole("heading", { name: "Get started" })).toBeTruthy();
    const diagnosis = screen.getByRole("link", { name: /Start diagnosis/i });
    expect(isProductEntryHref(diagnosis.getAttribute("href"))).toBe(true);
    expect(screen.getByRole("link", { name: "Access" }).getAttribute("href")).toBe(
      "#pricing",
    );
    expect(screen.getByRole("link", { name: "Stories" }).getAttribute("href")).toBe(
      "#testimonials",
    );
  });

  it("Welcome shell has no apply, strategy, or syllabus modals", () => {
    render(<WelcomeShell />);

    expect(screen.queryByText(/Claim Scholarship/i)).toBeNull();
    expect(screen.queryByText(/Book 1-on-1 Strategy Call/i)).toBeNull();
    expect(document.querySelector("[data-screen='marketing-welcome']")).toBeTruthy();
    expect(screen.queryByRole("dialog")).toBeNull();
  });
});
