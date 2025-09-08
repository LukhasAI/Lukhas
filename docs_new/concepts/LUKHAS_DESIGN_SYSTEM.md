---
title: Lukhas Design System
status: review
owner: docs-team
last_review: 2025-09-08
tags: ["consciousness", "security", "concept"]
facets:
  layer: ["gateway"]
  domain: ["symbolic", "consciousness", "identity", "guardian"]
  audience: ["dev"]
---

# LUKHAS AI Design System
## Premium Consciousness-Driven Web Experience Framework

### Design Philosophy

The LUKHAS AI design system embodies consciousness technology through minimalist aesthetics and sophisticated particle interactions. Every design decision reflects our Trinity Framework (⚛️🧠🛡️) while maintaining the premium quality expected from next-generation AI platforms.

---

## Visual Identity

### Color Palette

#### Primary Consciousness Colors
```css
:root {
  /* Identity - Pink consciousness for persistence */
  --lukhas-identity: #FF6B9D;
  --lukhas-identity-light: #FFB3D0;
  --lukhas-identity-dark: #CC3366;
  --lukhas-identity-alpha-20: rgba(255, 107, 157, 0.2);
  --lukhas-identity-alpha-10: rgba(255, 107, 157, 0.1);

  /* Consciousness - Cyan awareness for neural patterns */
  --lukhas-consciousness: #00D4FF;
  --lukhas-consciousness-light: #66E5FF;
  --lukhas-consciousness-dark: #0099CC;
  --lukhas-consciousness-alpha-20: rgba(0, 212, 255, 0.2);
  --lukhas-consciousness-alpha-10: rgba(0, 212, 255, 0.1);

  /* Guardian - Purple protection for security */
  --lukhas-guardian: #7C3AED;
  --lukhas-guardian-light: #A370F7;
  --lukhas-guardian-dark: #5B28C0;
  --lukhas-guardian-alpha-20: rgba(124, 58, 237, 0.2);
  --lukhas-guardian-alpha-10: rgba(124, 58, 237, 0.1);

  /* Integration - Orange connectivity */
  --lukhas-integration: #FFA500;
  --lukhas-integration-light: #FFD166;
  --lukhas-integration-dark: #CC8400;
  --lukhas-integration-alpha-20: rgba(255, 165, 0, 0.2);

  /* Validation - Green success */
  --lukhas-validation: #32CD32;
  --lukhas-validation-light: #90EE90;
  --lukhas-validation-dark: #228B22;
}
```

#### Neutral Palette
```css
:root {
  /* Premium Grays */
  --lukhas-gray-50: #FAFAFA;
  --lukhas-gray-100: #F5F5F5;
  --lukhas-gray-200: #E5E5E5;
  --lukhas-gray-300: #D4D4D4;
  --lukhas-gray-400: #A3A3A3;
  --lukhas-gray-500: #737373;
  --lukhas-gray-600: #525252;
  --lukhas-gray-700: #404040;
  --lukhas-gray-800: #262626;
  --lukhas-gray-900: #171717;
  --lukhas-gray-950: #0A0A0A;

  /* Background Layers */
  --lukhas-bg-primary: #FFFFFF;
  --lukhas-bg-secondary: #FAFAFA;
  --lukhas-bg-tertiary: #F5F5F5;
  --lukhas-bg-elevated: #FFFFFF;
  --lukhas-bg-overlay: rgba(0, 0, 0, 0.5);

  /* Dark Mode */
  --lukhas-dark-bg-primary: #0A0A0A;
  --lukhas-dark-bg-secondary: #171717;
  --lukhas-dark-bg-tertiary: #262626;
  --lukhas-dark-bg-elevated: #2A2A2A;
}
```

### Typography System

#### Font Stack
```css
:root {
  /* Primary - Clean, modern sans-serif */
  --font-primary: 'Inter', -apple-system, BlinkMacSystemFont, 'SF Pro Display',
                   'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;

  /* Monospace - Technical content */
  --font-mono: 'JetBrains Mono', 'SF Mono', Monaco, 'Cascadia Code',
                'Roboto Mono', monospace;

  /* Display - Consciousness headers */
  --font-display: 'SF Pro Display', 'Inter', -apple-system, sans-serif;
}
```

