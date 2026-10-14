// @vitest-environment jsdom

import { cleanup, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

vi.mock("next/navigation", () => ({
  useRouter: () => ({ refresh: vi.fn() }),
}));

import en from "../../../../messages/en.json";
import pt from "../../../../messages/pt-BR.json";
import { Hero } from "./Hero";
import { InteractiveSandbox } from "./InteractiveSandbox";
import { Pricing } from "./Pricing";
import { WelcomeShell } from "./WelcomeShell";

afterEach(() => {
  cleanup();
  delete (globalThis as { __cfLocale?: string }).__cfLocale;
});

function portuguese() {
  (globalThis as { __cfLocale?: string }).__cfLocale = "pt-BR";
}

describe("welcome locale (CAR-143)", () => {
  it("renders the hero in Portuguese and keeps the pillar names in English", () => {
    portuguese();
    render(<Hero />);

    expect(
      screen.getByRole("heading", { name: /engenheiro de IA de elite/i }),
    ).toBeTruthy();
    expect(screen.getByText("RAG Engineering")).toBeTruthy();
    expect(screen.getByText("Fine-Tuning")).toBeTruthy();
    expect(screen.getByText("LLM Evals")).toBeTruthy();
    expect(screen.getByText("OpsLLM")).toBeTruthy();
    expect(screen.getAllByText("BASE · PSP").length).toBeGreaterThan(0);
    expect(screen.queryByText("From Software Engineer to")).toBeNull();
  });

  it("prices the Portuguese page in USD per month and keeps salaries literal", () => {
    portuguese();
    render(<WelcomeShell />);

    expect(screen.getAllByText(/USD \$7\/mês/).length).toBeGreaterThan(0);
    expect(screen.queryByText(/USD \$7\/mo/)).toBeNull();
    expect(screen.getByText("R$5,000")).toBeTruthy();
    expect(screen.getByText("US$18/hr")).toBeTruthy();
    expect(screen.getByText(/Go Global/)).toBeTruthy();
    expect(screen.getByText(/programa de mentoria do BASE/)).toBeTruthy();
    expect(screen.getAllByText(/Desenvolvedor líder \(low-code\)/).length).toBeGreaterThan(0);
    expect(screen.queryByText(/Lead Developer|Mentorship Program|sua track/)).toBeNull();
    expect(screen.getByText("Fine-Tuning Mastery")).toBeTruthy();
    expect(screen.getByText("LLM Evals & Quality")).toBeTruthy();
    expect(screen.getByText("OpsLLM & Infrastructure")).toBeTruthy();
  });

  it("follows the locale in the document title and description", () => {
    expect(en.welcome.meta.title).toBe("Welcome · Career Forge");
    expect(en.welcome.meta.description).toMatch(/only moves when you prove it/);
    expect(pt.welcome.meta.title).toBe("Bem-vindo · Career Forge");
    expect(pt.welcome.meta.description).toMatch(/quando você prova/);
  });

  it("keeps the pricing card in dollars when the locale is Portuguese", () => {
    portuguese();
    render(<Pricing />);

    expect(screen.getByText("USD $7")).toBeTruthy();
    expect(screen.getAllByText(/USD \$7\/mês/).length).toBeGreaterThan(0);
    expect(screen.queryByText(/R\$|BRL/)).toBeNull();
  });

  it("translates simulator chrome and refreshes seeded inputs with the locale", () => {
    portuguese();
    const { rerender } = render(<InteractiveSandbox />);

    expect(screen.getByText("CONSULTA FINANCEIRA / REGULATÓRIA DE TESTE:")).toBeTruthy();
    expect(screen.getByText("DOCUMENTOS DE CONTEXTO RECUPERADOS:")).toBeTruthy();
    expect(screen.getByDisplayValue(/margem líquida de lucro/)).toBeTruthy();

    delete (globalThis as { __cfLocale?: string }).__cfLocale;
    rerender(<InteractiveSandbox />);

    expect(screen.getByText("TEST FINANCIAL / REGULATORY QUERY:")).toBeTruthy();
    expect(screen.getByDisplayValue(/Acme Corp's net cloud profit margin/)).toBeTruthy();
  });
});
