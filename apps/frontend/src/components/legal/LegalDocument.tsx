"use client";

import Link from "next/link";
import { useLocale } from "next-intl";

import { LocaleSwitch } from "@/components/i18n/LocaleSwitch";
import { BrandMark } from "@/components/ui/BrandMark";
import { legalPack } from "@/content/legal";
import type { Block, LegalPageId } from "@/content/legal";
import { resolveLocale } from "@/lib/locale";

const PAGES: LegalPageId[] = ["privacy", "terms", "security"];

function BlockView({ block }: { block: Block }) {
  if (block.kind === "ul") {
    return (
      <ul className="mt-3 list-disc space-y-2 pl-5 text-sm leading-relaxed text-slate-300">
        {block.items.map((item) => (
          <li key={item}>{item}</li>
        ))}
      </ul>
    );
  }

  return (
    <p className="mt-3 text-sm leading-relaxed text-slate-300">
      {block.parts.map((part, index) => {
        if (part.kind === "text") return <span key={index}>{part.text}</span>;
        const className = "text-orange-300 underline underline-offset-2 hover:text-orange-200";
        if (part.href.startsWith("/")) {
          return (
            <Link key={index} href={part.href} className={className}>
              {part.label}
            </Link>
          );
        }
        return (
          <a key={index} href={part.href} className={className}>
            {part.label}
          </a>
        );
      })}
    </p>
  );
}

export function LegalDocument({ page }: { page: LegalPageId }) {
  const pack = legalPack(resolveLocale(useLocale()));
  const doc = pack.pages[page];

  return (
    <div className="min-h-screen bg-slate-950 text-slate-300" data-screen={`legal-${page}`}>
      <header className="border-b border-slate-800">
        <div className="mx-auto flex max-w-3xl items-center justify-between gap-4 px-4 py-6">
          <Link href="/welcome" className="flex items-center gap-2.5">
            <BrandMark size={28} />
            <span className="font-mono text-lg font-extrabold text-white">
              CAREER<span className="text-orange-400">FORGE</span>
            </span>
          </Link>
          <LocaleSwitch tone="dark" />
        </div>
        <nav aria-label={pack.navLabel} className="mx-auto flex max-w-3xl gap-4 px-4 pb-4 text-sm">
          <Link href="/welcome" className="text-slate-400 hover:text-white">
            {pack.welcomeLabel}
          </Link>
          {PAGES.map((id) => (
            <Link
              key={id}
              href={`/legal/${id}`}
              aria-current={id === page ? "page" : undefined}
              className={
                id === page ? "text-white" : "text-slate-400 underline-offset-2 hover:text-white hover:underline"
              }
            >
              {pack.nav[id]}
            </Link>
          ))}
        </nav>
      </header>

      <article className="mx-auto max-w-3xl px-4 py-10">
        <h1 className="text-3xl font-semibold text-white">{doc.title}</h1>
        <p className="mt-2 text-xs text-slate-500">{doc.updated}</p>
        {doc.sections.map((section) => (
          <section key={section.id} id={section.id} className="mt-8" aria-labelledby={`${page}-${section.id}`}>
            <h2 id={`${page}-${section.id}`} className="text-lg font-semibold text-white">
              {section.heading}
            </h2>
            {section.blocks.map((block, index) => (
              <BlockView key={`${section.id}-${index}`} block={block} />
            ))}
          </section>
        ))}
      </article>
    </div>
  );
}
