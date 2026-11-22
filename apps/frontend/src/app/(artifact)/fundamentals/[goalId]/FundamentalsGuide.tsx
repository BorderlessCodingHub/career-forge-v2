"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useLocale, useTranslations } from "next-intl";
import { useEffect, useState } from "react";

import { getFundamentalsGuide, listFundamentals } from "@/lib/api-client";
import { fundamentalsPath } from "@/lib/fundamentals";
import { parseFundamentalsMarkdown } from "@/lib/fundamentals-markdown";
import { trackMessageKey } from "@/lib/goal-copy";
import type { Locale } from "@/lib/locale";
import type {
  FundamentalsCatalog,
  FundamentalsGuide as FundamentalsGuidePage,
} from "@/types/contracts";

export default function FundamentalsGuide() {
  const params = useParams<{ goalId: string }>();
  const goalId = params.goalId;
  const locale = useLocale() as Locale;
  const tGoal = useTranslations("goal");
  const t = useTranslations("fundamentals");
  const [page, setPage] = useState<FundamentalsGuidePage | null>(null);
  const [catalog, setCatalog] = useState<FundamentalsCatalog | null>(null);

  useEffect(() => {
    let cancelled = false;
    void (async () => {
      try {
        const guide = await getFundamentalsGuide(goalId, locale);
        if (!cancelled) setPage(guide);
      } catch {
        try {
          const index = await listFundamentals();
          const first = index.goals[0]?.goal_id;
          if (!first || first === goalId) {
            if (!cancelled) setPage(null);
            return;
          }
          const guide = await getFundamentalsGuide(first, locale);
          if (!cancelled) setPage(guide);
        } catch {
          if (!cancelled) setPage(null);
        }
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [goalId, locale]);

  useEffect(() => {
    let cancelled = false;
    void listFundamentals()
      .then((index) => {
        if (!cancelled) setCatalog(index);
      })
      .catch(() => {
        if (!cancelled) setCatalog(null);
      });
    return () => {
      cancelled = true;
    };
  }, []);

  if (!page) return null;

  const blocks = parseFundamentalsMarkdown(page.body_markdown);
  const sections = blocks.filter(
    (block): block is Extract<typeof block, { type: "heading" }> =>
      block.type === "heading" && block.level === 2,
  );

  return (
    <div
      className="mx-auto grid w-full max-w-6xl grid-cols-1 gap-10 px-6 py-8 md:grid-cols-[12rem_minmax(0,1fr)_14rem] md:items-start"
      data-screen="fundamentals"
      data-testid="fundamentals"
    >
      <aside className="md:sticky md:top-8">
        {catalog ? (
          <nav data-testid="fundamentals-goals" aria-label={t("goals")}>
            <ol className="space-y-2">
              {catalog.goals.map((goal) => {
                const titleKey = trackMessageKey(goal.goal_id);
                const title = titleKey ? tGoal(titleKey) : goal.goal_id;
                const open = goal.goal_id === page.goal_id;
                return (
                  <li key={goal.goal_id}>
                    <Link
                      href={fundamentalsPath(goal.goal_id)}
                      aria-current={open ? "page" : undefined}
                      data-testid={open ? "fundamentals-goal" : undefined}
                      className={
                        open
                          ? "text-sm font-semibold text-text-primary"
                          : "text-sm text-text-secondary hover:text-text-primary"
                      }
                    >
                      {title}
                    </Link>
                  </li>
                );
              })}
            </ol>
          </nav>
        ) : null}
      </aside>
      <article
        className="min-w-0 space-y-5 text-base leading-7 text-text-secondary"
        data-testid="fundamentals-guide"
      >
        {blocks.map((block, index) => {
          if (block.type === "heading") {
            const Tag = block.level === 2 ? "h2" : "h3";
            return (
              <Tag
                key={block.id}
                id={block.id}
                className="text-xl font-semibold leading-snug text-text-primary"
              >
                {block.text}
              </Tag>
            );
          }
          if (block.type === "video") {
            return (
              <iframe
                key={block.videoId}
                title="YouTube video"
                src={`https://www.youtube.com/embed/${block.videoId}`}
                className="aspect-video w-full rounded-md border border-border"
                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
                allowFullScreen
              />
            );
          }
          return <p key={index}>{block.text}</p>;
        })}
      </article>
      <nav
        className="text-sm md:sticky md:top-8"
        data-testid="fundamentals-sections"
        aria-label={t("sections")}
      >
        <ol className="space-y-2">
          {sections.map((section) => (
            <li key={section.id}>
              <a
                href={`#${section.id}`}
                className="text-text-secondary hover:text-text-primary"
              >
                {section.text}
              </a>
            </li>
          ))}
        </ol>
      </nav>
    </div>
  );
}
