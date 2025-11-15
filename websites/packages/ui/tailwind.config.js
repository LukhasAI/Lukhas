/** @type {import('tailwindcss').Config} */
export default {
  content: ['./src/**/*.{js,jsx,ts,tsx}'],
  theme: {
    extend: {
      colors: {
        // LUKHAS Brand Colors (CSS variable references)
        'deep-space': 'var(--lukhas-deep-space)',
        'card-bg': 'var(--lukhas-card-bg)',
        'card-elevated': 'var(--lukhas-card-elevated)',
        'lambda-blue': 'var(--lukhas-lambda-blue)',
        'quantum-green': 'var(--lukhas-quantum-green)',
        'luke-gold': 'var(--lukhas-luke-gold)',
        'text-primary': 'var(--lukhas-text-primary)',
        'text-secondary': 'var(--lukhas-text-secondary)',
        'border': 'var(--lukhas-border)',
        'border-bright': 'var(--lukhas-border-bright)',
        'domain-id-purple': 'var(--domain-id-purple)',
        'domain-com-trust-blue': 'var(--domain-com-trust-blue)',
        'domain-us-institutional': 'var(--domain-us-institutional)',
        'glass': 'var(--glass-bg)',
        'glass-border': 'var(--glass-border)',
      },
      fontFamily: {
        display: 'var(--font-display)',
        mono: 'var(--font-mono)',
      },
      letterSpacing: {
        'thin-capitals': 'var(--tracking-thin-capitals)',
        'heading': 'var(--tracking-heading)',
        'logo': 'var(--tracking-logo)',
      },
      transitionTimingFunction: {
        'lukhas': 'var(--easing-lukhas)',
      },
      backdropBlur: {
        'glass': 'var(--glass-blur)',
      },
      borderRadius: {
        'glass': 'var(--border-radius-glass)',
        'pill': 'var(--border-radius-pill)',
      },
      boxShadow: {
        'glow-blue': 'var(--glow-blue)',
        'glow-green': 'var(--glow-green)',
        'glow-purple': 'var(--glow-purple)',
      },
      zIndex: {
        'fixed': 'var(--z-fixed)',
      },
      animation: {
        'breathe-subtle': 'breathe-subtle 12s ease-in-out infinite',
        'spin': 'spin 1s linear infinite',
      },
    },
  },
  plugins: [],
}
