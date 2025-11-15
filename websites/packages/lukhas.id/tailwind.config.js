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
        // lukhas.id brand colors
        'consciousness-deep': '#1A1A2E',
        'awareness-silver': '#E8E8F0',
        'lambda-gold': '#FFB347',
        'security-purple': '#9333EA',
        'security-trust': '#7C3AED',

        // Supporting colors
        'guardian-shield': '#E17055',
        'consciousness-neural': '#00B894',
        'whisper-pearl': '#F8F9FA',

        // Semantic colors
        'verified-green': '#10B981',
        'warning-amber': '#F59E0B',
        'error-red': '#EF4444',
        'info-blue': '#3B82F6',
      },
      backgroundImage: {
        'security-gradient': 'linear-gradient(135deg, #9333EA 0%, #7C3AED 100%)',
      },
    },
  },
  plugins: [],
}
