/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        navy: "#1e293b",
        "accent-blue": "#2563eb",
        "risk-low": "#22c55e",
        "risk-med": "#f59e0b",
        "risk-high": "#ef4444",
        "risk-critical": "#7f1d1d",
      },
    },
  },
  plugins: [],
}
