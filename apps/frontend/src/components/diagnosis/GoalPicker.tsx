"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";

import { DemoModeToggle } from "@/components/layout/DemoModeToggle";
import { Button } from "@/components/ui";
import { CAREER_GOALS } from "@/lib/onboarding-data";
import { setMotivation, setSelectedGoal } from "@/lib/onboarding-session";

export function GoalPicker() {
  const router = useRouter();
  const [selected, setSelected] = useState("backend");
  const [motivation, setMotivationValue] = useState(
    "Quero trabalhar com APIs para space tech — sonho em escrever os sistemas que orquestram lançamentos de foguetes.",
  );
  const [touched, setTouched] = useState(false);

  const valid = selected.length > 0 && motivation.trim().length >= 20;

  const handleContinue = () => {
    if (!valid) return;
    setSelectedGoal(selected);
    setMotivation(motivation.trim());
    router.push("/onboarding");
  };

  return (
    <main className="min-h-screen grid-dots" data-testid="goal-picker">
      <div className="mx-auto flex min-h-screen max-w-3xl flex-col justify-center px-6 py-16">
        <div className="mb-6 flex justify-end">
          <DemoModeToggle />
        </div>
        <header className="mb-8">
          <span className="text-sm uppercase tracking-wide text-text-muted">
            Passo 1 de 3
          </span>
          <h1 className="mt-2 text-4xl font-semibold tracking-tight text-text-primary md:text-5xl">
            Para onde você quer ir?
          </h1>
        </header>

        <div className="grid gap-4 sm:grid-cols-3">
          {CAREER_GOALS.map((goal) => (
            <button
              key={goal.id}
              type="button"
              data-testid={`goal-${goal.id}`}
              disabled={!goal.active}
              onClick={() => goal.active && setSelected(goal.id)}
              className={`rounded-card border p-5 text-left transition ${
                selected === goal.id
                  ? "border-accent bg-accent/10"
                  : "border-border bg-surface hover:border-accent/40"
              } ${!goal.active ? "cursor-not-allowed opacity-50" : ""}`}
            >
              <span className="text-base font-medium text-text-primary">
                {goal.title}
              </span>
              {!goal.active && (
                <span className="mt-2 block text-xs text-text-muted">Em breve</span>
              )}
            </button>
          ))}
        </div>

        <div className="mt-8">
          <label
            htmlFor="motivation"
            className="flex items-center justify-between text-sm text-text-secondary"
          >
            Por que esse caminho?
            <span className="text-text-muted">{motivation.length}/280</span>
          </label>
          <textarea
            id="motivation"
            data-testid="motivation-input"
            className="mt-2 min-h-[120px] w-full rounded-card border border-border bg-surface-elevated px-4 py-3 text-sm text-text-primary outline-none ring-accent focus:ring-2"
            placeholder="Quero trabalhar com APIs para space tech..."
            value={motivation}
            onChange={(event) => {
              setMotivationValue(event.target.value.slice(0, 280));
              setTouched(true);
            }}
          />
          {touched && motivation.trim().length < 20 && (
            <p className="mt-2 text-sm text-warning">
              Mínimo 20 caracteres para personalizar sua trilha.
            </p>
          )}
        </div>

        <div className="mt-10 flex flex-wrap items-center gap-4">
          <Button
            data-testid="start-diagnosis"
            disabled={!valid}
            onClick={handleContinue}
          >
            Começar diagnóstico →
          </Button>
          <Link
            href="/forge"
            className="text-sm text-text-muted hover:text-text-secondary"
          >
            Pular para forge (dev)
          </Link>
        </div>
      </div>
    </main>
  );
}
