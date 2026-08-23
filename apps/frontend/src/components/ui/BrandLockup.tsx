import Link from "next/link";

import { BrandMark } from "@/components/ui/BrandMark";

type BrandLockupProps = {
  /** Pixel height for the mark; width scales with SVG aspect. */
  markSize?: number;
  className?: string;
};

export function BrandLockup({ markSize = 36, className = "" }: BrandLockupProps) {
  return (
    <Link
      href="/"
      className={`flex items-center gap-3 hover:opacity-90 ${className}`.trim()}
      data-testid="brand-lockup"
    >
      <BrandMark size={markSize} style={{ height: markSize, width: "auto" }} />
      <div>
        <p className="text-sm font-semibold text-text-primary">Career Forge</p>
        <p className="text-xs text-text-muted">Borderless Labs</p>
      </div>
    </Link>
  );
}
