# @lukhas/ui

**LUKHAS Design System** - Shared components, styles, and utilities for the LUKHAS website ecosystem.

## 📦 Installation

This is an internal package within the LUKHAS websites monorepo. It's automatically available to all sites via pnpm workspaces.

```bash
# In any site package (lukhas.id, lukhas.com, lukhas.us)
pnpm add @lukhas/ui
```

## 🎨 Design Tokens

### Colors

```tsx
import { colors } from '@lukhas/ui'

// Primary colors
colors.lukhas.deepSpace      // #0a0a0a - Primary background
colors.lukhas.lambdaBlue     // #00d4ff - Primary CTA, links
colors.lukhas.quantumGreen   // #00ff88 - Success, active states
colors.lukhas.lukeGold       // #d4af37 - Special accents

// Domain-specific
colors.domain.idPurple       // #9333EA - lukhas.id security
colors.domain.comTrustBlue   // #3B82F6 - lukhas.com corporate
colors.domain.usInstitutional // #1E40AF - lukhas.us compliance
```

### Typography

```tsx
// Font families
font-display  // Inter (thin capitals, 100-300 weight)
font-mono     // JetBrains Mono (code, technical)

// Letter spacing
tracking-thin-capitals  // -3px (hero text)
tracking-heading        // -1px (h1-h3)
tracking-body           // 0.15em (body text)
```

### Animation Timing

```tsx
// Transition durations
transition-fast     // 0.15s (micro-interactions)
transition-normal   // 0.3s (most transitions)
transition-slow     // 0.5s (page transitions)

// Easing function
ease-lukhas  // cubic-bezier(.4, 0, .2, 1)
```

---

## 🧩 Components

### GlassCard

Glassmorphism card with backdrop blur and subtle borders.

```tsx
import { GlassCard } from '@lukhas/ui'

<GlassCard className="p-6">
  <h2>Identity Management</h2>
  <p>Secure, private, accessible</p>
</GlassCard>
```

### Button

Primary and secondary button styles with hover effects.

```tsx
import { Button } from '@lukhas/ui'

<Button variant="primary" size="lg">
  Get Started
</Button>

<Button variant="secondary" size="md">
  Learn More
</Button>
```

### Header

Fixed header with glassmorphism and responsive navigation.

```tsx
import { Header } from '@lukhas/ui'

<Header
  logo="LUKHΛS"
  logoSuffix=".id"
  links={[
    { label: 'Home', href: '/' },
    { label: 'Dashboard', href: '/dashboard' },
    { label: 'Docs', href: '/docs' },
  ]}
/>
```

### Footer

Unified footer with ecosystem links and social icons.

```tsx
import { Footer } from '@lukhas/ui'

<Footer
  links={[
    { label: 'Privacy', href: '/privacy' },
    { label: 'Terms', href: '/terms' },
    { label: 'Security', href: '/security' },
  ]}
  social={{
    github: 'https://github.com/LukhasAI',
    twitter: 'https://twitter.com/LukhasAI',
  }}
/>
```

---

## 🎬 Utilities

### Morphing System

WebGL-based morphing orb system (ported from PR0T3US).

```tsx
import { MorphingOrb } from '@lukhas/ui/utils'

<MorphingOrb
  shapes={['sphere', 'cat', 'car', 'person']}
  morphSpeed={0.02}
  particleCount={1000}
  enableVoiceModulation={false}
/>
```

### cn (Class Names)

Utility for merging Tailwind classes with clsx.

```tsx
import { cn } from '@lukhas/ui'

<div className={cn(
  'glass-card',
  isActive && 'border-lambda-blue',
  'hover:scale-105'
)}>
  Content
</div>
```

---

## 🎨 Styles

### Global CSS Variables

Import in your app entry point:

```tsx
import '@lukhas/ui/styles'
```

Available variables:

