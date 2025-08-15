import type { Config } from 'tailwindcss'

const config: Config = {
  darkMode: ['class'],
  content: [
    './pages/**/*.{ts,tsx}',
    './components/**/*.{ts,tsx}',
    './app/**/*.{ts,tsx}',
    './src/**/*.{ts,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        'primary-dark': '#000000',
        'primary-light': '#FFFFFF',
        'trinity-identity': '#7C3AED',  // Purple 600
        'trinity-consciousness': '#2563EB',  // Blue 600
        'trinity-guardian': '#10B981',
        'accent-gold': '#F59E0B',
        'neutral-gray': '#9CA3AF',  // Gray 400
        'glass-white': 'rgba(255,255,255,0.05)',
      },
      fontFamily: {
        'ultralight': ['Helvetica Neue UltraLight', 'system-ui', 'sans-serif'],
        'thin': ['Helvetica Neue Thin', 'system-ui', 'sans-serif'],
        'regular': ['Helvetica Neue', 'system-ui', 'sans-serif'],
      },
      fontSize: {
        'hero': ['6rem', { lineHeight: '1', letterSpacing: '0.05em' }],
        'display': ['4rem', { lineHeight: '1.1', letterSpacing: '0.02em' }],
      },
      animation: {
        'pulse-slow': 'pulse 4s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'float': 'float 6s ease-in-out infinite',
        'glow': 'glow 2s ease-in-out infinite',
      },
      keyframes: {
        float: {
          '0%, 100%': { transform: 'translateY(0)' },
          '50%': { transform: 'translateY(-10px)' },
        },
        glow: {
          '0%, 100%': { opacity: '1' },
          '50%': { opacity: '0.6' },
        },
      },
      backdropBlur: {
        xs: '2px',
      },
    },
  },
  plugins: [],
}

export default config