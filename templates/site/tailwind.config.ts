import type { Config } from "tailwindcss";
import theme from "./theme.json";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}", "./lib/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        bg: theme.bg,
        surface: theme.surface,
        accent: theme.accent,
        "accent-deep": theme.accent_deep,
        highlight: theme.highlight,
        ink: theme.text,
      },
      fontFamily: {
        display: ["var(--font-display)", "serif"],
        body: ["var(--font-body)", "system-ui", "sans-serif"],
      },
    },
  },
  plugins: [],
};
export default config;
