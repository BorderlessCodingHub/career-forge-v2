"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import { StreamReveal } from "@/components/forge";
import { Button } from "@/components/ui";
import { getForgeGraph, type ForgeGraphNode } from "@/lib/forge-session";

export default function ForgeCompletePage() {
  const [graph, setGraph] = useState<ForgeGraphNode[] | null>(null);
  const [revealed, setRevealed] = useState(0);

  useEffect(() => {
    setGraph(getForgeGraph());
  }, []);

  useEffect(() => {
    if (!graph?.length) return;
    if (revealed >= graph.length) return;
    const timer = setTimeout(() => setRevealed((n) => n + 1), 280);
    return () => clearTimeout(timer);
  }, [graph, revealed]);

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
          Cada nó do stream materializa no layout vertical (HAC-9 em seguida).
        </p>

        <ol className="mt-10 space-y-4">
          {graph.map((node, index) => (
            <li
              key={node.node_id}
              className={`transition-all duration-500 ${
                index < revealed
                  ? "translate-y-0 opacity-100"
                  : "translate-y-4 opacity-0"
              }`}
              style={{ transitionDelay: `${index * 80}ms` }}
            >
              <div className="rounded-md border border-border bg-surface px-4 py-3">
                <StreamReveal
                  text={`${node.title ?? node.node_id} · ${node.status} · ${node.mastery_score}%`}
                />
              </div>
            </li>
          ))}
        </ol>

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
