"use client";

import {
  Children,
  cloneElement,
  isValidElement,
  useCallback,
  useEffect,
  useRef,
  useState,
  type ReactElement,
  type ReactNode,
} from "react";

import { PlgScrollPlaque } from "./PlgScrollPlaque";
import {
  PLG_STACK_WHEEL_COOLDOWN_MS,
  plgStackIsPinned,
  plgStackPanelState,
  plgStackWheelAction,
} from "./plg-stack-wheel";

type PlgStackScrollProps = {
  labels: readonly string[];
  sectionIds: readonly string[];
  hero: ReactNode;
  children: ReactNode;
};

type PanelProps = {
  id?: string;
  "data-plg-step"?: number;
  className?: string;
  children?: ReactNode;
};

export function PlgStackScroll({
  labels,
  sectionIds,
  hero,
  children,
}: PlgStackScrollProps) {
  const rootRef = useRef<HTMLDivElement>(null);
  const lockYRef = useRef<number | null>(null);
  const activeRef = useRef(0);
  const lockedRef = useRef(false);
  const cooldownRef = useRef(false);
  const touchStartYRef = useRef<number | null>(null);

  const [activeIndex, setActiveIndex] = useState(0);

  const stepCount = sectionIds.length;

  const setStep = useCallback((next: number) => {
    const clamped = Math.max(0, Math.min(stepCount - 1, next));
    activeRef.current = clamped;
    setActiveIndex(clamped);
  }, [stepCount]);

  useEffect(() => {
    activeRef.current = activeIndex;
  }, [activeIndex]);

  useEffect(() => {
    const root = rootRef.current;
    if (!root) return;

    const readGeometry = () => root.getBoundingClientRect();

    const applyScrollLock = () => {
      if (lockYRef.current === null) return;
      if (window.scrollY !== lockYRef.current) {
        window.scrollTo(0, lockYRef.current);
      }
    };

    const engageLock = () => {
      if (lockYRef.current === null) {
        lockYRef.current = window.scrollY;
      }
      lockedRef.current = true;
      document.documentElement.style.overflow = "hidden";
      applyScrollLock();
    };

    const releaseLock = () => {
      lockedRef.current = false;
      lockYRef.current = null;
      document.documentElement.style.overflow = "";
    };

    const runWheelAction = (deltaY: number) => {
      const { top, bottom } = readGeometry();
      const action = plgStackWheelAction(
        deltaY,
        activeRef.current,
        stepCount,
        top,
        bottom,
      );

      if (action === "ignore") {
        releaseLock();
        return false;
      }

      if (action === "release-up" || action === "release-down") {
        releaseLock();
        window.scrollBy(0, deltaY);
        return true;
      }

      if (cooldownRef.current) {
        engageLock();
        return true;
      }

      if (action === "advance") {
        engageLock();
        setStep(activeRef.current + 1);
        cooldownRef.current = true;
        window.setTimeout(() => {
          cooldownRef.current = false;
        }, PLG_STACK_WHEEL_COOLDOWN_MS);
        return true;
      }

      if (action === "retreat") {
        engageLock();
        setStep(activeRef.current - 1);
        cooldownRef.current = true;
        window.setTimeout(() => {
          cooldownRef.current = false;
        }, PLG_STACK_WHEEL_COOLDOWN_MS);
        return true;
      }

      engageLock();
      return true;
    };

    const onWheel = (event: WheelEvent) => {
      const consumed = runWheelAction(event.deltaY);
      if (consumed) {
        event.preventDefault();
        applyScrollLock();
      }
    };

    const onScroll = () => {
      const { top, bottom } = readGeometry();
      const pinned = plgStackIsPinned(top, bottom);

      if (!pinned) {
        releaseLock();
        return;
      }

      if (lockedRef.current) {
        applyScrollLock();
      }
    };

    const onTouchStart = (event: TouchEvent) => {
      touchStartYRef.current = event.touches[0]?.clientY ?? null;
    };

    const onTouchMove = (event: TouchEvent) => {
      const startY = touchStartYRef.current;
      const currentY = event.touches[0]?.clientY;
      if (startY === null || currentY === undefined) return;

      const deltaY = startY - currentY;
      if (Math.abs(deltaY) < 12) return;

      const consumed = runWheelAction(deltaY);
      if (consumed) {
        event.preventDefault();
        applyScrollLock();
        touchStartYRef.current = currentY;
      }
    };

    const { top, bottom } = readGeometry();
    if (plgStackIsPinned(top, bottom)) {
      engageLock();
    }

    window.addEventListener("wheel", onWheel, { passive: false });
    window.addEventListener("scroll", onScroll, { passive: true });
    window.addEventListener("touchstart", onTouchStart, { passive: true });
    window.addEventListener("touchmove", onTouchMove, { passive: false });

    return () => {
      document.documentElement.style.overflow = "";
      window.removeEventListener("wheel", onWheel);
      window.removeEventListener("scroll", onScroll);
      window.removeEventListener("touchstart", onTouchStart);
      window.removeEventListener("touchmove", onTouchMove);
    };
  }, [setStep, stepCount]);

  const panels = Children.toArray(children).filter(isValidElement) as ReactElement<PanelProps>[];

  return (
    <div
      ref={rootRef}
      className="plg-stack-scroll"
      data-active-step={activeIndex}
      data-testid="plg-stack-scroll"
    >
      <div className="plg-stack-pin">
        <div className="plg-hero-fold" data-testid="plg-hero-fold">
          {hero}
        </div>

        <PlgScrollPlaque labels={labels} activeIndex={activeIndex} />

        <div className="plg-stack-viewport" data-testid="plg-stack-viewport">
          {panels.map((panel, index) => {
            const state = plgStackPanelState(index, activeIndex);
            const mergedClassName = [
              "plg-stack-panel",
              panel.props.className ?? "",
            ]
              .filter(Boolean)
              .join(" ");

            return cloneElement(panel, {
              key: panel.props.id ?? index,
              className: mergedClassName,
              "data-plg-step": index,
              "data-plg-state": state,
              "aria-hidden": state !== "active",
            });
          })}
        </div>
      </div>
    </div>
  );
}
