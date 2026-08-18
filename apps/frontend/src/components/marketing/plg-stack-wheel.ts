/** Wheel-driven section swap on `/welcome/plg` — landpage only. */

export const PLG_STACK_HEADER_OFFSET_PX = 56;
export const PLG_STACK_WHEEL_COOLDOWN_MS = 520;
export const PLG_STACK_TRANSITION_MS = 480;

export type PlgStackWheelAction =
  | "advance"
  | "retreat"
  | "release-down"
  | "release-up"
  | "lock"
  | "ignore";

export function plgStackIsPinned(
  stackTop: number,
  stackBottom: number,
  headerOffsetPx = PLG_STACK_HEADER_OFFSET_PX,
): boolean {
  return (
    stackTop <= headerOffsetPx &&
    stackBottom > headerOffsetPx + 80
  );
}

export function plgStackWheelAction(
  deltaY: number,
  activeIndex: number,
  stepCount: number,
  stackTop: number,
  stackBottom: number,
): PlgStackWheelAction {
  if (!plgStackIsPinned(stackTop, stackBottom)) return "ignore";

  const goingDown = deltaY > 0;
  const max = Math.max(0, stepCount - 1);

  if (goingDown && activeIndex < max) return "advance";
  if (!goingDown && activeIndex > 0) return "retreat";
  if (goingDown && activeIndex >= max) return "release-down";
  if (!goingDown && activeIndex <= 0) return "release-up";
  return "lock";
}

export function plgStackPanelState(
  panelIndex: number,
  activeIndex: number,
): "before" | "active" | "after" {
  if (panelIndex === activeIndex) return "active";
  if (panelIndex < activeIndex) return "before";
  return "after";
}
