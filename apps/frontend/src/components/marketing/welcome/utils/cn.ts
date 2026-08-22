import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

/** Welcome-local className helper (CAR-51) — not a global frontend util. */
export function cn(...inputs: ClassValue[]): string {
  return twMerge(clsx(inputs));
}
