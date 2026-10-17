// @vitest-environment jsdom

import { cleanup, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

vi.mock("next/navigation", () => ({
  useRouter: () => ({ refresh: vi.fn() }),
}));

import { LegalDocument } from "@/components/legal/LegalDocument";
import { Footer } from "@/components/marketing/welcome/Footer";
import type { LegalPageId } from "@/content/legal";

afterEach(() => {
  cleanup();
  delete (globalThis as { __cfLocale?: string }).__cfLocale;
});

function portuguese() {
  (globalThis as { __cfLocale?: string }).__cfLocale = "pt-BR";
}

describe("welcome footer legal links", () => {
  it("opens the public privacy, terms, and security routes", () => {
    render(<Footer />);

    expect(screen.getByRole("link", { name: "Privacy Policy" }).getAttribute("href")).toBe(
      "/legal/privacy",
    );
    expect(screen.getByRole("link", { name: "Terms of Service" }).getAttribute("href")).toBe(
      "/legal/terms",
    );
    expect(screen.getByRole("link", { name: "Security" }).getAttribute("href")).toBe(
      "/legal/security",
    );
  });

  it("keeps the same routes when the footer is Portuguese", () => {
    portuguese();
    render(<Footer />);

    expect(
      screen.getByRole("link", { name: "Política de privacidade" }).getAttribute("href"),
    ).toBe("/legal/privacy");
    expect(screen.getByRole("link", { name: "Termos de serviço" }).getAttribute("href")).toBe(
      "/legal/terms",
    );
    expect(screen.getByRole("link", { name: "Segurança" }).getAttribute("href")).toBe(
      "/legal/security",
    );
  });
});

const LEFT_OUT =
  /Discord|Vimeo|Google Meet|Appmax|PandaVideo|Go Global|cookie banner|\/legal\/cookies|\/legal\/vendors/i;

function page(id: LegalPageId) {
  render(<LegalDocument page={id} />);
}

function hrefs(name: string): string[] {
  return screen.getAllByRole("link", { name }).map((link) => link.getAttribute("href") ?? "");
}

describe("legal pages", () => {
  it("states the Career Forge refund in terms section 6", () => {
    page("terms");

    expect(screen.getByRole("heading", { name: "6. Refund and cancellation" })).toBeTruthy();
    expect(screen.getByText("This section is the refund text for Career Forge.")).toBeTruthy();
    expect(
      screen.getByText(
        "The external subscription is USD $7/month via Stripe. BASE and PSP are not charged for Career Forge.",
      ),
    ).toBeTruthy();
    expect(screen.getByText("The first forge on an external account is included.")).toBeTruthy();
    expect(
      screen.getByText(
        "Amounts already charged are not refunded. The Borderless 7-day cohort window does not apply.",
      ),
    ).toBeTruthy();
    expect(
      screen.getByText(
        "Cancellation is in the Stripe customer portal. Paid access follows the subscription status.",
      ),
    ).toBeTruthy();
    expect(screen.getByText(/at least 18 years old/)).toBeTruthy();
    expect(screen.getByText(/State of Wyoming/)).toBeTruthy();
    expect(screen.getByText(/American Arbitration Association/)).toBeTruthy();
    expect(screen.getByText(/class-wide arbitration/)).toBeTruthy();
    expect(hrefs("Privacy Policy")).toContain("/legal/privacy");
    expect(document.body.textContent).not.toMatch(LEFT_OUT);
  });

  it("states the same refund in Portuguese", () => {
    portuguese();
    page("terms");

    expect(screen.getByRole("heading", { name: "6. Reembolso e cancelamento" })).toBeTruthy();
    expect(screen.getByText("Esta seção é o texto de reembolso do Career Forge.")).toBeTruthy();
    expect(
      screen.getByText(
        "A assinatura externa é de USD $7/mês via Stripe. BASE e PSP não são cobrados pelo Career Forge.",
      ),
    ).toBeTruthy();
    expect(screen.getByText("O primeiro forge em uma conta externa está incluído.")).toBeTruthy();
    expect(
      screen.getByText(
        "Valores já cobrados não são reembolsados. A janela de 7 dias das turmas da Borderless não se aplica.",
      ),
    ).toBeTruthy();
    expect(
      screen.getByText(
        "O cancelamento fica no portal de cliente da Stripe. O acesso pago segue o status da assinatura.",
      ),
    ).toBeTruthy();
    expect(screen.getByText(/pelo menos 18 anos/)).toBeTruthy();
    expect(screen.getByText(/Estado de Wyoming/)).toBeTruthy();
    expect(hrefs("Política de privacidade")).toContain("/legal/privacy");
    expect(document.body.textContent).not.toMatch(LEFT_OUT);
  });

  it("names the privacy categories the product stores", () => {
    page("privacy");

    expect(screen.getByRole("heading", { name: "Privacy Policy" })).toBeTruthy();
    expect(screen.getByText("Name.")).toBeTruthy();
    expect(screen.getByText("Email.")).toBeTruthy();
    expect(screen.getByText("Password hash.")).toBeTruthy();
    expect(screen.getByText("Locale.")).toBeTruthy();
    expect(
      screen.getByText("The Borderless account link, when you sign in with a Borderless account."),
    ).toBeTruthy();
    expect(screen.getByText(/Stripe customer id and the Stripe subscription id/)).toBeTruthy();
    expect(screen.getByText(/Card numbers stay at Stripe/)).toBeTruthy();
    expect(screen.getByText("The diagnosis interview.")).toBeTruthy();
    expect(screen.getByText("PDF CV text, when you upload a CV.")).toBeTruthy();
    expect(screen.getByText("The roadmap.")).toBeTruthy();
    expect(screen.getByText("Validation answers.")).toBeTruthy();
    expect(screen.getByText(/cf_locale cookie/)).toBeTruthy();
    expect(screen.getByText(/localStorage/)).toBeTruthy();
    expect(screen.getByText("Stripe, for billing.")).toBeTruthy();
    expect(screen.getByText("Resend, for email.")).toBeTruthy();
    expect(screen.getByText(/model provider \(OpenAI\)/)).toBeTruthy();
    expect(screen.getByText(/Sentry, when a DSN is set/)).toBeTruthy();
    expect(screen.getByText(/LangSmith, when tracing is on/)).toBeTruthy();
    expect(screen.getByText(/at least 18 years old/)).toBeTruthy();
    expect(hrefs("careerforgelabs@gmail.com").every((href) => href.startsWith("mailto:"))).toBe(
      true,
    );
    expect(document.body.textContent).not.toMatch(LEFT_OUT);
    expect(document.body.textContent).not.toMatch(/\/legal\/cookies|\/legal\/vendors/);
  });

  it("names those categories in Portuguese", () => {
    portuguese();
    page("privacy");

    expect(screen.getByRole("heading", { name: "Política de privacidade" })).toBeTruthy();
    expect(screen.getByText("Nome.")).toBeTruthy();
    expect(screen.getByText("E-mail.")).toBeTruthy();
    expect(screen.getByText("Hash da senha.")).toBeTruthy();
    expect(screen.getByText("Idioma.")).toBeTruthy();
    expect(
      screen.getByText("O vínculo com a conta Borderless, quando você entra com uma conta Borderless."),
    ).toBeTruthy();
    expect(screen.getByText(/identificador de cliente da Stripe/)).toBeTruthy();
    expect(screen.getByText(/números de cartão permanecem na Stripe/)).toBeTruthy();
    expect(screen.getByText("A entrevista de diagnóstico.")).toBeTruthy();
    expect(screen.getByText("O texto do CV em PDF, quando você envia um CV.")).toBeTruthy();
    expect(screen.getByText("A trilha.")).toBeTruthy();
    expect(screen.getByText("As respostas de validação.")).toBeTruthy();
    expect(screen.getByText(/cookie cf_locale/)).toBeTruthy();
    expect(screen.getByText(/localStorage/)).toBeTruthy();
    expect(screen.getByText(/provedor de modelo \(OpenAI\)/)).toBeTruthy();
    expect(screen.getByText(/Sentry, quando um DSN está definido/)).toBeTruthy();
    expect(screen.getByText(/LangSmith, quando o rastreamento está ligado/)).toBeTruthy();
    expect(screen.getByText(/pelo menos 18 anos/)).toBeTruthy();
  });

  it("limits the security page to the claims we make", () => {
    page("security");

    expect(screen.getByRole("heading", { name: "Security" })).toBeTruthy();
    expect(screen.getByText("Career Forge is served over HTTPS in transit.")).toBeTruthy();
    expect(screen.getByText("Passwords are stored as hashes.")).toBeTruthy();
    expect(
      screen.getByText("Card data is handled by Stripe and is not stored by Career Forge."),
    ).toBeTruthy();
    expect(screen.getByText("Access to production data is limited to operators.")).toBeTruthy();
    expect(screen.getByText("No method is completely secure.")).toBeTruthy();
    expect(hrefs("Privacy Policy")).toContain("/legal/privacy");
    expect(document.body.textContent).not.toMatch(
      /audit log|backup|vendor assessment|certification|SOC|ISO/i,
    );
  });

  it("limits the Portuguese security page the same way", () => {
    portuguese();
    page("security");

    expect(screen.getByRole("heading", { name: "Segurança" })).toBeTruthy();
    expect(screen.getByText("O Career Forge é servido por HTTPS em trânsito.")).toBeTruthy();
    expect(screen.getByText("As senhas são armazenadas como hashes.")).toBeTruthy();
    expect(
      screen.getByText(
        "Os dados de cartão são tratados pela Stripe e não são armazenados pelo Career Forge.",
      ),
    ).toBeTruthy();
    expect(screen.getByText("O acesso a dados de produção é limitado a operadores.")).toBeTruthy();
    expect(screen.getByText("Nenhum método é completamente seguro.")).toBeTruthy();
    expect(hrefs("Política de privacidade")).toContain("/legal/privacy");
    expect(document.body.textContent).not.toMatch(
      /log de auditoria|backup|avaliação de fornecedor|certificação|SOC|ISO/i,
    );
  });
});
