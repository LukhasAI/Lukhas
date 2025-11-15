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
        'dream-ethereal': '#8b7cf6',
        'dream-ethereal-dark': '#6366f1',
        'lambda-gold': '#ffb347',
        'consciousness-neural': '#00b894',
        'guardian-shield': '#e17055',
      },
      backgroundImage: {
        'dream-gradient': 'linear-gradient(135deg, #8b7cf6 0%, #6366f1 100%)',
        'cosmic-gradient': 'linear-gradient(135deg, #000814 0%, #7209b7 100%)',
      },
    },
  },
  plugins: [],
}
