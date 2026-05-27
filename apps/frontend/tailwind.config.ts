import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ["var(--font-sans)", "Inter", "system-ui", "sans-serif"],
        mono: ["var(--font-mono)", "JetBrains Mono", "monospace"],
      },
      colors: {
        bg: "var(--bg)",
        "bg-sidebar": "var(--bg-sidebar)",
        surface: "var(--surface)",
        "surface-elevated": "var(--surface-elevated)",
        "surface-node": "var(--surface-node)",
        accent: "var(--accent)",
        "accent-mint": "var(--accent-mint)",
        "accent-mint-bright": "var(--accent-mint-bright)",
        success: "var(--success)",
        warning: "var(--warning)",
        locked: "var(--locked)",
        evidence: "var(--evidence)",
        "text-primary": "var(--text)",
        "text-secondary": "var(--text-2)",
        "text-muted": "var(--text-3)",
        border: "var(--border)",
        "border-soft": "var(--border-soft)",
      },
      borderColor: {
        DEFAULT: "var(--border)",
      },
      borderRadius: {
        card: "12px",
        node: "16px",
        modal: "12px",
      },
      spacing: {
        grid: "4px",
      },
      backgroundImage: {
        "brand-ribbon":
          "linear-gradient(135deg, var(--accent-mint) 0%, var(--accent) 100%)",
        "dot-grid":
          "radial-gradient(rgba(255,255,255,0.04) 1px, transparent 1px)",
      },
      backgroundSize: {
        dots: "24px 24px",
      },
    },
  },
  plugins: [],
};

export default config;
