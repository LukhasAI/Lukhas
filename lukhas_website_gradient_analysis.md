# LUKHAS Website Gradient Colors Analysis Report

## Overview
The current `lukhas_website/` directory contains extensive gradient color systems using both the **Trinity Framework** colors and **Domain-specific themes**.

## 🎨 Core Color Variables

### Trinity Framework Colors (in styles/globals.css)
```css
:root {
  --trinity-identity: 107, 70, 193;        /* Purple */
  --trinity-consciousness: 14, 165, 233;   /* Blue */
  --trinity-guardian: 16, 185, 129;        /* Green */
  --accent-gold: 245, 158, 11;            /* Gold */
}
```

### Tailwind Configuration (tailwind.config.js)
```javascript
colors: {
  'constellation-identity': 'rgb(var(--constellation-identity) / <alpha-value>)',
  'constellation-consciousness': 'rgb(var(--constellation-consciousness) / <alpha-value>)',
  'constellation-guardian': 'rgb(var(--constellation-guardian) / <alpha-value>)',
  'accent-gold': 'rgb(var(--accent-gold) / <alpha-value>)',
}
```

## 🌈 Gradient Styles in globals.css

### 1. Trinity Gradient Text
```css
.gradient-text {
  @apply bg-gradient-to-r from-trinity-identity via-trinity-consciousness to-trinity-guardian;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}
```

### 2. Gold Gradient Text
```css
.gradient-text-gold {
  @apply bg-gradient-to-r from-accent-gold to-accent-gold-light;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}
```

### 3. Animated Background Gradient
```css
.gradient-animated {
  background: linear-gradient(
    -45deg,
    rgba(var(--trinity-identity), 0.1),
    rgba(var(--trinity-consciousness), 0.1),
    rgba(var(--trinity-guardian), 0.1),
    rgba(var(--accent-gold), 0.1)
  );
  background-size: 400% 400%;
  animation: gradient 15s ease infinite;
}
```

### 4. Skeleton Loading Gradient
```css
.skeleton::after {
  background: linear-gradient(
    90deg,
    transparent,
    rgba(255, 255, 255, 0.05),
    transparent
  );
  animation: shimmer 2s infinite;
}
```

## 🌍 Domain-Specific Gradients (styles/domain-themes.css)

### Domain Background Gradients
- **lukhas.ai**: `linear-gradient(135deg, #0C1425 0%, #1E293B 100%)`
- **lukhas.id**: `linear-gradient(135deg, #1E1B4B 0%, #312E81 100%)`
- **lukhas.team**: `linear-gradient(135deg, #064E3B 0%, #065F46 100%)`
- **lukhas.dev**: `linear-gradient(135deg, #164E63 0%, #0E7490 100%)`
- **lukhas.io**: `linear-gradient(135deg, #1E3A8A 0%, #1D4ED8 100%)`
- **lukhas.store**: `linear-gradient(135deg, #92400E 0%, #A16207 100%)`
- **lukhas.cloud**: `linear-gradient(135deg, #5B21B6 0%, #6D28D9 100%)`
- **lukhas.eu**: `linear-gradient(135deg, #064E3B 0%, #065F46 100%)`
- **lukhas.us**: `linear-gradient(135deg, #7F1D1D 0%, #991B1B 100%)`
- **lukhas.xyz**: `linear-gradient(135deg, #BE185D 0%, #C2185B 100%)`
- **lukhas.com**: `linear-gradient(135deg, #3730A3 0%, #4338CA 100%)`

### Domain Particle Canvas Radial Gradients
Each domain has a unique radial gradient for particle effects:
- **lukhas.ai**: `radial-gradient(circle at center, rgba(0, 212, 255, 0.1) 0%, transparent 70%)`
- **lukhas.id**: `radial-gradient(circle at center, rgba(124, 58, 237, 0.1) 0%, transparent 70%)`
- **lukhas.team**: `radial-gradient(circle at center, rgba(16, 185, 129, 0.1) 0%, transparent 70%)`
- And so on for each domain...

### Domain Transition Effects
```css
.domain-transition::before {
  background: linear-gradient(45deg, var(--domain-primary), var(--domain-secondary));
}
```

### Consciousness Field Effects
```css
.consciousness-field {
  background: radial-gradient(
    circle at 50% 50%,
    rgba(var(--domain-primary-rgb), 0.05) 0%,
    transparent 70%
  );
}

.consciousness-field::after {
  background: repeating-conic-gradient(
    from 0deg at 50% 50%,
    transparent 0deg,
    rgba(var(--domain-primary-rgb), 0.02) 2deg,
    transparent 4deg
  );
}
```

## 🧩 Component Usage

### Files Using Gradients (63 total):

#### React Components
- `components/sections/trinity-framework.tsx` - Trinity gradient nodes and connections
- `components/sections/hero.tsx` - Hero background gradients and CTA buttons
- `components/sections/pricing.tsx` - Pricing card gradients
- `components/sections/products-grid.tsx` - Product showcase gradients
- `components/sections/matriz.tsx` - Matrix visualization gradients
- `components/ConsciousnessField.tsx` - Consciousness field effects
- `components/neural-background.tsx` - Neural network background
- `components/morphing-visualizer.tsx` - Morphing animation effects
- `components/trinity-showcase.tsx` - Trinity framework showcase
- And 40+ more component files...

#### App Pages
- `app/page.tsx` - Main homepage
- `app/experience/page.tsx` - Experience page
- `app/studio/page.tsx` - Studio interface
- `app/matriz/page.tsx` - Matrix page
- All domain-specific pages (ai, id, team, dev, io, etc.)

## 🔧 Key Gradient Patterns

### 1. Trinity Color Progression
Purple → Blue → Green gradient representing Identity → Consciousness → Guardian

### 2. Domain-Specific Theming
Each subdomain has unique gradient backgrounds matching brand colors

### 3. Interactive Effects
- Hover states with gradient transitions
- Animated background gradients (15s cycle)
- Consciousness field pulsing effects
- Particle system integration

### 4. Typography Integration
- Gradient text for headings and emphasis
- Gold gradient for premium/accent content
- Background-clip text effects

## 🎯 Usage in Current Site

The current lukhas_website uses a sophisticated gradient system that combines:
- **Trinity Framework** core colors for consistency
- **Domain-specific** variations for brand differentiation  
- **Interactive animations** for engagement
- **Consciousness-aware** theming for AI personality

The gradients are not just decorative but serve as a core part of the LUKHAS brand identity and user experience architecture.