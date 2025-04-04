import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{js,ts,jsx,tsx,mdx}", "./src/**/*.{js,ts,jsx,tsx,mdx}"],
  theme: {
    extend: {
      fontFamily: {
        sans: ["var(--font-ibm-plex-arabic)", "sans-serif"],
        ibmPlex: ["var(--font-ibm-plex-arabic)", "sans-serif"],
      },
    },
  },
  plugins: [],
};

export default config;
