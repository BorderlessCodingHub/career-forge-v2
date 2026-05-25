import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        bg: "var(--bg)",
        "bg-sidebar": "var(--bg-sidebar)",
        surface: "var(--surface)",
        "surface-elevated": "var(--surface-elevated)",
        accent: "var(--accent)",
        "accent-mint": "var(--accent-mint)",
        "text-primary": "var(--text)",
        "text-secondary": "var(--text-2)",
        "text-muted": "var(--text-3)",
        border: "var(--border)",
      },
      backgroundImage: {
        "brand-ribbon":
          "linear-gradient(135deg, var(--accent-mint) 0%, var(--accent) 100%)",
      },
    },
  },
  plugins: [],
};

export default config;
