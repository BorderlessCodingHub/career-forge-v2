"use client";

import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

import { Button, Select } from "@/components/ui";
import { CAREER_GOALS } from "@/lib/onboarding-data";
import {
  clearCvAttachment,
  getCvAttachment,
  getMotivation,
  getSelectedGoal,
  getYearsXp,
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
  const [selected, setSelected] = useState("rag-engineer");
  const [motivation, setMotivationValue] = useState("");
  const [yearsXp, setYearsXpValue] = useState<YearsXpRange | "">("");
  const [cvAttachment, setCvAttachmentState] = useState<CvAttachment | null>(null);
  const [touched, setTouched] = useState(false);

  useEffect(() => {
    const storedGoal = getSelectedGoal();
    if (storedGoal) setSelected(storedGoal);
    const storedMotivation = getMotivation();
    if (storedMotivation) setMotivationValue(storedMotivation);
    const storedYearsXp = getYearsXp();
    if (storedYearsXp) setYearsXpValue(storedYearsXp);
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
            Step 1 of 3
          </span>
          <h1 className="mt-2 text-4xl font-semibold tracking-tight text-text-primary md:text-5xl">
            Where do you want to go?
          </h1>
        </header>

        <div className="grid gap-4 sm:grid-cols-2">
          {CAREER_GOALS.map((goal) => (
            <button
              key={goal.id}
              type="button"
              data-testid={`goal-${goal.id}`}
              disabled={!goal.active}
              onClick={() => goal.active && setSelected(goal.id)}
              className={`rounded-md border p-5 text-left transition ${
                selected === goal.id
                  ? "border-accent bg-accent/10"
                  : "border-border bg-surface hover:border-accent/40"
              } ${!goal.active ? "cursor-not-allowed opacity-50" : ""}`}
            >
              <span className="text-base font-medium text-text-primary">
                {goal.title}
              </span>
              {!goal.active && (
                <span className="mt-2 block text-xs text-text-muted">Coming soon</span>
              )}
            </button>
          ))}
        </div>

        <div className="mt-8">
          <label
            htmlFor="motivation"
            className="flex items-center justify-between text-sm text-text-secondary"
          >
            Why this path?
            <span className="text-text-muted">{motivation.length}/280</span>
          </label>
          <textarea
            id="motivation"
            data-testid="motivation-input"
            className="mt-2 min-h-[120px] w-full resize-none rounded-md border border-border bg-surface-elevated px-4 py-3 text-sm text-text-primary outline-none ring-accent focus:ring-2"
            placeholder="In your own words, what motivates you on this path…"
            value={motivation}
            onChange={(event) => {
              setMotivationValue(event.target.value.slice(0, 280));
              setTouched(true);
            }}
          />
          {touched && motivation.trim().length < 20 && (
            <p className="mt-2 text-sm text-warning">
              At least 20 characters so we can personalize your trail.
            </p>
          )}
        </div>

        <div className="mt-6">
          <label
            htmlFor="years-xp"
            className="text-sm text-text-secondary"
          >
            Years of experience (if applicable)
          </label>
          <Select
            id="years-xp"
            data-testid="years-xp-select"
            className="mt-2"
            value={yearsXp}
            options={YEARS_XP_OPTIONS}
            placeholder="Select…"
            onChange={(next) => {
              setYearsXpValue(next);
              setTouched(true);
            }}
          />
          {touched && !yearsXp && (
            <p className="mt-2 text-sm text-warning">
              Share your experience so we can calibrate the diagnosis.
            </p>
          )}
        </div>

        <div className="mt-6">
          <label className="text-sm text-text-secondary">
            Resume (optional)
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
            Start diagnosis →
          </Button>
        </div>
      </div>
    </main>
  );
}