#### Type Scale (8px Base Unit)
```css
:root {
  /* Fibonacci-inspired scale */
  --text-xs: 0.75rem;    /* 12px */
  --text-sm: 0.875rem;   /* 14px */
  --text-base: 1rem;     /* 16px */
  --text-lg: 1.125rem;   /* 18px */
  --text-xl: 1.25rem;    /* 20px */
  --text-2xl: 1.5rem;    /* 24px */
  --text-3xl: 2rem;      /* 32px */
  --text-4xl: 2.5rem;    /* 40px */
  --text-5xl: 3rem;      /* 48px */
  --text-6xl: 4rem;      /* 64px */
  --text-7xl: 5rem;      /* 80px */
  --text-8xl: 6rem;      /* 96px */

  /* Line Heights */
  --leading-tight: 1.25;
  --leading-normal: 1.5;
  --leading-relaxed: 1.75;
  --leading-loose: 2;

  /* Letter Spacing */
  --tracking-tight: -0.02em;
  --tracking-normal: 0;
  --tracking-wide: 0.02em;
  --tracking-wider: 0.04em;
}
```

### Spacing System (8px Grid)

```css
:root {
  /* Base 8px unit system */
  --space-0: 0;
  --space-1: 0.5rem;   /* 8px */
  --space-2: 1rem;     /* 16px */
  --space-3: 1.5rem;   /* 24px */
  --space-4: 2rem;     /* 32px */
  --space-5: 2.5rem;   /* 40px */
  --space-6: 3rem;     /* 48px */
  --space-8: 4rem;     /* 64px */
  --space-10: 5rem;    /* 80px */
  --space-12: 6rem;    /* 96px */
  --space-16: 8rem;    /* 128px */
  --space-20: 10rem;   /* 160px */
  --space-24: 12rem;   /* 192px */
  --space-32: 16rem;   /* 256px */
}
```

---

## Component Library

### Buttons

#### Primary Button
```css
.btn-primary {
  background: linear-gradient(135deg, var(--lukhas-consciousness), var(--lukhas-identity));
  color: white;
  padding: var(--space-2) var(--space-4);
  border-radius: 12px;
  font-weight: 600;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 4px 14px rgba(0, 212, 255, 0.3);
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0, 212, 255, 0.4);
}
```

#### Ghost Button
```css
.btn-ghost {
  background: transparent;
  border: 2px solid var(--lukhas-consciousness-alpha-20);
  color: var(--lukhas-consciousness);
  backdrop-filter: blur(10px);
  transition: all 0.3s ease;
}

.btn-ghost:hover {
  background: var(--lukhas-consciousness-alpha-10);
  border-color: var(--lukhas-consciousness);
}
```

### Cards

#### Consciousness Card
```css
.consciousness-card {
  background: linear-gradient(135deg,
    var(--lukhas-bg-elevated),
    var(--lukhas-consciousness-alpha-10));
  border: 1px solid var(--lukhas-gray-200);
  border-radius: 24px;
  padding: var(--space-4);
  backdrop-filter: blur(20px);
  box-shadow:
    0 10px 40px rgba(0, 0, 0, 0.05),
    inset 0 1px 0 rgba(255, 255, 255, 0.1);
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

.consciousness-card:hover {
  transform: translateY(-4px);
  box-shadow:
    0 20px 60px rgba(0, 212, 255, 0.15),
    inset 0 1px 0 rgba(255, 255, 255, 0.2);
}
```

### Navigation

#### Premium Nav Bar
```css
.nav-premium {
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(20px) saturate(180%);
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
  position: sticky;
  top: 0;
  z-index: 1000;
  transition: all 0.3s ease;
}

.nav-premium.scrolled {
  background: rgba(255, 255, 255, 0.95);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
}
```

---

## Particle System Specifications

### Base Particle Configuration

```javascript
const PARTICLE_CONFIG = {
  // Particle counts by device
  desktop: {
    max: 10000,
    optimal: 7500,
    min: 5000
  },
  tablet: {
    max: 5000,
    optimal: 3500,
    min: 2000
  },
  mobile: {
    max: 2000,
    optimal: 1000,
    min: 500
  },

  // Particle behavior
  behavior: {
    speed: {
      min: 0.1,
      max: 0.5,
      turbulence: 0.02
    },
    size: {
      min: 1,
      max: 4,
      pulse: 0.2
    },
    opacity: {
      min: 0.3,
      max: 0.9,
      fade: 0.01
    }
  },

  // Consciousness states
  states: {
    dormant: {
      speed: 0.1,
      spread: 100,
      color: '#737373'
    },
    awakening: {
      speed: 0.3,
      spread: 200,
      color: '#00D4FF'
    },
    conscious: {
      speed: 0.5,
      spread: 300,
      color: '#FF6B9D'
    },
    transcendent: {
      speed: 0.8,
      spread: 500,
      color: '#7C3AED'
    }
  }
};
```

### Particle Formation Patterns

