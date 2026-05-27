"use client";

import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

import { Button, Select } from "@/components/ui";
import { CAREER_GOALS } from "@/lib/onboarding-data";
import {
  clearCvAttachment,
  getCvAttachment,
  setCvAttachment,
  setMotivation,
  setSelectedGoal,
  setYearsXp,
  type CvAttachment,
  type YearsXpRange,
} from "@/lib/onboarding-session";
import { YEARS_XP_OPTIONS } from "@/lib/years-xp";

import { CvDropzone } from "./CvDropzone";

export function GoalPicker() {
  const router = useRouter();
  const [selected, setSelected] = useState("backend");
  const [motivation, setMotivationValue] = useState("");
  const [yearsXp, setYearsXpValue] = useState<YearsXpRange | "">("");
  const [cvAttachment, setCvAttachmentState] = useState<CvAttachment | null>(null);
  const [touched, setTouched] = useState(false);

  useEffect(() => {
    setCvAttachmentState(getCvAttachment());
  }, []);

  const valid =
    selected.length > 0 &&
    motivation.trim().length >= 20 &&
    yearsXp.length > 0;

  const handleContinue = () => {
    if (!valid || !yearsXp) return;
    setSelectedGoal(selected);
    setMotivation(motivation.trim());
    setYearsXp(yearsXp);
    router.push("/onboarding");
  };

  return (
    <main className="min-h-screen grid-dots" data-testid="goal-picker">
      <div className="mx-auto flex min-h-screen max-w-3xl flex-col justify-center px-6 py-16">
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
            className="mt-2 min-h-[120px] w-full resize-none rounded-card border border-border bg-surface-elevated px-4 py-3 text-sm text-text-primary outline-none ring-accent focus:ring-2"
            placeholder="Conte em suas palavras o que te motiva nesse caminho…"
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

        <div className="mt-6">
          <label
            htmlFor="years-xp"
            className="text-sm text-text-secondary"
          >
            Anos de XP (se aplicável)
          </label>
          <Select
            id="years-xp"
            data-testid="years-xp-select"
            className="mt-2"
            value={yearsXp}
            options={YEARS_XP_OPTIONS}
            placeholder="Selecione…"
            onChange={(next) => {
              setYearsXpValue(next);
              setTouched(true);
            }}
          />
          {touched && !yearsXp && (
            <p className="mt-2 text-sm text-warning">
              Informe sua experiência para calibrar o diagnóstico.
            </p>
          )}
        </div>

        <div className="mt-6">
          <label className="text-sm text-text-secondary">
            Currículo (opcional)
          </label>
          <CvDropzone
            attachment={cvAttachment}
            onAttach={(attachment) => {
              setCvAttachment(attachment);
              setCvAttachmentState(attachment);
            }}
            onRemove={() => {
              clearCvAttachment();
              setCvAttachmentState(null);
            }}
          />
        </div>

        <div className="mt-10">
          <Button
            data-testid="start-diagnosis"
            disabled={!valid}
            onClick={handleContinue}
          >
            Começar diagnóstico →
          </Button>
        </div>
      </div>
    </main>
  );
}
