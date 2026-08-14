"use client";

import {
  useEffect,
  useRef,
  useState,
  type CSSProperties,
  type ReactNode,
} from "react";

import {
  scrollRevealClassName,
  shouldSkipMotion,
  staggerDelayMs,
} from "./welcome-motion";

type ScrollRevealProps = {
  children: ReactNode;
  className?: string;
  /** Optional stagger index within a group (40–80ms step). */
  delayIndex?: number;
  as?: "div" | "li" | "article";
};

/**
 * One-shot scroll fade-in for `/welcome` only (CAR-38).
 * Reduced-motion: visible immediately, no transform animation.
 */
export function ScrollReveal({
  children,
  className = "",
  delayIndex = 0,
  as: Tag = "div",
}: ScrollRevealProps) {
  const ref = useRef<HTMLElement | null>(null);
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;

    const reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    if (shouldSkipMotion(reduced)) {
      setVisible(true);
      return;
    }

    const io = new IntersectionObserver(
      ([entry]) => {
        if (entry?.isIntersecting) {
          setVisible(true);
          io.disconnect();
        }
      },
      { threshold: 0.12, rootMargin: "0px 0px -10% 0px" },
    );
    io.observe(el);
    return () => io.disconnect();
  }, []);

  const style: CSSProperties | undefined =
    delayIndex > 0 && visible
      ? { transitionDelay: `${staggerDelayMs(delayIndex)}ms` }
      : undefined;

  return (
    <Tag
      ref={ref as never}
      className={`${scrollRevealClassName(visible)}${className ? ` ${className}` : ""}`}
      style={style}
    >
      {children}
    </Tag>
  );
}
