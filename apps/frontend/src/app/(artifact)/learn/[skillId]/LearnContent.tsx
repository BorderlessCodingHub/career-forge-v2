"use client";

import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import { useEffect, useMemo, useState } from "react";

import { getCanonicalContent } from "@/lib/api-client";
import { parseCanonicalMarkdown } from "@/lib/canonical-content";
import type { CanonicalPage } from "@/types/contracts";

export default function LearnContent() {
  const router = useRouter();
  const params = useParams<{ skillId: string }>();
  const skillId = typeof params.skillId === "string" ? params.skillId : "";

  const [page, setPage] = useState<CanonicalPage | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!skillId) {
      router.replace("/roadmap");
      return;
    }

    let cancelled = false;
    setLoading(true);
    void getCanonicalContent(skillId)
      .then((data) => {
        if (!cancelled) setPage(data);
      })
      .catch(() => {
        if (!cancelled) router.replace("/roadmap");
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, [router, skillId]);

  const blocks = useMemo(
    () => (page ? parseCanonicalMarkdown(page.body_markdown) : []),
    [page],
  );

  if (loading) {
    return (
      <main className="min-h-screen px-4 py-20 text-center" data-screen="canonical-learn">
        <p className="text-sm text-text-muted animate-pulse">Loading…</p>
      </main>
    );
  }

  if (!page) {
    return null;
  }

  return (
    <main
      className="mx-auto min-h-screen max-w-3xl px-4 py-6 sm:px-6"
      data-screen="canonical-learn"
      data-testid="canonical-learn"
    >
      <Link
        href="/roadmap"
        className="text-xs font-semibold uppercase tracking-widest text-accent-mint hover:underline"
        data-testid="learn-return-to-roadmap"
      >
        ← Return to roadmap
      </Link>
      <h1 className="mt-4 text-2xl font-semibold text-text-primary">{page.title}</h1>
      <article className="mt-6 space-y-4 text-text-secondary">
        {blocks.map((block, index) => {
          if (block.type === "heading") {
            const Heading = block.level === 1 ? "h2" : block.level === 2 ? "h3" : "h4";
            return (
              <Heading key={index} className="font-semibold text-text-primary">
                {block.text}
              </Heading>
            );
          }
          if (block.type === "list") {
            return (
              <ul key={index} className="list-disc space-y-1 pl-5">
                {block.items.map((item) => (
                  <li key={item}>{item}</li>
                ))}
              </ul>
            );
          }
          if (block.type === "code") {
            return (
              <pre
                key={index}
                className="overflow-x-auto rounded-md border border-border bg-surface px-3 py-3 font-mono text-sm text-text-primary"
              >
                <code>{block.text}</code>
              </pre>
            );
          }
          return (
            <p key={index} className="text-sm leading-6">
              {block.text}
            </p>
          );
        })}
      </article>
    </main>
  );
}
