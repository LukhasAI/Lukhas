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
        // lukhas.com brand colors
        'consciousness-deep': '#1A1A2E',
        'awareness-silver': '#E8E8F0',
        'lambda-gold': '#FFB347',
        'trust-blue': '#3B82F6',
        'trust-blue-dark': '#2563EB',
        'guardian-shield': '#E17055',

        // Supporting colors
        'consciousness-neural': '#00B894',
        'whisper-pearl': '#F8F9FA',

        // Semantic colors
        'verified-green': '#10B981',
        'warning-amber': '#F59E0B',
        'error-red': '#EF4444',
        'info-blue': '#3B82F6',
      },
      backgroundImage: {
        'trust-gradient': 'linear-gradient(135deg, #3B82F6 0%, #2563EB 100%)',
        'guardian-gradient': 'linear-gradient(135deg, #E17055 0%, #D35A47 100%)',
      },
    },
  },
  plugins: [],
}
