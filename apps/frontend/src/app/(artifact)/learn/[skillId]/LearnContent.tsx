"use client";

import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import { useEffect, useMemo, useState } from "react";

import { getCanonicalContent } from "@/lib/api-client";
import type { CanonicalBlock } from "@/lib/canonical-content";
import { parseCanonicalMarkdown } from "@/lib/canonical-content";
import { learnAssetSrc } from "@/lib/learn-assets";
import type { CanonicalPage } from "@/types/contracts";

function CanonicalQuiz({
  block,
}: {
  block: Extract<CanonicalBlock, { type: "quiz" }>;
}) {
  const [picked, setPicked] = useState<string | null>(null);

  return (
    <div
      className="space-y-3 rounded-md border border-border bg-surface px-4 py-3"
      data-testid="canonical-quiz"
    >
      {block.prompt ? (
        <p className="text-sm font-medium text-text-primary">{block.prompt}</p>
      ) : null}
      <div className="flex flex-col gap-2">
        {block.options.map((option) => {
          const selected = picked === option.key;
          const isCorrect = option.key === block.correct;
          const stateClass = !picked
            ? "border-border text-text-secondary hover:border-accent-mint"
            : isCorrect
              ? "border-accent-mint text-text-primary"
              : selected
                ? "border-border text-text-muted line-through"
                : "border-border text-text-muted";
          return (
            <button
              key={option.key}
              type="button"
              disabled={picked !== null}
              className={`rounded-md border px-3 py-2 text-left text-sm ${stateClass}`}
              onClick={() => setPicked(option.key)}
            >
              {option.key}) {option.text}
            </button>
          );
        })}
      </div>
      {picked ? (
        <p className="text-sm leading-6 text-text-secondary">
          {picked === block.correct ? "Correct. " : "Incorrect. "}
          {block.why}
        </p>
      ) : null}
    </div>
  );
}

function CanonicalBlockView({ block }: { block: CanonicalBlock }) {
  if (block.type === "heading") {
    const Heading = block.level === 1 ? "h2" : block.level === 2 ? "h3" : "h4";
    return <Heading className="font-semibold text-text-primary">{block.text}</Heading>;
  }
  if (block.type === "list") {
    return (
      <ul className="list-disc space-y-1 pl-5">
        {block.items.map((item) => (
          <li key={item}>{item}</li>
        ))}
      </ul>
    );
  }
  if (block.type === "code") {
    return (
      <pre className="overflow-x-auto rounded-md border border-border bg-surface px-3 py-3 font-mono text-sm text-text-primary">
        <code>{block.text}</code>
      </pre>
    );
  }
  if (block.type === "figure") {
    return (
      <figure>
        <img
          src={learnAssetSrc(block.src)}
          alt={block.alt}
          className="w-full rounded-md border border-border bg-surface"
        />
      </figure>
    );
  }
  if (block.type === "callout") {
    return (
      <aside className="space-y-1 rounded-md border border-border bg-surface px-4 py-3">
        {block.label ? (
          <p className="text-xs font-semibold uppercase tracking-widest text-accent-mint">
            {block.label}
          </p>
        ) : null}
        {block.text ? <p className="text-sm leading-6">{block.text}</p> : null}
      </aside>
    );
  }
  if (block.type === "quiz") {
    return <CanonicalQuiz block={block} />;
  }
  return <p className="text-sm leading-7">{block.text}</p>;
}

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
      <h1 className="mt-4 text-2xl font-semibold leading-snug text-text-primary">{page.title}</h1>
      <article className="mt-6 space-y-5 text-text-secondary">
        {blocks.map((block, index) => (
          <CanonicalBlockView key={index} block={block} />
        ))}
      </article>
    </main>
  );
}
