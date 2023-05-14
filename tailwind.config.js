/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: "class",
  content: ["src/templates/**/*.{html,js}", "src/static/js/**/*.js"],
  theme: {
    extend: {
      aria: {
        // non-default https://tailwindcss.com/docs/hover-focus-and-other-states#aria-states
        current: 'current="page"',
      },
      colors: {
        dawn: {
          darker: "#15803d", // green-700
          DEFAULT: "#16a34a", // green-600
          muted: "#22c55e", // green-500
          lighter: "#86efac", // green-300
        },
        dusk: {
          darker: "#7e22ce", // purple-700
          DEFAULT: "#9333ea", // purple-600
          muted: "#a855f7", // purple-500
          lighter: "#d8b4fe", // purple-300
        },
        grayed: {
          darker: "#334155", // slate-700
          DEFAULT: "#475569", // slate-600
          muted: "#94a3b8", // slate-400
          lighter: "#cbd5e1", // slate-300
        },
      },
    },
  },
  plugins: [
    require("@tailwindcss/typography"),
    require("@tailwindcss/forms"),
    require("@tailwindcss/aspect-ratio"),
    require("@tailwindcss/container-queries"),
  ],
};
