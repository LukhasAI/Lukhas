/** @type {import('tailwindcss').Config} */
export default {
  content: ['./src/**/*.{js,jsx,ts,tsx}'],
  theme: {
    extend: {
      colors: {
        lukhas: {
          'deep-space': '#0a0a0a',
          'card-bg': '#181c24',
          'card-elevated': '#232b39',
          'lambda-blue': '#00d4ff',
          'quantum-green': '#00ff88',
          'luke-gold': '#d4af37',
          'text-primary': '#f0f6fc',
          'text-secondary': '#7d8590',
          'border': '#2a2a3e',
        },
        domain: {
          'id-purple': '#9333EA',
          'com-trust-blue': '#3B82F6',
          'us-institutional': '#1E40AF',
        },
      },
      fontFamily: {
        display: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
      letterSpacing: {
        'thin-capitals': '-3px',
        'heading': '-1px',
        'body': '0.15em',
      },
      transitionTimingFunction: {
        'lukhas': 'cubic-bezier(.4, 0, .2, 1)',
      },
      backdropBlur: {
        'lukhas': '18px',
      },
      borderRadius: {
        'glass': '18px',
      },
    },
  },
  plugins: [],
}
