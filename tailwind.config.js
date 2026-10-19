/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  darkMode: ["class", '[data-theme="dark"]'],
  theme: {
    extend: {
      fontFamily: {
        mono: [
          '"Cascadia Mono"',
          '"Cascadia Code"',
          "ui-monospace",
          "SFMono-Regular",
          "Consolas",
          '"Liberation Mono"',
          "monospace",
        ],
      },
      colors: {
        ground: "var(--bg-ground)",
        surface: "var(--bg-surface)",
        elevated: "var(--bg-elevated)",
        hover: "var(--bg-hover)",
        selected: "var(--bg-selected)",
        ink: {
          primary: "var(--text-primary)",
          secondary: "var(--text-secondary)",
          muted: "var(--text-muted)",
        },
        border: {
          subtle: "var(--border-subtle)",
          strong: "var(--border-strong)",
          focus: "var(--border-focus)",
        },
        accent: {
          DEFAULT: "var(--accent-primary)",
          soft: "var(--accent-soft)",
          ink: "var(--accent-ink)",
        },
        status: {
          correct: "var(--status-correct)",
          incorrect: "var(--status-incorrect)",
          warning: "var(--status-warning)",
        },
      },
    },
  },
  plugins: [],
};
