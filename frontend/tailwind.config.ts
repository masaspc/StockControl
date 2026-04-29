import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
    "./lib/**/*.{ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          DEFAULT: "#0b3d91",
          light: "#1e63d9",
          dark: "#072b66",
        },
      },
    },
  },
  plugins: [],
};

export default config;
