/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './app/**/*.{js,ts,jsx,tsx,mdx}',
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        'trinity-identity': 'rgb(107, 70, 193)',
        'trinity-consciousness': 'rgb(14, 165, 233)', 
        'trinity-guardian': 'rgb(16, 185, 129)',
        'accent-gold': 'rgb(245, 158, 11)',
        'accent-gold-light': 'rgb(251, 191, 36)',
        'text-primary': 'rgb(255, 255, 255)',
        'text-secondary': 'rgba(255, 255, 255, 0.7)',
        'text-tertiary': 'rgba(255, 255, 255, 0.5)',
        'bg-primary': 'rgb(0, 0, 0)',
        'bg-secondary': 'rgb(17, 17, 17)',
        'bg-tertiary': 'rgb(38, 38, 38)',
        'glass': 'rgba(255, 255, 255, 0.05)',
        'glass-border': 'rgba(255, 255, 255, 0.1)',
      },
      fontSize: {
        'display': ['3.5rem', { lineHeight: '1.1', letterSpacing: '-0.02em' }],
      },
      fontFamily: {
        'light': ['Helvetica Neue Light', 'system-ui', 'sans-serif'],
        'regular': ['Helvetica Neue', 'system-ui', 'sans-serif'],
        'medium': ['Helvetica Neue Medium', 'system-ui', 'sans-serif'],
      },
    },
  },
  plugins: [],
}