```css
/* Colors */
--lukhas-deep-space: #0a0a0a;
--lukhas-card-bg: #181c24;
--lukhas-lambda-blue: #00d4ff;
--lukhas-quantum-green: #00ff88;
--lukhas-luke-gold: #d4af37;

/* Spacing */
--spacing-xs: 4px;
--spacing-sm: 8px;
--spacing-md: 16px;
--spacing-lg: 24px;
--spacing-xl: 32px;
--spacing-xxl: 48px;

/* Animation */
--timing-fast: 0.15s;
--timing-normal: 0.3s;
--timing-slow: 0.5s;
--timing-breathe: 12s;
--easing: cubic-bezier(.4, 0, .2, 1);

/* Border Radius */
--border-radius-sm: 4px;
--border-radius-md: 8px;
--border-radius-lg: 12px;
--border-radius-xl: 16px;
--border-radius-glass: 18px;
```

---

## 🛠️ Development

```bash
# Run Storybook (coming soon)
pnpm dev

# Build library
pnpm build

# Lint
pnpm lint
```

---

## 📁 Structure

```
ui/
├── src/
│   ├── components/       # React components
│   │   ├── GlassCard.tsx
│   │   ├── Button.tsx
│   │   ├── Header.tsx
│   │   └── Footer.tsx
│   ├── styles/           # CSS and design tokens
│   │   ├── variables.css # CSS custom properties
│   │   ├── animations.css # Reusable keyframes
│   │   └── index.css     # Main export
│   ├── utils/            # Utilities and helpers
│   │   ├── morphing-system/ # WebGL morphing (PR0T3US port)
│   │   ├── cn.ts         # Class name utility
│   │   └── index.ts
│   └── index.ts          # Main export
├── package.json
├── vite.config.ts
├── tailwind.config.js
└── README.md
```

---

## 📖 Usage Examples

### lukhas.id (Identity Management)

```tsx
import { Header, GlassCard, Button } from '@lukhas/ui'
import '@lukhas/ui/styles'

function LoginPage() {
  return (
    <>
      <Header logo="LUKHΛS" logoSuffix=".id" />
      <main className="min-h-screen bg-lukhas-deep-space p-6">
        <GlassCard className="max-w-md mx-auto p-8">
          <h1 className="text-3xl font-display font-thin tracking-heading">
            Welcome Back
          </h1>
          <form className="mt-6 space-y-4">
            {/* Form fields */}
          </form>
          <Button variant="primary" className="w-full mt-6">
            Sign In
          </Button>
        </GlassCard>
      </main>
    </>
  )
}
```

### lukhas.com (Corporate Placeholder)

```tsx
import { MorphingOrb, Button } from '@lukhas/ui'
import '@lukhas/ui/styles'

function HomePage() {
  return (
    <div className="relative min-h-screen bg-lukhas-deep-space">
      <MorphingOrb
        shapes={['sphere', 'guardian', 'constellation']}
        className="absolute inset-0 z-0"
      />
      <div className="relative z-10 flex flex-col items-center justify-center min-h-screen">
        <h1 className="text-6xl font-display font-thin tracking-thin-capitals">
          LUKHΛS
        </h1>
        <p className="mt-4 text-lukhas-text-secondary">
          The Guardian of Ethical AI Consciousness
        </p>
        <Button variant="primary" className="mt-8">
          Join Waiting List
        </Button>
      </div>
    </div>
  )
}
```

---

## 🔧 Customization

### Extending Tailwind Config

Sites can extend the base Tailwind config:

```js
// lukhas.id/tailwind.config.js
import baseConfig from '@lukhas/ui/tailwind.config'

export default {
  ...baseConfig,
  content: [
    './src/**/*.{js,jsx,ts,tsx}',
    '../ui/src/**/*.{js,jsx,ts,tsx}', // Include UI components
  ],
  theme: {
    extend: {
      ...baseConfig.theme.extend,
      colors: {
        ...baseConfig.theme.extend.colors,
        // Add site-specific colors
        custom: '#ff00ff',
      },
    },
  },
}
```

---

## 📝 License

Copyright © 2025 LUKHAS AI. All rights reserved.

---

**Built with** [Vite](https://vitejs.dev/) + [React](https://react.dev/) + [Tailwind CSS](https://tailwindcss.com/)
