const { fontFamily } = require("tailwindcss/defaultTheme")

/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        // Dark theme (default)
        'dark': {
          'background': '#0B0B0F',
          'surface': '#111216',
          'surface-alt': 'rgba(18,18,24,0.6)',
          'text-primary': '#FFFFFF',
          'text-secondary': '#C9CDD6',
          'border': 'rgba(255,255,255,0.08)'
        },
        // Light theme
        'light': {
          'background': '#FFFFFF',
          'surface': '#F5F7FB',
          'surface-alt': 'rgba(255,255,255,0.55)',
          'text-primary': '#0A0A0A',
          'text-secondary': '#4B5563',
          'border': 'rgba(10,10,10,0.08)'
        },
        // Semantic colors
        'accent': '#4F8BFF',
        'success': '#22C55E',
        'warning': '#F59E0B',
        'danger': '#EF4444',
        'info': '#38BDF8'
      },
      fontFamily: {
        sans: ['Inter', ...fontFamily.sans],
      },
      fontSize: {
        'display': ['3rem', { lineHeight: '1.3' }],
        'h1': ['3rem', { lineHeight: '1.3' }],
        'h2': ['2.25rem', { lineHeight: '1.3' }],
        'h3': ['1.75rem', { lineHeight: '1.3' }],
        'h4': ['1.375rem', { lineHeight: '1.3' }],
        'body': ['1rem', { lineHeight: '1.55' }],
        'small': ['0.875rem', { lineHeight: '1.55' }],
      },
      spacing: {
        '4': '4px',
        '8': '8px',
        '12': '12px',
        '16': '16px',
        '20': '20px',
        '24': '24px',
        '32': '32px',
        '40': '40px',
      },
      borderRadius: {
        'xs': '6px',
        'sm': '10px',
        'md': '14px',
        'lg': '20px',
        'xl': '28px',
      },
      boxShadow: {
        'subtle': '0 1px 2px rgba(0,0,0,.25)',
        'floating': '0 8px 24px rgba(0,0,0,.25)',
      },
      backdropBlur: {
        'glass': '16px',
      },
      transitionDuration: {
        '90': '90ms',
        '180': '180ms',
        '250': '250ms',
        '350': '350ms',
        '450': '450ms',
      },
      animation: {
        'fade-in': 'fadeIn 150ms ease-out',
        'scale-up': 'scaleUp 90ms ease-out',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        scaleUp: {
          '0%': { transform: 'scale(0.95)' },
          '100%': { transform: 'scale(1)' },
        },
      },
      maxWidth: {
        'homepage': '1280px',
        'content': '720px',
      },
      gridTemplateColumns: {
        'homepage': 'repeat(12, 1fr)',
        'products-3': 'repeat(3, 1fr)',
        'products-2': 'repeat(2, 1fr)',
        'studio': '208px 1fr 232px',
        // When fully collapsed we render 0px columns (we also use arbitrary classes via grid-cols-[...])
        'studio-collapsed': '0px 1fr 0px',
      },
      gridTemplateAreas: {
        'studio': '"left context right" "left chat right"',
      },
      screens: {
        'xs': '480px',
      },
    },
  },
  plugins: [],
}