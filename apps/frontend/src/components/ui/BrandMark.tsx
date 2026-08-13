import type { ImgHTMLAttributes } from "react";

import { brandAssetPath, BRAND_LOGO_SVG } from "@/lib/brand-assets";

type BrandMarkProps = Omit<ImgHTMLAttributes<HTMLImageElement>, "src" | "alt"> & {
  /** Pixel height; width scales with SVG aspect (~501:596). */
  size?: number;
  /** `color` = official SVG; `inherit` keeps mark but softens for dense chrome. */
  variant?: "color" | "inherit";
  alt?: string;
};

export function BrandMark({
  size = 36,
  variant = "color",
  className = "",
  alt = "Borderless",
  ...props
}: BrandMarkProps) {
  const inheritClass = variant === "inherit" ? "opacity-90" : "";
  return (
    // eslint-disable-next-line @next/next/no-img-element -- static SVG from public/brand
    <img
      src={brandAssetPath(BRAND_LOGO_SVG)}
      alt={alt}
      width={Math.round((size * 501) / 596)}
      height={size}
      className={`inline-block shrink-0 object-contain ${inheritClass} ${className}`.trim()}
      data-testid="brand-mark"
      data-variant={variant}
      {...props}
    />
  );
}
