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
        'integration-orange': '#fb923c',
        'integration-orange-dark': '#f97316',
        'lambda-gold': '#ffb347',
        'trust-blue': '#3b82f6',
        'success-green': '#10b981',
        'warning-amber': '#f59e0b',
        'error-red': '#ef4444',
        'info-blue': '#3b82f6',
      },
      backgroundImage: {
        'marketplace-gradient': 'linear-gradient(135deg, #fb923c 0%, #f97316 100%)',
      },
    },
  },
  plugins: [],
}
