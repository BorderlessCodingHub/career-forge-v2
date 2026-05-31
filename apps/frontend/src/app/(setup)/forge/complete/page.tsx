"use client";

import Link from "next/link";
import { useEffect, useRef, useState } from "react";

import { StreamReveal } from "@/components/forge";
import { Button } from "@/components/ui";
import { getForgeGraph, type ForgeGraphNode } from "@/lib/forge-session";

export default function ForgeCompletePage() {
  const [graph, setGraph] = useState<ForgeGraphNode[] | null>(null);
  const [revealed, setRevealed] = useState(0);
  const sentinelRef = useRef<HTMLDivElement>(null);
  const autoScrollRef = useRef(true);

  useEffect(() => {
    const handleScroll = () => {
      const { scrollHeight, scrollTop, clientHeight } = document.documentElement;
      autoScrollRef.current = scrollHeight - scrollTop - clientHeight < 150;
    };
    window.addEventListener("scroll", handleScroll, { passive: true });
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  useEffect(() => {
    window.scrollTo(0, 0);
    setGraph(getForgeGraph());
  }, []);

  useEffect(() => {
    if (!graph?.length) return;
    if (revealed >= graph.length) return;
    const timer = setTimeout(() => setRevealed((n) => n + 1), 280);
    return () => clearTimeout(timer);
  }, [graph, revealed]);

  useEffect(() => {
    if (revealed === 0) return;
    if (!autoScrollRef.current) return;
    const { scrollHeight, clientHeight } = document.documentElement;
    if (scrollHeight <= clientHeight) return;
    requestAnimationFrame(() => {
      sentinelRef.current?.scrollIntoView({ behavior: "smooth" });
    });
  }, [revealed]);

  if (!graph?.length) {
    return (
      <main className="min-h-screen grid-dots p-8">
        <p className="text-text-secondary">Nenhum grafo forjado ainda.</p>
        <Link href="/forge" className="mt-4 inline-block text-accent">
          Voltar ao forge
        </Link>
      </main>
    );
  }

  const done = revealed >= graph.length;

  return (
    <main
      className="min-h-screen grid-dots px-4 py-10"
      data-screen="forge-reveal"
    >
      <div className="mx-auto max-w-2xl">
        <h1 className="text-3xl font-semibold text-text-primary">
          Sua trilha está pronta
        </h1>
        <p className="mt-2 text-text-secondary">
          Cada capítulo do seu plano aparece abaixo. Explore a trilha e comece a estudar.
        </p>

        <ol className="mt-10 space-y-4">
          {graph.slice(0, revealed).map((node) => (
            <li
              key={node.node_id}
              className="animate-[reveal_400ms_ease-out]"
              style={{ animationFillMode: "backwards" }}
            >
              <div className="rounded-md border border-border bg-surface px-4 py-3">
                <StreamReveal
                  text={`${node.title ?? node.node_id} · ${node.status} · ${node.mastery_score}%`}
                />
              </div>
            </li>
          ))}
        </ol>
        <div ref={sentinelRef} />

        {done && (
          <div className="mt-10">
            <Link href="/roadmap">
              <Button data-testid="forge-to-roadmap">
                Explorar trilha vertical →
              </Button>
            </Link>
          </div>
        )}
      </div>
    </main>
  );
}
