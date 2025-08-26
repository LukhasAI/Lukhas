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
        'trinity-identity': 'rgb(var(--trinity-identity) / <alpha-value>)',
        'trinity-consciousness': 'rgb(var(--trinity-consciousness) / <alpha-value>)',
        'trinity-guardian': 'rgb(var(--trinity-guardian) / <alpha-value>)',
        'accent-gold': 'rgb(var(--accent-gold) / <alpha-value>)',
        'accent-gold-light': 'rgb(251, 191, 36)',
        'text-primary': 'rgb(var(--text-primary) / <alpha-value>)',
        'text-secondary': 'rgb(var(--text-secondary) / <alpha-value>)',
        'text-tertiary': 'rgb(var(--text-tertiary) / <alpha-value>)',
        'bg-primary': 'rgb(var(--bg-primary) / <alpha-value>)',
        'bg-secondary': 'rgb(var(--bg-secondary) / <alpha-value>)',
        'bg-tertiary': 'rgb(var(--bg-tertiary) / <alpha-value>)',
        'glass': 'var(--glass)',
        'glass-border': 'var(--glass-border)',
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
