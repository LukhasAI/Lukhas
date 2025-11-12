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
        'enterprise-pink': '#ec4899',
        'enterprise-pink-dark': '#db2777',
        'trust-blue': '#3b82f6',
        'lambda-gold': '#ffb347',
        'success-green': '#10b981',
        'warning-amber': '#f59e0b',
        'error-red': '#ef4444',
        'info-blue': '#3b82f6',
      },
      backgroundImage: {
        'enterprise-gradient': 'linear-gradient(135deg, #ec4899 0%, #db2777 100%)',
      },
    },
  },
  plugins: [],
}