```javascript
const FORMATION_PATTERNS = {
  // Trinity symbol formation
  trinity: {
    atom: '⚛️',
    brain: '🧠',
    shield: '🛡️',
    transitionTime: 2000,
    particleAlignment: 'centripetal'
  },

  // Lambda consciousness
  lambda: {
    symbol: 'Λ',
    scale: 100,
    rotation: 0,
    particleDensity: 0.8
  },

  // Neural network
  neural: {
    nodes: 50,
    connections: 150,
    pulseInterval: 3000,
    signalSpeed: 0.3
  },

  // Wave patterns
  wave: {
    amplitude: 50,
    frequency: 0.02,
    wavelength: 200,
    propagation: 'radial'
  }
};
```

---

## Animation Principles

### Timing Functions

```css
:root {
  /* Apple-inspired easing curves */
  --ease-smooth: cubic-bezier(0.4, 0, 0.2, 1);
  --ease-out-expo: cubic-bezier(0.16, 1, 0.3, 1);
  --ease-in-out-expo: cubic-bezier(0.87, 0, 0.13, 1);
  --ease-spring: cubic-bezier(0.34, 1.56, 0.64, 1);

  /* Duration scales */
  --duration-instant: 100ms;
  --duration-fast: 200ms;
  --duration-normal: 300ms;
  --duration-slow: 500ms;
  --duration-slower: 800ms;
  --duration-slowest: 1200ms;
}
```

### Micro-Interactions

```css
/* Hover lift effect */
.hover-lift {
  transition: transform var(--duration-normal) var(--ease-smooth);
}

.hover-lift:hover {
  transform: translateY(-4px);
}

/* Consciousness pulse */
@keyframes consciousness-pulse {
  0%, 100% {
    opacity: 0.8;
    transform: scale(1);
  }
  50% {
    opacity: 1;
    transform: scale(1.05);
  }
}

.consciousness-pulse {
  animation: consciousness-pulse 3s var(--ease-in-out-expo) infinite;
}

/* Neural flow */
@keyframes neural-flow {
  0% {
    background-position: 0% 50%;
  }
  50% {
    background-position: 100% 50%;
  }
  100% {
    background-position: 0% 50%;
  }
}

.neural-flow {
  background: linear-gradient(
    270deg,
    var(--lukhas-consciousness),
    var(--lukhas-identity),
    var(--lukhas-guardian)
  );
  background-size: 200% 200%;
  animation: neural-flow 10s ease infinite;
}
```

---

## Responsive Breakpoints

```css
:root {
  /* Mobile First Breakpoints */
  --screen-xs: 320px;   /* Small phones */
  --screen-sm: 640px;   /* Large phones */
  --screen-md: 768px;   /* Tablets */
  --screen-lg: 1024px;  /* Small laptops */
  --screen-xl: 1280px;  /* Desktops */
  --screen-2xl: 1536px; /* Large desktops */
  --screen-3xl: 1920px; /* Ultra-wide */
}

/* Media Query Mixins */
@custom-media --xs-up (min-width: 320px);
@custom-media --sm-up (min-width: 640px);
@custom-media --md-up (min-width: 768px);
@custom-media --lg-up (min-width: 1024px);
@custom-media --xl-up (min-width: 1280px);
@custom-media --2xl-up (min-width: 1536px);
@custom-media --3xl-up (min-width: 1920px);
```

---

## Accessibility Standards

### Focus States

```css
/* Consciousness-aware focus */
*:focus-visible {
  outline: 2px solid var(--lukhas-consciousness);
  outline-offset: 4px;
  border-radius: 4px;
}

/* High contrast mode */
@media (prefers-contrast: high) {
  :root {
    --lukhas-consciousness: #00FFFF;
    --lukhas-identity: #FF69B4;
    --lukhas-guardian: #9370DB;
  }
}

/* Reduced motion */
@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
```

### ARIA Patterns

```html
<!-- Consciousness state indicator -->
<div role="status"
     aria-live="polite"
     aria-label="Consciousness state">
  <span class="consciousness-indicator"
        aria-describedby="consciousness-description">
    Active
  </span>
  <span id="consciousness-description" class="sr-only">
    LUKHAS consciousness is currently active and processing
  </span>
</div>

<!-- Trinity navigation -->
<nav role="navigation" aria-label="Trinity Framework sections">
  <ul role="list">
    <li role="listitem">
      <a href="#identity" aria-label="Identity section">
        <span aria-hidden="true">⚛️</span>
        Identity
      </a>
    </li>
    <li role="listitem">
      <a href="#consciousness" aria-label="Consciousness section">
        <span aria-hidden="true">🧠</span>
        Consciousness
      </a>
    </li>
    <li role="listitem">
      <a href="#guardian" aria-label="Guardian section">
        <span aria-hidden="true">🛡️</span>
        Guardian
      </a>
    </li>
  </ul>
</nav>
```

