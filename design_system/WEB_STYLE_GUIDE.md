# 🎨 LUKHAS AI Web Style Guide
*Comprehensive Design System for Consciousness Technology Interfaces*

⚛️🧠🛡️ **Constellation Framework Design** | **Premium Aesthetic** | **Accessibility First**

---

## 📚 Table of Contents
- [Core Design Philosophy](#-core-design-philosophy)
- [Color System](#-color-system)
- [Typography](#-typography)
- [Spacing & Layout](#-spacing--layout)
- [Components](#-components)
- [Animation & Motion](#-animation--motion)
- [Accessibility](#-accessibility)
- [Performance Guidelines](#-performance-guidelines)
- [Code Standards](#-code-standards)

---

## 🎯 Core Design Philosophy

### **Design Principles**
1. **Consciousness-Driven**: Every element reflects AI consciousness and awareness
2. **Trinity Harmony**: Visual balance between Identity, Consciousness, and Guardian
3. **Premium Minimalism**: Clean, sophisticated interfaces inspired by Apple/OpenAI
4. **Accessibility First**: WCAG 2.1 AA compliance minimum
5. **Performance Optimized**: Sub-3 second load times, 60fps animations

### **Visual Language**
- **Glass Morphism**: Translucent surfaces with backdrop blur
- **Depth Layers**: Z-axis utilization for hierarchy
- **Particle Systems**: Dynamic, AI-controlled visual elements
- **Gradient Flows**: Smooth color transitions representing consciousness
- **Magnetic Interactions**: Elements that respond to user proximity

---

## 🔤 Brand Naming & Stylization (Λ rules)

### Official Names
- **Primary brand (display)**: `LUKHΛS` (U+039B Greek capital lambda).
  - **Use for**: wordmark, page headers, hero sections, promotional graphics.
  - **Do not use** in long paragraphs, legal text, or SEO-critical copy.
- **Plain-text brand**: **Lukhas**.
  - **Use for**: paragraphs, alt text, meta tags, filenames, code.
- **Product/Company pairing**: **Lukhas AI** (plain text) | **LUKHΛS ΛI** (display only).
- **Identity system**: **ΛiD** (Login/Identity), read aloud and written in plain text as **Lukhas ID**.

### Usage Rules
1. **Display vs. Plain Text**
   - Logos, wordmarks, big headings: prefer stylized `LUKHΛS` and `ΛI`.
   - Body copy, accessibility, SEO: use **Lukhas** and **AI**.
2. **Accessibility & Screen Readers**
   - When stylizing with Λ, add `aria-label="Lukhas"` or `aria-label="Lukhas AI"`.
   - For the identity button, label text may show `Log in with ΛiD`, but set `aria-label="Log in with Lukhas ID"`.
3. **Encoding & Fallback**
   - Always use the **Greek Lambda** (U+039B) character, not a Latin "A".
   - Prefer an **SVG wordmark** to guarantee uniform weight of Λ across platforms. Provide a plain-text fallback.

### Product Naming: MΛTRIZ
- **Display form**: `MΛTRIZ` (Greek Lambda Λ replaces first A)
- **Plain form**: **Matriz** (use in paragraphs, SEO, alt text)
- **Slug/URL**: `/matriz` (never include Λ in URLs)
- **Former name**: MATADA (deprecated - update all references)
- **Usage context**: Multimodal Adaptive Temporal Architecture for Dynamic Awareness

### Examples
```html
<!-- Header wordmark (display) -->
<a class="brand-wordmark" href="/" aria-label="Lukhas">LUKHΛS</a>

<!-- Product pairing (display) -->
<h1 class="brand-pair" aria-label="Lukhas AI">LUKHΛS <span class="ai">ΛI</span></h1>

<!-- Auth button (display with a11y) -->
<button class="btn-primary" aria-label="Log in with Lukhas ID">Log in with ΛiD</button>

<!-- MATRIZ product reference (display with a11y) -->
<h2 class="product-name" aria-label="Matriz">MΛTRIZ</h2>
```

---

## 🗣️ Voice & Tone — The Three‑Layer Pattern

Lukhas content may be rendered in **three parallel modes** to speak to different audiences.

1) **Poetic/Metaphor (Intro layer)** – short, professional poetic line to set context.
2) **Technical/Academic** – precise, formal, domain-specific explanation.
3) **Plain‑Language ("Mom Test")** – friendly, minimal jargon, short sentences.

### Authoring Rules
- Each page/section **may include all three** layers, or a **Tone Switch** can toggle them.
- Keep the **Poetic** blurb ≤ 40 words. Avoid claims; evoke purpose.
- **Technical** layer uses correct terminology and citations.
- **Plain‑Language** explains outcomes, not implementation details.

### Tone Switch (UI pattern)
```tsx
// components/ToneSwitch.tsx
export function ToneSwitch({ value, onChange }: { value: 'poetic'|'technical'|'plain'; onChange: (v:any)=>void }) {
  return (
    <div role="tablist" aria-label="Content tone">
      {(['poetic','technical','plain'] as const).map(k => (
        <button role="tab" aria-selected={value===k} onClick={()=>onChange(k)} key={k} className={`tab ${value===k?'active':''}`}>{k}</button>
      ))}
    </div>
  )
}
```

```css
/* Tone utilities */
.tone-poetic{ font-style: italic; letter-spacing: var(--tracking-wide); opacity:.9 }
.tone-technical{ font-family: var(--font-mono); }
.tone-plain{ font-weight: var(--weight-regular); }
```

---

## 🎨 Color System

### **Primary Colors - Constellation Framework**

```css
/* Trinity Core Colors */
--trinity-identity: rgb(107, 70, 193);      /* #6B46C1 - Deep Purple */
--trinity-consciousness: rgb(14, 165, 233);  /* #0EA5E9 - Sky Blue */
--trinity-guardian: rgb(16, 185, 129);       /* #10B981 - Emerald */

/* Accent Colors */
--accent-gold: rgb(245, 158, 11);           /* #F59E0B - Premium Gold */
--accent-gold-light: rgb(251, 191, 36);     /* #FBBF24 - Light Gold */
```

### **Semantic Colors**

```css
/* Text Colors */
--text-primary: rgb(255, 255, 255);         /* Pure White */
--text-secondary: rgb(163, 163, 163);       /* Gray 400 */
--text-tertiary: rgb(115, 115, 115);        /* Gray 500 */

/* Background Colors */
--bg-primary: rgb(0, 0, 0);                 /* Pure Black */
--bg-secondary: rgb(18, 18, 18);            /* Gray 900 */
--bg-tertiary: rgb(38, 38, 38);             /* Gray 800 */

/* Glass Effects */
--glass: rgba(255, 255, 255, 0.05);
--glass-border: rgba(255, 255, 255, 0.1);
```

### **Gradient Combinations**

```css
/* Trinity Gradient */
.gradient-trinity {
  background: linear-gradient(135deg,
    var(--trinity-identity) 0%,
    var(--trinity-consciousness) 50%,
    var(--trinity-guardian) 100%
  );
}

/* Consciousness Flow */
.gradient-consciousness {
  background: linear-gradient(90deg,
    rgba(107, 70, 193, 0.8),
    rgba(14, 165, 233, 0.6),
    rgba(16, 185, 129, 0.8)
  );
}
```

---

## 📝 Typography

### **Font Stack**


```css
/* Primary Font Family - Helvetica Neue */
--font-ultralight: 'Helvetica Neue UltraLight', -apple-system, system-ui, sans-serif;
--font-light: 'Helvetica Neue Light', -apple-system, system-ui, sans-serif;
--font-regular: 'Helvetica Neue', -apple-system, system-ui, sans-serif;
--font-medium: 'Helvetica Neue Medium', -apple-system, system-ui, sans-serif;

/* Monospace for Code */
--font-mono: 'SF Mono', 'Monaco', 'Inconsolata', 'Fira Code', monospace;
```

### **Wordmark & Font Strategy**

- **Wordmark**: `LUKHΛS` set in **Helvetica Neue UltraLight** (100), **ALL CAPS**.
- **Delivery**: Prefer an **SVG wordmark** asset to lock the Λ weight and kerning.
  Fallback to text with the stack below.
- **UI Body/Headings**: Inter (variable) is recommended for app UI; Helvetica Neue remains acceptable if licensed.

```css
/* Logo (display) */
.brand-wordmark { font-family: 'Helvetica Neue', Inter, system-ui, sans-serif; font-weight: 100; letter-spacing: 0.12em; text-transform: uppercase; }

/* UI (general) */
:root { --ui-font: Inter, 'Helvetica Neue', -apple-system, system-ui, sans-serif; }
body { font-family: var(--ui-font); }
```

**Why**: Some fonts render Greek Λ at a different weight if they fall back. Using SVG prevents mismatched weight; Inter ensures broad Greek coverage when text is used.

### **Type Scale**

```css
/* Display */
--text-display: 3.5rem;      /* 56px - Hero headlines */
--text-h1: 2.5rem;           /* 40px - Page titles */
--text-h2: 2rem;             /* 32px - Section headers */
--text-h3: 1.5rem;           /* 24px - Subsections */
--text-h4: 1.25rem;          /* 20px - Card titles */
--text-body: 1rem;           /* 16px - Body text */
--text-small: 0.875rem;      /* 14px - Captions */
--text-tiny: 0.75rem;        /* 12px - Labels */

/* Line Heights */
--leading-tight: 1.1;
--leading-normal: 1.5;
--leading-relaxed: 1.75;

/* Letter Spacing */
--tracking-tight: -0.02em;
--tracking-normal: 0;
--tracking-wide: 0.025em;
```

### **Font Weights**

```css
--weight-ultralight: 100;
--weight-light: 300;
--weight-regular: 400;
--weight-medium: 500;
```

---

## 📐 Spacing & Layout

### **Spacing Scale**

```css
/* Base unit: 4px */
--space-0: 0;
--space-1: 0.25rem;   /* 4px */
--space-2: 0.5rem;    /* 8px */
--space-3: 0.75rem;   /* 12px */
--space-4: 1rem;      /* 16px */
--space-5: 1.25rem;   /* 20px */
--space-6: 1.5rem;    /* 24px */
--space-8: 2rem;      /* 32px */
--space-10: 2.5rem;   /* 40px */
--space-12: 3rem;     /* 48px */
--space-16: 4rem;     /* 64px */
--space-20: 5rem;     /* 80px */
--space-24: 6rem;     /* 96px */
--space-32: 8rem;     /* 128px */
```

### **Grid System**

```css
/* Container Widths */
--container-xs: 20rem;    /* 320px */
--container-sm: 24rem;    /* 384px */
--container-md: 28rem;    /* 448px */
--container-lg: 32rem;    /* 512px */
--container-xl: 36rem;    /* 576px */
--container-2xl: 42rem;   /* 672px */
--container-3xl: 48rem;   /* 768px */
--container-4xl: 56rem;   /* 896px */
--container-5xl: 64rem;   /* 1024px */
--container-6xl: 72rem;   /* 1152px */
--container-7xl: 80rem;   /* 1280px */

/* Grid Columns */
--grid-cols-1: repeat(1, minmax(0, 1fr));
--grid-cols-2: repeat(2, minmax(0, 1fr));
--grid-cols-3: repeat(3, minmax(0, 1fr));
--grid-cols-4: repeat(4, minmax(0, 1fr));
--grid-cols-6: repeat(6, minmax(0, 1fr));
--grid-cols-12: repeat(12, minmax(0, 1fr));
```

### **Breakpoints**

```css
/* Mobile First Breakpoints */
--screen-sm: 640px;
--screen-md: 768px;
--screen-lg: 1024px;
--screen-xl: 1280px;
--screen-2xl: 1536px;
```

---

## 🧩 Components

### **Button Styles**

```css
/* Primary Button */
.btn-primary {
  background: var(--trinity-identity);
  color: white;
  padding: var(--space-3) var(--space-6);
  border-radius: 8px;
  font-weight: var(--weight-medium);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 40px rgba(107, 70, 193, 0.4);
}

/* Glass Button */
.btn-glass {
  background: var(--glass);
  backdrop-filter: blur(24px);
  border: 1px solid var(--glass-border);
  color: white;
  transition: all 0.3s ease;
}

/* Magnetic Button */
.btn-magnetic {
  position: relative;
  transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}
```

### **Authentication Buttons**

```css
/* Login with ΛiD (display) */
.btn-login-lambda { composes: btn-primary; }
.btn-login-lambda::after { content: ' '; }
```

**Labels**
- **Display text**: `Log in with ΛiD`
- **ARIA label**: `Log in with Lukhas ID`
- **Grammar**: Use **"Log in"** (verb) for actions; use **"Login"** (noun) for screens/sections.
```

### **Card Components**

```css
/* Glass Card */
.card-glass {
  background: var(--glass);
  backdrop-filter: blur(24px);
  border: 1px solid var(--glass-border);
  border-radius: 16px;
  padding: var(--space-6);
}

/* Elevated Card */
.card-elevated {
  background: var(--bg-secondary);
  border-radius: 16px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
  transition: transform 0.3s ease;
}

.card-elevated:hover {
  transform: translateY(-4px) scale(1.02);
}
```

### **Input Fields**

```css
/* Glass Input */
.input-glass {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  padding: var(--space-3) var(--space-4);
  color: white;
  font-size: var(--text-body);
  transition: all 0.3s ease;
}

.input-glass:focus {
  outline: none;
  border-color: var(--trinity-consciousness);
  box-shadow: 0 0 0 3px rgba(14, 165, 233, 0.1);
}
```

---

## 🎬 Animation & Motion

### **Timing Functions**

```css
/* Easing Curves */
--ease-in-out: cubic-bezier(0.4, 0, 0.2, 1);
--ease-out: cubic-bezier(0, 0, 0.2, 1);
--ease-in: cubic-bezier(0.4, 0, 1, 1);
--ease-bounce: cubic-bezier(0.68, -0.55, 0.265, 1.55);

/* Duration */
--duration-instant: 100ms;
--duration-fast: 200ms;
--duration-normal: 300ms;
--duration-slow: 500ms;
--duration-slower: 700ms;
```

### **Animation Presets**

```css
/* Fade In */
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

/* Pulse */
@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

/* Gradient Flow */
@keyframes gradientFlow {
  0% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
}

/* Particle Float */
@keyframes particleFloat {
  0%, 100% { transform: translateY(0) rotate(0deg); }
  33% { transform: translateY(-30px) rotate(120deg); }
  66% { transform: translateY(30px) rotate(240deg); }
}
```

### **Interaction States**

```css
/* Hover Transitions */
.hover-lift {
  transition: transform var(--duration-normal) var(--ease-out);
}

.hover-lift:hover {
  transform: translateY(-4px);
}

/* Focus Rings */
.focus-ring:focus-visible {
  outline: none;
  ring: 2px solid var(--trinity-identity);
  ring-offset: 2px;
}
```

---

## ♿ Accessibility

### **WCAG 2.1 AA Requirements**

1. **Color Contrast**
   - Normal text: 4.5:1 minimum
   - Large text: 3:1 minimum
   - UI components: 3:1 minimum

2. **Focus Indicators**
   - Visible focus rings on all interactive elements
   - High contrast focus states
   - Keyboard navigation support

3. **Screen Reader Support**
   - Semantic HTML structure
   - ARIA labels where needed
   - Alt text for all images
   - Skip navigation links
   - **Stylized glyphs**: When using Λ in text, provide a plain-text label for AT.

   ```html
   <!-- Stylized, but accessible -->
   <h1 aria-label="Lukhas AI">LUKHΛS <span aria-hidden="true">ΛI</span></h1>
   ```

4. **Motion Preferences**
   ```css
   @media (prefers-reduced-motion: reduce) {
     * {
       animation-duration: 0.01ms !important;
       transition-duration: 0.01ms !important;
     }
   }
   ```

### **Keyboard Navigation**

```css
/* Tab Order */
[tabindex]:focus {
  outline: 2px solid var(--trinity-consciousness);
  outline-offset: 2px;
}

/* Skip Links */
.skip-link {
  position: absolute;
  top: -40px;
  left: 0;
  background: var(--trinity-identity);
  color: white;
  padding: var(--space-2) var(--space-4);
  z-index: 100;
}

.skip-link:focus {
  top: 0;
}
```

---

## ⚡ Performance Guidelines

### **Core Web Vitals Targets**

- **LCP (Largest Contentful Paint)**: < 2.5s
- **FID (First Input Delay)**: < 100ms
- **CLS (Cumulative Layout Shift)**: < 0.1
- **TTI (Time to Interactive)**: < 3.8s

### **Optimization Strategies**

1. **Image Optimization**
   ```jsx
   // Use Next.js Image component
   import Image from 'next/image'

   <Image
     src="/hero.webp"
     alt="LUKHAS AI Consciousness"
     width={1920}
     height={1080}
     priority
     placeholder="blur"
   />
   ```

2. **Font Loading**
   ```css
   @font-face {
     font-family: 'Helvetica Neue';
     src: url('/fonts/HelveticaNeue.woff2') format('woff2');
     font-display: swap; /* Critical for performance */
   }
   ```

3. **Code Splitting**
   ```jsx
   // Dynamic imports for heavy components
   const ParticleSystem = dynamic(() => import('./ParticleSystem'), {
     loading: () => <div className="skeleton" />,
     ssr: false
   })
   ```

4. **CSS Optimization**
   - Use CSS-in-JS sparingly
   - Purge unused Tailwind classes
   - Minimize critical CSS
   - Use CSS containment

---

## 💻 Code Standards

### **Component Structure**

```tsx
// components/Button/Button.tsx
import { forwardRef } from 'react'
import { cn } from '@/lib/utils'
import styles from './Button.module.css'

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'glass'
  size?: 'sm' | 'md' | 'lg'
  trinity?: 'identity' | 'consciousness' | 'guardian'
}

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = 'primary', size = 'md', trinity, children, ...props }, ref) => {
    return (
      <button
        ref={ref}
        className={cn(
          styles.button,
          styles[variant],
          styles[size],
          trinity && styles[`trinity-${trinity}`],
          className
        )}
        {...props}
      >
        {children}
      </button>
    )
  }
)

Button.displayName = 'Button'
```

### **Styling Approach**

1. **Tailwind for Utilities**
   ```jsx
   <div className="flex items-center justify-between p-4">
   ```

2. **CSS Modules for Components**
   ```css
   /* Button.module.css */
   .button {
     @apply px-6 py-3 rounded-lg font-medium transition-all;
   }
   ```

3. **CSS-in-JS for Dynamic Styles**
   ```jsx
   const dynamicStyle = {
     transform: `translateX(${mouseX}px)`,
     opacity: isVisible ? 1 : 0
   }
   ```

### **Naming Conventions**

- **Components**: PascalCase (`ParticleSystem.tsx`)
- **Utilities**: camelCase (`formatDate.ts`)
- **Constants**: UPPER_SNAKE_CASE (`MAX_PARTICLES`)
- **CSS Classes**: kebab-case (`btn-primary`)
- **CSS Modules**: camelCase (`styles.buttonPrimary`)

### **File Organization**

```
lukhas_website/
├── components/
│   ├── ui/           # Reusable UI components
│   ├── sections/     # Page sections
│   ├── layouts/      # Layout components
│   └── particles/    # Three.js components
├── styles/
│   ├── globals.css   # Global styles
│   ├── themes/       # Theme variations
│   └── modules/      # CSS modules
├── lib/
│   ├── utils/        # Utility functions
│   ├── hooks/        # Custom React hooks
│   └── animations/   # GSAP/Framer configs
└── public/
    ├── fonts/        # Web fonts
    ├── images/       # Static images
    └── textures/     # 3D textures
```

---

## 🚀 Libraries & Tools

### **Core Dependencies**

```json
{
  "dependencies": {
    // UI Framework
    "@radix-ui/react-*": "^1.0.0",     // Accessible components
    "tailwindcss": "^3.4.0",            // Utility CSS
    "clsx": "^2.1.0",                   // Class utilities
    "tailwind-merge": "^2.2.0",         // Merge Tailwind classes

    // Animation
    "framer-motion": "^11.0.0",         // React animations
    "gsap": "^3.12.4",                  // Advanced animations
    "lottie-react": "^2.4.0",           // Lottie animations

    // 3D Graphics
    "@react-three/fiber": "^8.15.0",    // React Three.js
    "@react-three/drei": "^9.92.0",     // Three.js helpers
    "three": "^0.160.0",                // 3D library

    // State & Data
    "zustand": "^5.0.7",                // State management
    "@tanstack/react-query": "^5.17.0", // Data fetching

    // Icons & Media
    "lucide-react": "^0.303.0",         // Icon library

    // Analytics
    "@vercel/analytics": "^1.1.1"       // Performance tracking
  }
}
```

### **Development Tools**

```json
{
  "devDependencies": {
    // Linting & Formatting
    "eslint": "^8.55.0",
    "prettier": "^3.0.0",
    "@typescript-eslint/eslint-plugin": "^6.0.0",

    // Testing
    "@testing-library/react": "^14.0.0",
    "jest": "^29.0.0",
    "cypress": "^13.0.0",

    // Build Tools
    "vite": "^5.0.0",
    "postcss": "^8.4.32",
    "autoprefixer": "^10.4.16"
  }
}
```

---

## 📋 Checklist for Developers

### **Before Development**
- [ ] Review Constellation Framework branding guidelines
- [ ] Check color contrast ratios
- [ ] Plan responsive breakpoints
- [ ] Set up component structure

### **During Development**
- [ ] Use semantic HTML
- [ ] Implement keyboard navigation
- [ ] Add ARIA labels where needed
- [ ] Test with screen readers
- [ ] Optimize images and fonts
- [ ] Implement loading states

### **Before Deployment**
- [ ] Run Lighthouse audit
- [ ] Test on multiple devices
- [ ] Verify WCAG compliance
- [ ] Check bundle size
- [ ] Test animations at 60fps
- [ ] Validate meta tags

---

## 🔗 Resources

- **Figma Design System**: [Coming Soon]
- **Storybook Components**: [Coming Soon]
- **Trinity Brand Guide**: `/branding/LUKHAS_TRINITY_FRAMEWORK.md`
- **Performance Dashboard**: [Coming Soon]
- **Accessibility Checker**: [axe DevTools](https://www.deque.com/axe/)

---

*Last Updated: 2025-08-19 | Version: 1.0.0 | LUKHAS AI Design System*
