import { link, list, para } from "./blocks";
import type { LegalPack } from "./types";

const privacyLink = link("/legal/privacy", "Privacy Policy");
const contact = link("mailto:careerforgelabs@gmail.com", "careerforgelabs@gmail.com");

export const enLegal: LegalPack = {
  navLabel: "Legal",
  welcomeLabel: "Welcome",
  nav: {
    privacy: "Privacy Policy",
    terms: "Terms of Service",
    security: "Security",
  },
  pages: {
    terms: {
      title: "Terms of Service",
      description:
        "Terms of Service for Career Forge, operated by Borderless Coding LLC.",
      updated: "Effective date: October 17, 2026. Last updated: October 17, 2026.",
      sections: [
        {
          id: "agreement",
          heading: "Agreement",
          blocks: [
            para(
              'These Terms of Service ("Terms") are a legal agreement between you ("Customer", "you") and Borderless Coding LLC, a Wyoming limited liability company located at 30 N Gould St, STE R, Sheridan, WY 82801, USA ("Borderless Coding", "we", "us"). By creating a Career Forge account or accessing Career Forge, you agree to these Terms in full. If you do not agree, do not use Career Forge.',
            ),
          ],
        },
        {
          id: "services",
          heading: "1. Services provided",
          blocks: [
            para(
              "Borderless Coding operates Career Forge, an online adaptive learning system. Career Forge includes:",
            ),
            list(
              "A diagnosis interview that maps where you are before a roadmap is forged.",
              "A live roadmap forge for one of four LLM tracks: RAG engineer, agent engineer, LLM evals, and fine-tuning.",
              "A roadmap you follow.",
              "Mastery validation.",
              "A contextual mentor and an evidence report.",
            ),
            para(
              "Career Forge is delivered online. Nothing physical is shipped. Career Forge is the product described in these Terms.",
            ),
          ],
        },
        {
          id: "eligibility",
          heading: "2. Eligibility",
          blocks: [
            para(
              "You must be at least 18 years old to create an account or use Career Forge. By creating an account, you confirm that the information you provide is accurate and complete.",
            ),
          ],
        },
        {
          id: "account",
          heading: "3. Account and access",
          blocks: [
            para(
              "You sign in with a Career Forge password or with a Borderless account. Credentials are personal and non-transferable. You are responsible for activity under your account. We may suspend or close an account that violates these Terms.",
            ),
          ],
        },
        {
          id: "delivery",
          heading: "4. Delivery",
          blocks: [
            para(
              "Career Forge runs in the product: diagnosis, forge, roadmap, and mastery validation. The first forge on an external account is included. BASE and PSP are not charged for Career Forge. After that included forge, paid access follows the subscription status.",
            ),
          ],
        },
        {
          id: "payment",
          heading: "5. Payment",
          blocks: [
            para(
              "The external subscription is USD $7/month via Stripe. BASE and PSP are not charged for Career Forge. Card numbers are handled by Stripe and are not stored by Career Forge. A failed payment can pause paid access until the subscription is current.",
            ),
          ],
        },
        {
          id: "refund",
          heading: "6. Refund and cancellation",
          blocks: [
            para("This section is the refund text for Career Forge."),
            list(
              "The external subscription is USD $7/month via Stripe. BASE and PSP are not charged for Career Forge.",
              "The first forge on an external account is included.",
              "Amounts already charged are not refunded. The Borderless 7-day cohort window does not apply.",
              "Cancellation is in the Stripe customer portal. Paid access follows the subscription status.",
            ),
          ],
        },
        {
          id: "ip",
          heading: "7. Intellectual property",
          blocks: [
            para(
              "Career Forge software, catalogs, branding, and materials we provide are the property of Borderless Coding LLC. Your account grants a personal, non-transferable, non-exclusive license to use Career Forge for your own learning. You may not copy, redistribute, resell, or share that material for commercial use. A violation can end the account. Amounts already charged are not refunded, as section 6 states.",
            ),
          ],
        },
        {
          id: "conduct",
          heading: "8. Conduct",
          blocks: [
            para(
              "You agree to use Career Forge lawfully, to upload only material you have the right to provide, and not to disrupt the service or other learners' data. We may suspend access for a serious or repeated violation. Suspension does not refund amounts already charged.",
            ),
          ],
        },
        {
          id: "disclaimer",
          heading: "9. No employment guarantee",
          blocks: [
            para(
              "Career Forge provides adaptive learning. It is not an employment service, a recruitment service, or a job-placement guarantee. Results depend on your effort and on factors we do not control. Stories on the marketing page are individual outcomes. We do not guarantee a salary, an offer, an interview, or a timeline.",
            ),
          ],
        },
        {
          id: "liability",
          heading: "10. Limitation of liability",
          blocks: [
            para("To the maximum extent permitted by law:"),
            list(
              "Borderless Coding's total liability for any claim arising from these Terms or your use of Career Forge shall not exceed the amount you paid to Borderless Coding for Career Forge in the twelve months before the claim.",
              "We are not liable for indirect, incidental, consequential, or punitive damages, including lost income, lost opportunities, or career outcomes.",
              "We are not liable for interruptions or third-party outages beyond our reasonable control.",
            ),
          ],
        },
        {
          id: "privacy",
          heading: "11. Privacy",
          blocks: [
            para(
              "Your personal data is handled under our ",
              privacyLink,
              ". By using Career Forge, you acknowledge that policy.",
            ),
          ],
        },
        {
          id: "third-parties",
          heading: "12. Third-party services",
          blocks: [
            para(
              "Career Forge uses Stripe for billing, Resend for email, and a model provider (OpenAI) for diagnosis, forge, and validation. Sentry receives error reports when a DSN is set. LangSmith receives traces when tracing is on. We are not responsible for their terms, availability, or data practices.",
            ),
          ],
        },
        {
          id: "modifications",
          heading: "13. Modifications",
          blocks: [
            para(
              "We may update these Terms. The date at the top of this page changes when we do. Continued use of Career Forge after an update is acceptance of the updated Terms.",
            ),
          ],
        },
        {
          id: "law",
          heading: "14. Governing law and disputes",
          blocks: [
            list(
              "These Terms are governed by the laws of the State of Wyoming, United States.",
              "Any dispute is first addressed in good faith by contacting careerforgelabs@gmail.com.",
              "If it is still unresolved after 30 days, it goes to binding arbitration under the rules of the American Arbitration Association, conducted in English.",
              "You waive any right to participate in a class action or in class-wide arbitration.",
            ),
          ],
        },
        {
          id: "severability",
          heading: "15. Severability",
          blocks: [
            para(
              "If any provision of these Terms is found unenforceable, the remaining provisions remain in full effect.",
            ),
          ],
        },
        {
          id: "entire",
          heading: "16. Entire agreement",
          blocks: [
            para(
              "These Terms, including section 6 as the refund text, together with the Privacy Policy, are the entire agreement between you and Borderless Coding LLC about Career Forge.",
            ),
          ],
        },
        {
          id: "contact",
          heading: "Contact",
          blocks: [
            para("Email: ", contact),
            para("Entity: Borderless Coding LLC"),
            para("Address: 30 N Gould St, STE R, Sheridan, WY 82801, USA"),
          ],
        },
      ],
    },
    privacy: {
      title: "Privacy Policy",
      description:
        "What Career Forge stores about an account, billing, learning, and the browser, and which processors it uses.",
      updated: "Last updated: October 17, 2026.",
      sections: [
        {
          id: "intro",
          heading: "1. Introduction",
          blocks: [
            para(
              'Borderless Coding LLC ("Borderless Coding", "we"), located at 30 N Gould St, STE R, Sheridan, WY 82801, USA, operates Career Forge. This policy names what Career Forge stores and which processors handle it. You must be at least 18 years old to use Career Forge.',
            ),
          ],
        },
        {
          id: "account",
          heading: "2. Account",
          blocks: [
            para("When you create an account, Career Forge stores:"),
            list(
              "Name.",
              "Email.",
              "Password hash.",
              "Locale.",
              "The Borderless account link, when you sign in with a Borderless account.",
            ),
            para("Career Forge stores the password hash, not the password itself."),
          ],
        },
        {
          id: "billing",
          heading: "3. Billing",
          blocks: [
            para(
              "For an external subscription, Career Forge stores the Stripe customer id and the Stripe subscription id. Card numbers stay at Stripe. Career Forge does not store card numbers.",
            ),
          ],
        },
        {
          id: "learning",
          heading: "4. Learning",
          blocks: [
            para("Career Forge stores learning records you create in the product:"),
            list(
              "The diagnosis interview.",
              "PDF CV text, when you upload a CV.",
              "The roadmap.",
              "Validation answers.",
            ),
          ],
        },
        {
          id: "browser",
          heading: "5. Browser",
          blocks: [
            para(
              "Career Forge stores your locale in the cf_locale cookie. The learner access token is kept in localStorage in your browser.",
            ),
          ],
        },
        {
          id: "processors",
          heading: "6. Processors",
          blocks: [
            para("Career Forge uses these processors to run the product:"),
            list(
              "Stripe, for billing.",
              "Resend, for email.",
              "The model provider (OpenAI), for diagnosis, forge, validation, and related model calls.",
              "Sentry, when a DSN is set, for error reports.",
              "LangSmith, when tracing is on, for traces of those model runs.",
            ),
            para(
              "We share personal data with a processor so it can do that work. Career Forge does not sell personal data.",
            ),
          ],
        },
        {
          id: "use",
          heading: "7. How we use it",
          blocks: [
            para(
              "We use this data to create and sign in your account, run the diagnosis and the forge, keep your roadmap and validation answers, bill an external subscription through Stripe, and send account email through Resend.",
            ),
          ],
        },
        {
          id: "requests",
          heading: "8. Privacy requests",
          blocks: [
            para(
              "To ask for access, correction, or deletion of Career Forge personal data, email ",
              contact,
              ".",
            ),
          ],
        },
        {
          id: "security",
          heading: "9. Security",
          blocks: [
            para(
              "What we claim about protecting Career Forge is on the ",
              link("/legal/security", "Security"),
              " page. No method is completely secure.",
            ),
          ],
        },
        {
          id: "changes",
          heading: "10. Changes",
          blocks: [
            para(
              "We may update this policy. The date at the top of this page changes when we do.",
            ),
          ],
        },
        {
          id: "contact",
          heading: "11. Contact",
          blocks: [
            para("Privacy requests: ", contact),
            para("Entity: Borderless Coding LLC"),
            para("Address: 30 N Gould St, STE R, Sheridan, WY 82801, USA"),
          ],
        },
      ],
    },
    security: {
      title: "Security",
      description: "The security claims Career Forge makes.",
      updated: "Last updated: October 17, 2026.",
      sections: [
        {
          id: "claims",
          heading: "What we claim",
          blocks: [
            para(
              "Career Forge is operated by Borderless Coding LLC, 30 N Gould St, STE R, Sheridan, WY 82801, USA. This page states only the following:",
            ),
            list(
              "Career Forge is served over HTTPS in transit.",
              "Passwords are stored as hashes.",
              "Card data is handled by Stripe and is not stored by Career Forge.",
              "Access to production data is limited to operators.",
              "No method is completely secure.",
            ),
            para("How Career Forge handles personal data is described in the ", privacyLink, "."),
            para("Security questions: ", contact),
          ],
        },
      ],
    },
  },
};
