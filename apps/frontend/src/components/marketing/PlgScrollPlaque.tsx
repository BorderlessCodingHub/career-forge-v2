"use client";

import { useEffect, useRef, useState } from "react";

import { shouldSkipMotion } from "./welcome-motion";
import {
  PLG_PLAQUE_FLIP_HALF_MS,
  PLG_PLAQUE_FLIP_MS,
} from "./plg-plaque-spy";

type PlgScrollPlaqueProps = {
  labels: readonly string[];
  activeIndex: number;
};

type FlapPhase = "idle" | "out" | "in";

export function PlgScrollPlaque({ labels, activeIndex }: PlgScrollPlaqueProps) {
  const shownIndex = useRef(activeIndex);
  const targetIndex = useRef(activeIndex);
  const flipping = useRef(false);
  const timers = useRef<number[]>([]);

  const [text, setText] = useState(labels[activeIndex] ?? labels[0] ?? "");
  const [phase, setPhase] = useState<FlapPhase>("idle");
  const [dir, setDir] = useState<1 | -1>(1);

  useEffect(() => {
    const reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    const skip = shouldSkipMotion(reduced);

    const clearTimers = () => {
      for (const id of timers.current) window.clearTimeout(id);
      timers.current = [];
    };

    const startFlip = () => {
      const from = shownIndex.current;
      const to = targetIndex.current;
      if (from === to) {
        flipping.current = false;
        return;
      }

      const nextText = labels[to] ?? labels[0] ?? "";

      if (skip) {
        shownIndex.current = to;
        setText(nextText);
        setPhase("idle");
        flipping.current = false;
        return;
      }

      flipping.current = true;
      setDir(to > from ? 1 : -1);
      setPhase("out");

      const mid = window.setTimeout(() => {
        shownIndex.current = to;
        setText(nextText);
        setPhase("in");
      }, PLG_PLAQUE_FLIP_HALF_MS);

      const end = window.setTimeout(() => {
        setPhase("idle");
        flipping.current = false;
        if (targetIndex.current !== shownIndex.current) startFlip();
      }, PLG_PLAQUE_FLIP_MS);

      timers.current = [mid, end];
    };

    const clamped = Math.max(0, Math.min(activeIndex, labels.length - 1));
    if (clamped === shownIndex.current && !flipping.current) return;

    targetIndex.current = clamped;
    if (!flipping.current) startFlip();

    return () => clearTimers();
  }, [activeIndex, labels]);

  const flapClass =
    phase === "out"
      ? dir === 1
        ? "is-out"
        : "is-out-rev"
      : phase === "in"
        ? dir === 1
          ? "is-in"
          : "is-in-rev"
        : "";

  return (
    <div
      className="plg-stack-plaque border-b border-border-soft bg-bg/95 py-3 backdrop-blur-md"
      aria-hidden
      data-testid="plg-scroll-plaque"
    >
      <div className="mx-auto max-w-6xl px-4 sm:px-6">
        <div className="plg-plaque-board overflow-hidden rounded-card border border-border bg-surface px-4 py-3 shadow-[0_12px_40px_rgba(0,0,0,0.28)] sm:px-6">
          <p
            className={`plg-plaque-face flex min-h-[3.25rem] items-center justify-center text-center text-pretty text-lg font-semibold tracking-tight text-text-primary sm:min-h-[4rem] sm:text-2xl ${flapClass}`}
            data-testid="plg-scroll-plaque-text"
          >
            {text}
          </p>
        </div>
      </div>
    </div>
  );
}
