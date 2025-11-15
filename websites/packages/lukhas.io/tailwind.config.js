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
        'infrastructure-green': '#22c55e',
        'infrastructure-green-dark': '#16a34a',
        'code-cyan': '#06b6d4',
        'lambda-gold': '#ffb347',
        'success-green': '#10b981',
        'warning-amber': '#f59e0b',
        'error-red': '#ef4444',
        'info-blue': '#3b82f6',
      },
      backgroundImage: {
        'infrastructure-gradient': 'linear-gradient(135deg, #22c55e 0%, #16a34a 100%)',
      },
    },
  },
  plugins: [],
}
