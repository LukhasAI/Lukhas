# Icon Design Specification for lukhas.team

**Complete Visual Identity System for LUKHAS Platform**

**Created**: 2025-11-10
**Status**: Design Brief Ready for Delegation
**Purpose**: Bespoke icon system for consciousness-aware developer platform
**Timeline**: 2 weeks (initial designs) + 1 week (revisions)

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Design Philosophy](#design-philosophy)
3. [Constellation Framework Icons](#constellation-framework-icons-8-stars)
4. [Platform Feature Icons](#platform-feature-icons)
5. [Technical Specifications](#technical-specifications)
6. [Animation Requirements](#animation-requirements)
7. [Implementation Guide](#implementation-guide)
8. [Designer Workflow](#designer-workflow)
9. [Delivery Format](#delivery-format)

---

## Executive Summary

### Project Scope

**Deliverables**:
- **8 Constellation Framework Icons** (⚛️ Identity, ✦ Memory, 🔬 Vision, 🌱 Bio, 🌙 Dream, ⚖️ Ethics, 🛡️ Guardian, ⚛️ Quantum)
- **15 Platform Feature Icons** (MATRIZ, Memory Healix, Test Runner, Coverage, etc.)
- **3 Color Variants** per icon (default, success, error)
- **2 Animation States** (idle, active)
- **React Components** with TypeScript + Framer Motion
- **Figma Source Files**

**Timeline**:
- Week 1: Initial designs + feedback round
- Week 2: Revisions + finalization
- Week 3: Component implementation + delivery

**Designer Requirements**:
- Experience with icon systems (Heroicons, Lucide, Phosphor)
- Proficiency in Figma + SVG optimization
- Understanding of React/TypeScript (for component export)
- Bonus: Animation experience with Lottie or Framer Motion

---

## Design Philosophy

### Visual Language

**Core Principles**:

1. **Consciousness-Aware**: Each icon should feel "alive" - not static, but breathing
2. **Minimal & Precise**: Clean lines, no unnecessary detail (think Apple SF Symbols)
3. **Scalable**: Crisp at 16px, detailed at 64px
4. **Cohesive**: Family resemblance across all 23 icons
5. **Accessible**: WCAG 2.1 AA compliant (3:1 contrast minimum)

**Style References**:
- ✅ **Heroicons** - Clean, 2px stroke, friendly
- ✅ **Lucide** - Geometric, consistent proportions
- ✅ **Phosphor** - Duotone variants, expressive
- ❌ **Material Icons** - Too generic for consciousness theme
- ❌ **Font Awesome** - Too busy, inconsistent quality

**Mood Board**:
```
Geometric         Organic           Consciousness
   ████              ╱╲               ◉ ◉
   ████             ╱  ╲              │ │
   ████            ▕    ▏           ─┼─┼─
   ████             ╲  ╱              │ │
   ████              ╲╱               ◉ ◉

  Clean             Flow            Distributed
```

---

## Constellation Framework Icons (8 Stars)

### Design Brief Overview

**Constraints**:
- **Base Size**: 24x24px viewBox
- **Stroke Width**: 2px (consistent across all)
- **Corner Radius**: 2px (rounded, friendly)
- **Padding**: 2px inside viewBox (icons don't touch edges)
- **Color Palette**: Single-color with 3 variants (see Technical Specs)

---

### 1. ⚛️ Identity Star

**Concept**: Lambda (λ) + Human Figure

**Visual Elements**:
- Lambda symbol (λ) as primary shape
- Stylized human silhouette integrated into lambda
- Fingerprint or biometric pattern in background (subtle)

**Symbolism**:
- Lambda = Unique identity (Lambda ID = ΛiD)
- Human figure = Individual consciousness
- Fingerprint = Uniqueness

**Design Direction**:
```
     ╱╲
    ╱  ╲        Lambda overlaid with
   ╱ ⚈⚈ ╲       human head/shoulders
  ╱  ││  ╲
 ╱   ││   ╲
```

**Color**: Purple (`hsl(270, 60%, 55%)`)

**Use Cases**:
- User profile icon
- Authentication buttons
- ΛiD system branding

---

### 2. ✦ Memory Star

**Concept**: Brain + Database Nodes

**Visual Elements**:
- Simplified brain outline (top hemisphere)
- Connected nodes/dots (neural network)
- Small database cylinder integrated

**Symbolism**:
- Brain = Cognitive memory
- Network = Distributed storage
- Persistence = Database

**Design Direction**:
```
    ╔═══╗
   ╱ ◉─◉ ╲      Brain outline with
  │  │╲│  │     connected neural nodes
   ╲ ◉─◉ ╱      + database symbol
    ╚═══╝
```

**Color**: Blue (`hsl(200, 60%, 55%)`)

**Use Cases**:
- Memory Healix branding
- Test history/recall features
- Context preservation indicators

---

### 3. 🔬 Vision Star

**Concept**: Eye + Lens + Pattern Recognition

**Visual Elements**:
- Stylized eye with geometric iris
- Concentric circles (focus/zoom effect)
- Grid pattern overlay (pattern recognition)

**Symbolism**:
- Eye = Perception
- Lens = Focus/analysis
- Grid = Pattern recognition

**Design Direction**:
```
     ╱─────╲
    │  ◉    │     Eye with geometric
    │ ╱│╲   │     iris and focus rings
     ╲─────╱
```

**Color**: Teal (`hsl(160, 60%, 55%)`)

**Use Cases**:
- Code review features
- Visual analysis tools
- Pattern detection indicators

---

### 4. 🌱 Bio Star

**Concept**: Seedling + DNA Helix

**Visual Elements**:
- Growing plant with two leaves
- DNA double helix as stem/roots
- Curved organic lines (growth trajectory)

**Symbolism**:
- Seedling = Organic growth
- DNA = Bio-inspired algorithms
- Curves = Natural adaptation

**Design Direction**:
```
      ╱╲
     ╱  ╲        Seedling with
    │ ⚬⚬ │       DNA helix as stem
     ╲  ╱
      ╲╱╲╱╲     (organic curves)
```

**Color**: Green (`hsl(120, 60%, 55%)`)

**Use Cases**:
- Bio-adaptive workflow indicators
- Organic growth metrics
- Natural adaptation features

---

### 5. 🌙 Dream Star

**Concept**: Crescent Moon + Thought Cloud + Stars

**Visual Elements**:
- Crescent moon (main shape)
- Thought bubble/cloud
- Small stars (sparkle, creativity)
- Ethereal glow effect (subtle)

**Symbolism**:
- Moon = Unconscious processing
- Cloud = Imagination
- Stars = Creative insights

**Design Direction**:
```
      ★
    ╱───╲        Crescent moon with
   │ ≋≋  │       thought cloud and
    ╲   ╱        sparkle stars
      ◡
```

**Color**: Magenta (`hsl(280, 60%, 65%)`)

**Use Cases**:
- Creative suggestions
- Predictive features
- Imaginative analysis

---

### 6. ⚖️ Ethics Star

**Concept**: Balance Scale + Checkmark + Heart

**Visual Elements**:
- Traditional balance scale
- Checkmark in one scale pan (approval)
- Heart in other pan (values)

**Symbolism**:
- Scale = Balanced judgment
- Checkmark = Ethical approval
- Heart = Human values

**Design Direction**:
```
      ╱─╲
     ╱   ╲       Balance scale with
    ╱     ╲      checkmark vs. heart
   ✓       ♡     (values-driven)
```

**Color**: Orange (`hsl(30, 60%, 55%)`)

**Use Cases**:
- GDPR compliance indicators
- Ethical review status
- Values alignment checks

---

### 7. 🛡️ Guardian Star

**Concept**: Shield + Lock + Eye

**Visual Elements**:
- Shield shape (main outline)
- Padlock in center
- Watchful eye (always vigilant)
- Constitutional document symbol

**Symbolism**:
- Shield = Protection
- Lock = Security enforcement
- Eye = Constant monitoring

**Design Direction**:
```
     ╱────╲
    │  🔒  │      Shield with lock
    │  ◉   │      and watchful eye
     ╲────╱       (vigilant guardian)
```

**Color**: Red (`hsl(0, 60%, 55%)`)

**Use Cases**:
- Constitutional AI branding
- Security alerts
- Guardian review status

---

### 8. ⚛️ Quantum Star

**Concept**: Atom + Superposition + Entanglement

**Visual Elements**:
- Atomic structure (nucleus + electrons)
- Overlapping circles (superposition)
- Connected particles (entanglement)
- Wave patterns (quantum behavior)

**Symbolism**:
- Atom = Quantum-inspired
- Superposition = Multiple states
- Entanglement = Distributed connection

**Design Direction**:
```
      ◉
     ╱│╲         Atom with orbiting
    ◉ ◉ ◉        electrons and
     ╲│╱         quantum wave pattern
      ◉
```

**Color**: Indigo (`hsl(240, 60%, 55%)`)

**Use Cases**:
- Quantum-inspired algorithm indicators
- Parallel processing features
- Distributed computation

---

## Platform Feature Icons

### 9. MATRIZ Cognitive Engine

**Concept**: Brain + Circuit Board + Flow

**Visual Elements**:
- Brain outline (simplified)
- Circuit paths overlaid
- Flowing data streams

**Color**: Blue-Purple gradient

**Size**: 32x32px (larger, primary brand icon)

---

### 10. Memory Healix (Self-Healing)

**Concept**: DNA Helix + Bandaid/Repair + Circular Flow

**Visual Elements**:
- Double helix (spiral)
- Repair symbol (cross/bandaid)
- Circular arrows (self-renewal)

**Color**: Green (`hsl(142, 71%, 45%)`)

**Animation**: Rotating helix with pulsing repair icon

---

### 11. Test Runner

**Concept**: Play Button + Checkmarks + Progress

**Visual Elements**:
- Play/run icon (triangle)
- Checkmark trail
- Progress indicator

**Color**: Blue (`hsl(200, 60%, 55%)`)

---

### 12. Coverage Tracker

**Concept**: Target + Percentage + Checkered Pattern

**Visual Elements**:
- Bullseye/target circles
- Percentage number (85%)
- Checkered pattern (code coverage)

**Color**: Green (success) / Orange (warning) / Red (error)

---

### 13. Performance Dashboard

**Concept**: Speedometer + Lightning + Graph

**Visual Elements**:
- Speedometer gauge
- Lightning bolt (speed)
- Upward trend line

**Color**: Purple (`hsl(270, 60%, 55%)`)

---

### 14. Flaky Test Detector

**Concept**: Broken Link + Warning + Oscillation

**Visual Elements**:
- Broken chain link
- Warning triangle
- Wave pattern (instability)

**Color**: Orange (`hsl(38, 92%, 50%)`)

---

### 15. Consciousness Graph

**Concept**: Network Nodes + Brain + Connections

**Visual Elements**:
- Connected nodes (graph)
- Central brain icon
- Flowing connections

**Color**: Multi-color (all 8 star colors)

---

### 16. Build Status

**Concept**: Construction Crane + Checkmark/X + Gears

**Visual Elements**:
- Simple crane/wrench
- Status indicator (✓ or ✗)
- Gear (automation)

**Color**: Green (success) / Red (failure) / Orange (in-progress)

---

### 17. Deployment Pipeline

**Concept**: Rocket + Stages + Arrow Flow

**Visual Elements**:
- Rocket (deployment)
- Multi-stage rocket (pipeline stages)
- Directional arrow

**Color**: Blue (`hsl(200, 60%, 55%)`)

---

### 18. API Explorer

**Concept**: Compass + Code Brackets + Search

**Visual Elements**:
- Compass (exploration)
- Code symbol `{ }`
- Magnifying glass

**Color**: Teal (`hsl(160, 60%, 55%)`)

---

### 19. Code Search

**Concept**: Magnifying Glass + Code + File Tree

**Visual Elements**:
- Large magnifying glass
- Code snippet inside
- File tree background

**Color**: Purple (`hsl(270, 60%, 55%)`)

---

### 20. Team Dashboard

**Concept**: People + Graph + Collaboration

**Visual Elements**:
- Multiple user silhouettes
- Upward trend graph
- Handshake/connection

**Color**: Blue (`hsl(200, 60%, 55%)`)

---

### 21. Alert/Notification

**Concept**: Bell + Badge + Pulse

**Visual Elements**:
- Bell outline
- Notification badge (number)
- Pulsing circle

**Color**: Red (critical) / Orange (warning) / Blue (info)

**Animation**: Shake + pulse on new alert

---

### 22. Settings/Preferences

**Concept**: Gear + Sliders + Profile

**Visual Elements**:
- Traditional gear
- Slider controls
- User preference icon

**Color**: Neutral gray (`hsl(215, 16.3%, 46.9%)`)

---

### 23. Documentation

**Concept**: Book + Code + Bookmark

**Visual Elements**:
- Open book
- Code snippet on page
- Bookmark ribbon

**Color**: Purple (`hsl(270, 60%, 55%)`)

---

## Technical Specifications

### Size Standards

| Use Case | Size (px) | Export Sizes |
|----------|-----------|--------------|
| **Inline Icons** | 16x16 | 16, 20, 24 |
| **Navigation** | 20x20 | 20, 24 |
| **Dashboard Cards** | 24x24 | 24, 32, 48 |
| **Hero Sections** | 48x48 | 48, 64, 96 |
| **Brand/Logo** | 64x64+ | 64, 96, 128, 256 |

**Note**: All icons designed at 24x24px viewBox, scaled up/down as needed.

---

### Color Variants

#### 1. Default (Constellation Star Colors)

```css
/* CSS Variables */
--constellation-identity: hsl(270, 60%, 55%);    /* Purple */
--constellation-memory: hsl(200, 60%, 55%);      /* Blue */
--constellation-vision: hsl(160, 60%, 55%);      /* Teal */
--constellation-bio: hsl(120, 60%, 55%);         /* Green */
--constellation-dream: hsl(280, 60%, 65%);       /* Magenta */
--constellation-ethics: hsl(30, 60%, 55%);       /* Orange */
--constellation-guardian: hsl(0, 60%, 55%);      /* Red */
--constellation-quantum: hsl(240, 60%, 55%);     /* Indigo */
```

#### 2. Success Variant

```css
--success: hsl(142, 71%, 45%);  /* Green */
--success-bg: hsl(142, 76%, 95%);
--success-foreground: hsl(142, 71%, 25%);
```

#### 3. Warning Variant

```css
--warning: hsl(38, 92%, 50%);   /* Orange */
--warning-bg: hsl(38, 100%, 95%);
--warning-foreground: hsl(38, 92%, 30%);
```

#### 4. Error Variant

```css
--error: hsl(0, 72%, 51%);      /* Red */
--error-bg: hsl(0, 100%, 95%);
--error-foreground: hsl(0, 72%, 31%);
```

---

### Stroke & Fill

**Default Style**: Outline (stroke-only)

```svg
<svg viewBox="0 0 24 24" stroke="currentColor" fill="none" stroke-width="2">
  <!-- Icon paths -->
</svg>
```

**Duotone Option** (for larger sizes 48px+):

```svg
<svg viewBox="0 0 24 24">
  <!-- Background shape (20% opacity) -->
  <path fill="currentColor" opacity="0.2" d="..." />
  <!-- Foreground outline -->
  <path stroke="currentColor" fill="none" stroke-width="2" d="..." />
</svg>
```

---

### Accessibility

**WCAG 2.1 AA Compliance**:

1. **Contrast Ratio**: 3:1 minimum (for icons 24px+)
2. **Focus States**: 2px outline on keyboard focus
3. **Alt Text**: All icons have semantic `aria-label`

**Example**:
```tsx
<svg aria-label="Memory Star - View memory system" role="img">
  <title>Memory Star</title>
  <!-- Icon paths -->
</svg>
```

---

## Animation Requirements

### Framer Motion Variants

#### 1. Idle State (Default)

```typescript
const idleVariant = {
  scale: 1,
  rotate: 0,
  opacity: 1,
};
```

#### 2. Hover State

```typescript
const hoverVariant = {
  scale: 1.1,
  transition: {
    type: 'spring',
    stiffness: 300,
    damping: 10,
  },
};
```

#### 3. Active/Loading State

```typescript
const activeVariant = {
  rotate: [0, 360],
  transition: {
    duration: 2,
    repeat: Infinity,
    ease: 'linear',
  },
};
```

#### 4. Success State (Checkmark Bounce)

```typescript
const successVariant = {
  scale: [1, 1.2, 1],
  opacity: [0, 1],
  transition: {
    duration: 0.5,
    times: [0, 0.5, 1],
  },
};
```

#### 5. Error State (Shake)

```typescript
const errorVariant = {
  x: [-10, 10, -10, 10, 0],
  transition: {
    duration: 0.4,
  },
};
```

---

### Specific Icon Animations

**Memory Healix** (Self-Healing):
- Continuous slow rotation (helix spinning)
- Pulse effect on repair icon

**MATRIZ** (Cognitive Processing):
- Neural connections "firing" (path stroke animation)
- Subtle glow pulse

**Test Runner**:
- Progress bar filling
- Checkmarks appearing sequentially

**Constellation Stars** (on hover):
- Gentle glow effect (filter: drop-shadow)
- Scale up 110%

---

## Implementation Guide

### React Component Structure

**File**: `components/icons/ConstellationIcon.tsx`

```typescript
import { motion, Variants } from 'framer-motion';

interface ConstellationIconProps {
  star: 'identity' | 'memory' | 'vision' | 'bio' | 'dream' | 'ethics' | 'guardian' | 'quantum';
  size?: number;
  variant?: 'default' | 'success' | 'warning' | 'error';
  animated?: boolean;
  className?: string;
}

const starColors = {
  identity: 'hsl(270, 60%, 55%)',
  memory: 'hsl(200, 60%, 55%)',
  vision: 'hsl(160, 60%, 55%)',
  bio: 'hsl(120, 60%, 55%)',
  dream: 'hsl(280, 60%, 65%)',
  ethics: 'hsl(30, 60%, 55%)',
  guardian: 'hsl(0, 60%, 55%)',
  quantum: 'hsl(240, 60%, 55%)',
};

const hoverVariant: Variants = {
  rest: { scale: 1 },
  hover: {
    scale: 1.1,
    filter: 'drop-shadow(0 0 8px currentColor)',
    transition: { type: 'spring', stiffness: 300 },
  },
};

export function ConstellationIcon({
  star,
  size = 24,
  variant = 'default',
  animated = true,
  className,
}: ConstellationIconProps) {
  const color = variant === 'default' ? starColors[star] : undefined;

  return (
    <motion.svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      stroke={color || 'currentColor'}
      fill="none"
      strokeWidth={2}
      strokeLinecap="round"
      strokeLinejoin="round"
      className={className}
      variants={animated ? hoverVariant : undefined}
      initial="rest"
      whileHover={animated ? 'hover' : undefined}
      aria-label={`${star} star icon`}
      role="img"
    >
      {/* Icon paths (imported from SVG) */}
      {getStarPaths(star)}
    </motion.svg>
  );
}

function getStarPaths(star: string) {
  // SVG paths for each star icon
  // (Exported from Figma as React components)
  const paths = {
    identity: <path d="M12 2L8 8L12 14L16 8L12 2Z M12 10a2 2 0 100-4 2 2 0 000 4Z" />,
    memory: <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2Zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8Z M8 12h8 M12 8v8" />,
    // ... other star paths
  };

  return paths[star as keyof typeof paths] || null;
}
```

---

## Designer Workflow

### Tools Required

1. **Figma** (primary design tool)
   - Icon design and iteration
   - Variant management
   - Prototyping animations

2. **SVGOMG** (https://jakearchibald.github.io/svgomg/)
   - SVG optimization
   - Remove unnecessary attributes
   - Reduce file size

3. **React SVGR** (https://react-svgr.com/playground/)
   - Convert SVG to React components
   - Add TypeScript types
   - Configure props

---

### Step-by-Step Process

#### Week 1: Initial Designs

**Day 1-2**: Constellation Framework Icons (8 stars)
- Create 24x24px frames in Figma
- Design each star icon based on briefs above
- Export SVGs for review

**Day 3-4**: Platform Feature Icons (15 icons)
- Design feature icons
- Ensure visual consistency with constellation icons
- Export SVGs

**Day 5**: Review & Feedback
- Present designs to team
- Iterate based on feedback

#### Week 2: Revisions & Variants

**Day 6-7**: Color Variants
- Create success/warning/error variants
- Test contrast ratios (WCAG AA)

**Day 8-9**: Size Variants
- Test icons at 16px, 20px, 24px, 48px
- Ensure legibility at all sizes

**Day 10**: Finalization
- Optimize SVGs with SVGOMG
- Export all variants

#### Week 3: Component Implementation

**Day 11-12**: React Components
- Convert SVGs to React components with SVGR
- Add TypeScript types
- Implement Framer Motion animations

**Day 13**: Testing
- Test icons in lukhas.team frontend
- Verify animations and accessibility

**Day 14**: Delivery
- Package all assets
- Provide documentation

---

## Delivery Format

### File Structure

```
lukhas-team-icons/
├── figma/
│   └── lukhas-team-icons.fig           # Figma source file
├── svg/
│   ├── constellation/                  # 8 constellation star icons
│   │   ├── identity.svg
│   │   ├── memory.svg
│   │   ├── vision.svg
│   │   ├── bio.svg
│   │   ├── dream.svg
│   │   ├── ethics.svg
│   │   ├── guardian.svg
│   │   └── quantum.svg
│   └── features/                       # 15 platform feature icons
│       ├── matriz.svg
│       ├── memory-healix.svg
│       ├── test-runner.svg
│       ├── coverage.svg
│       ├── performance.svg
│       ├── flaky-test.svg
│       ├── consciousness-graph.svg
│       ├── build-status.svg
│       ├── deployment.svg
│       ├── api-explorer.svg
│       ├── code-search.svg
│       ├── team.svg
│       ├── alert.svg
│       ├── settings.svg
│       └── documentation.svg
├── react/
│   ├── constellation/                  # React components
│   │   ├── IdentityIcon.tsx
│   │   ├── MemoryIcon.tsx
│   │   └── ... (8 total)
│   ├── features/
│   │   ├── MatrizIcon.tsx
│   │   ├── MemoryHealixIcon.tsx
│   │   └── ... (15 total)
│   └── index.ts                        # Barrel export
├── sizes/                               # Pre-exported sizes
│   ├── 16px/
│   ├── 20px/
│   ├── 24px/
│   ├── 48px/
│   └── 64px/
└── README.md                            # Usage documentation
```

---

### Usage Documentation

**README.md**:

````markdown
# LUKHAS Icon System

## Installation

```bash
# Copy React components to your project
cp -r react/constellation components/icons/constellation
cp -r react/features components/icons/features
```

## Usage

```typescript
import { IdentityIcon } from '@/components/icons/constellation';
import { MatrizIcon } from '@/components/icons/features';

function MyComponent() {
  return (
    <div>
      {/* Constellation star icon */}
      <IdentityIcon size={24} variant="default" animated />

      {/* Feature icon */}
      <MatrizIcon size={32} color="hsl(200, 60%, 55%)" />
    </div>
  );
}
```

## Color Variants

- `default` - Uses constellation star color
- `success` - Green (hsl(142, 71%, 45%))
- `warning` - Orange (hsl(38, 92%, 50%))
- `error` - Red (hsl(0, 72%, 51%))

## Sizes

Common sizes: 16, 20, 24, 32, 48, 64 (px)

## Accessibility

All icons include:
- `aria-label` for screen readers
- `role="img"` for semantics
- Proper color contrast (WCAG 2.1 AA)
````

---

## Delegation Checklist

### Designer Responsibilities

- [ ] Design 8 Constellation Framework icons (Week 1)
- [ ] Design 15 Platform Feature icons (Week 1)
- [ ] Create color variants (success, warning, error) (Week 2)
- [ ] Test icons at multiple sizes (16-64px) (Week 2)
- [ ] Optimize SVGs with SVGOMG (Week 2)
- [ ] Convert to React components with SVGR (Week 3)
- [ ] Add Framer Motion animations (Week 3)
- [ ] Test accessibility (WCAG AA) (Week 3)
- [ ] Package deliverables (Week 3)

### Developer Responsibilities

- [ ] Review initial designs (Week 1, Day 5)
- [ ] Integrate React components into lukhas-team frontend (Week 3)
- [ ] Test icons in all dashboard pages
- [ ] Verify animations work correctly
- [ ] Run accessibility audit

---

## Budget Estimate

**Designer Time**:
- Week 1 (Initial designs): 40 hours @ $75/hr = $3,000
- Week 2 (Revisions): 30 hours @ $75/hr = $2,250
- Week 3 (Implementation): 20 hours @ $75/hr = $1,500
- **Total**: ~90 hours = **$6,750**

**Alternative**: Hire freelance icon designer on Dribbble/Behance for ~$3,000-5,000 (fixed price).

---

**Document Version**: 1.0
**Last Updated**: 2025-11-10
**Status**: Design Brief Complete, Ready for Delegation
**Next Document**: [MATRIZ_INTEGRATION_ARCHITECTURE.md](MATRIZ_INTEGRATION_ARCHITECTURE.md)
