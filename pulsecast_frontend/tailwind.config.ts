import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "var(--pc-background)",
        surface: "var(--pc-surface)",
        panel: "var(--pc-panel)",
        border: "var(--pc-border)",
        heading: "var(--pc-heading)",
        contrast: "var(--pc-contrast)",
        muted: "var(--pc-muted)",
        primary: "var(--pc-primary)",
        "primary-strong": "var(--pc-primary-strong)",
        accent: "var(--pc-accent)",
      },
      fontFamily: {
        sans: [
          "var(--font-geist-sans)",
          "Inter",
          "-apple-system",
          "BlinkMacSystemFont",
          "Segoe UI",
          "sans-serif",
        ],
        mono: ["var(--font-geist-mono)", "SFMono-Regular", "Menlo", "monospace"],
      },
      boxShadow: {
        card: "0 18px 55px rgba(0, 0, 0, 0.28)",
        inset: "inset 0 1px 0 rgba(255, 255, 255, 0.03)",
      },
    },
  },
  plugins: [],
};
export default config;
