/*
 * ═══════════════════════════════════════════════════════════════════════════
 * FILENAME: tailwind.config.js
 * MODULE: frontend
 * DESCRIPTION: Tailwind CSS configuration for Oneiric Core frontend. Defines
 *              custom theme extensions, animations, colors, and design system
 *              for the symbolic dream analysis interface.
 * DEPENDENCIES: tailwindcss, postcss, frontend framework
 * LICENSE: PROPRIETARY - LUKHAS AI SYSTEMS - UNAUTHORIZED ACCESS PROHIBITED
 * ═══════════════════════════════════════════════════════════════════════════
 */

/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      keyframes: {
        fadeUp: {
          '0%': {
            opacity: '0',
            transform: 'translateY(12px)'
          },
          '100%': {
            opacity: '1',
            transform: 'translateY(0)'
          },
        },
        shimmer: {
          '0%': {
            backgroundPosition: '-200px 0'
          },
          '100%': {
            backgroundPosition: 'calc(200px + 100%) 0'
          },
        },
      },
      animation: {
        fadeUp: 'fadeUp 0.8s ease-out',
        shimmer: 'shimmer 1.3s ease-in-out infinite',
      },
      colors: {
        symbolic: {
          50: '#f0f9ff',
          100: '#e0f2fe',
          200: '#bae6fd',
          300: '#7dd3fc',
          400: '#38bdf8',
          500: '#0ea5e9',
          600: '#0284c7',
          700: '#0369a1',
          800: '#075985',
          900: '#0c4a6e',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'Consolas', 'monospace'],
      },
    },
  },
  plugins: [],
};

/*
 * ═══════════════════════════════════════════════════════════════════════════
 * FILENAME: tailwind.config.js
 * VERSION: 1.0.0
 * TIER SYSTEM: Frontend styling (Visual layer for all user tiers)
 * ΛTRACE INTEGRATION: ENABLED
 * CAPABILITIES: Custom theme definition, animation configuration, color palette
 *               management, responsive design utilities, component styling
 * FUNCTIONS: Configuration object export for Tailwind CSS compilation
 * CLASSES: None directly defined (exports configuration object)
 * DECORATORS: None
 * DEPENDENCIES: Tailwind CSS framework, PostCSS processing
 * INTERFACES: Tailwind CSS configuration interface, design system API
 * ERROR HANDLING: Configuration validation by Tailwind CSS
 * LOGGING: ΛTRACE_ENABLED for style compilation and usage tracking
 * AUTHENTICATION: Not applicable (Styling configuration)
 * HOW TO USE:
 *   Automatically used by Tailwind CSS during build process
 *   Classes available in all frontend components
 *   Custom animations: animate-fadeUp, animate-shimmer
 *   Custom colors: symbolic-50 through symbolic-900
 * INTEGRATION NOTES: Defines visual identity for Oneiric Core interface.
 *   Supports symbolic color scheme and dream-like animations.
 *   Integrates with Next.js build process for optimized CSS generation.
 * MAINTENANCE: Update color palette, animations, and breakpoints as design
 *   system evolves. Maintain consistency across all frontend components.
 * CONTACT: LUKHAS DEVELOPMENT TEAM
 * LICENSE: PROPRIETARY - LUKHAS AI SYSTEMS - UNAUTHORIZED ACCESS PROHIBITED
 * ═══════════════════════════════════════════════════════════════════════════
 */
