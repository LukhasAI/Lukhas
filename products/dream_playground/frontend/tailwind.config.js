/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        lukhas: {
          purple: '#7C3AED',
          blue: '#3B82F6',
          cyan: '#06B6D4',
        }
      }
    },
  },
  plugins: [],
}
