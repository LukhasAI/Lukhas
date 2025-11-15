/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
    "../ui/src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'consciousness-deep': '#1a1a2e',
        'awareness-silver': '#e8e8f0',
        'institutional-blue': '#1e40af',
        'institutional-blue-dark': '#1e3a8a',
        'guardian-shield': '#e17055',
        'verified-green': '#10b981',
        'warning-amber': '#f59e0b',
      },
      backgroundImage: {
        'institutional-gradient': 'linear-gradient(135deg, #1e40af 0%, #1e3a8a 100%)',
      },
    },
  },
  plugins: [],
}
