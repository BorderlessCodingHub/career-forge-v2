"use client";

import { useEffect, useRef, useState } from "react";

import { shouldSkipMotion } from "./welcome-motion";
import {
  PLG_PLAQUE_FLIP_HALF_MS,
  PLG_PLAQUE_FLIP_MS,
  plgPlaqueLabelIndex,
} from "./plg-plaque-spy";

type PlgScrollPlaqueProps = {
  labels: readonly string[];
  sectionIds: readonly string[];
};

type FlapPhase = "idle" | "out" | "in";

export function PlgScrollPlaque({ labels, sectionIds }: PlgScrollPlaqueProps) {
  const plaqueRef = useRef<HTMLDivElement>(null);
  const shownIndex = useRef(0);
  const targetIndex = useRef(0);
  const flipping = useRef(false);
  const timers = useRef<number[]>([]);

  const [text, setText] = useState(labels[0] ?? "");
  const [phase, setPhase] = useState<FlapPhase>("idle");
  const [dir, setDir] = useState<1 | -1>(1);

  useEffect(() => {
    const plaque = plaqueRef.current;
    if (!plaque) return;

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

    const read = () => {
      const sectionTops = sectionIds.map((id) => {
        const el = document.getElementById(id);
        return el ? el.getBoundingClientRect().top : Number.POSITIVE_INFINITY;
      });
      const next = plgPlaqueLabelIndex(
        plaque.getBoundingClientRect().bottom,
        sectionTops,
      );
      const clamped = Math.min(next, labels.length - 1);
      if (clamped === shownIndex.current && !flipping.current) return;
      targetIndex.current = clamped;
      if (!flipping.current) startFlip();
    };

    let frame = 0;
    const onScroll = () => {
      cancelAnimationFrame(frame);
      frame = requestAnimationFrame(read);
    };

    read();
    window.addEventListener("scroll", onScroll, { passive: true, capture: true });
    window.addEventListener("resize", onScroll);

    const io = new IntersectionObserver(onScroll, {
      threshold: [0, 0.1, 0.25, 0.5, 0.75, 1],
    });
    for (const id of sectionIds) {
      const el = document.getElementById(id);
      if (el) io.observe(el);
    }

    return () => {
      cancelAnimationFrame(frame);
      window.removeEventListener("scroll", onScroll, true);
      window.removeEventListener("resize", onScroll);
      io.disconnect();
      clearTimers();
    };
  }, [labels, sectionIds]);

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
      ref={plaqueRef}
      className="sticky top-14 z-30 border-b border-border-soft bg-bg/95 py-3 backdrop-blur-md"
      aria-hidden
      data-testid="plg-scroll-plaque"
    >
      <div className="mx-auto max-w-6xl px-4 sm:px-6">
        <div className="plg-plaque-board overflow-hidden rounded-card border border-border bg-surface px-4 py-3 shadow-[0_12px_40px_rgba(0,0,0,0.28)] sm:px-6">
          <p
            className={`plg-plaque-face flex min-h-[3.25rem] items-center justify-center text-center text-pretty text-lg font-semibold tracking-tight text-text-primary sm:min-h-[4rem] sm:text-2xl ${flapClass}`}
          >
            {text}
          </p>
        </div>
      </div>
    </div>
  );
}