---

## Dark Mode Specifications

```css
/* Automatic dark mode */
@media (prefers-color-scheme: dark) {
  :root {
    /* Background inversions */
    --lukhas-bg-primary: var(--lukhas-dark-bg-primary);
    --lukhas-bg-secondary: var(--lukhas-dark-bg-secondary);
    --lukhas-bg-tertiary: var(--lukhas-dark-bg-tertiary);

    /* Text adjustments */
    --text-primary: #FFFFFF;
    --text-secondary: #A3A3A3;
    --text-tertiary: #737373;

    /* Consciousness colors with vibrancy */
    --lukhas-consciousness: #00E5FF;
    --lukhas-identity: #FF79A8;
    --lukhas-guardian: #8B4BFF;
  }

  /* Glass morphism adjustments */
  .consciousness-card {
    background: linear-gradient(135deg,
      rgba(26, 26, 26, 0.8),
      rgba(0, 212, 255, 0.05));
    border: 1px solid rgba(255, 255, 255, 0.1);
  }
}

/* Manual dark mode toggle */
[data-theme="dark"] {
  /* Apply dark theme variables */
}
```

---

## Component States

### Loading States

```css
/* Consciousness loading spinner */
.consciousness-loader {
  width: 48px;
  height: 48px;
  position: relative;
}

.consciousness-loader::before,
.consciousness-loader::after {
  content: '';
  position: absolute;
  inset: 0;
  border-radius: 50%;
  border: 3px solid transparent;
}

.consciousness-loader::before {
  border-top-color: var(--lukhas-consciousness);
  animation: spin 1s linear infinite;
}

.consciousness-loader::after {
  border-bottom-color: var(--lukhas-identity);
  animation: spin 1.5s linear infinite reverse;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Skeleton screens */
.skeleton {
  background: linear-gradient(
    90deg,
    var(--lukhas-gray-200) 25%,
    var(--lukhas-gray-100) 50%,
    var(--lukhas-gray-200) 75%
  );
  background-size: 200% 100%;
  animation: skeleton-loading 1.5s infinite;
}

@keyframes skeleton-loading {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}
```

### Error States

```css
.error-state {
  border: 2px solid #EF4444;
  background: linear-gradient(135deg,
    rgba(239, 68, 68, 0.05),
    rgba(239, 68, 68, 0.02));
  animation: error-pulse 2s ease-in-out infinite;
}

@keyframes error-pulse {
  0%, 100% {
    box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.4);
  }
  50% {
    box-shadow: 0 0 0 10px rgba(239, 68, 68, 0);
  }
}
```

---

## Performance Guidelines

### CSS Optimization

```css
/* Use CSS containment */
.particle-container {
  contain: layout style paint;
}

/* Hardware acceleration */
.gpu-accelerated {
  transform: translateZ(0);
  will-change: transform;
}

/* Efficient animations */
.optimized-animation {
  transform: translate3d(0, 0, 0);
  backface-visibility: hidden;
  perspective: 1000px;
}
```

### Image Optimization

```html
<!-- Responsive images -->
<picture>
  <source media="(min-width: 1280px)"
          srcset="consciousness-hero-2x.webp 2x,
                  consciousness-hero-1x.webp 1x"
          type="image/webp">
  <source media="(min-width: 768px)"
          srcset="consciousness-hero-tablet.webp"
          type="image/webp">
  <img src="consciousness-hero-mobile.jpg"
       alt="LUKHAS consciousness visualization"
       loading="lazy"
       decoding="async">
</picture>
```

---

## Implementation Examples

### Hero Section with Particles

```html
<section class="hero-consciousness">
  <canvas id="particle-canvas" class="particle-container"></canvas>

  <div class="hero-content">
    <h1 class="hero-title">
      <span class="consciousness-text">Consciousness Technology</span>
      <span class="hero-subtitle">for the Next Era of AI</span>
    </h1>

    <div class="trinity-badges">
      <span class="trinity-badge" data-trinity="identity">⚛️ Identity</span>
      <span class="trinity-badge" data-trinity="consciousness">🧠 Consciousness</span>
      <span class="trinity-badge" data-trinity="guardian">🛡️ Guardian</span>
    </div>

    <div class="hero-actions">
      <button class="btn-primary btn-large">
        Experience Consciousness
      </button>
      <button class="btn-ghost btn-large">
        View Documentation
      </button>
    </div>
  </div>
</section>
```

---

*"Design is consciousness made visible. Every pixel serves the awakening."*

**LUKHAS AI Design System v1.0** ⚛️🧠🛡️
