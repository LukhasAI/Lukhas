# LUKHAS Logo Concepts

> **🎨 Three Bespoke Lambda-Based Logo Designs**

**Version**: 1.0
**Date**: 2025-11-06
**Source**: [Deliverables.md](../../docs/gonzo/Deliverables.md)
**Status**: ✅ Canonical
**Priority**: P1 (Brand Identity)

---

## Overview

Three unique logo concepts for LUKHAS, each embodying the cognitive architecture and constellation framework while maintaining technical precision and accessibility.

**Design Goals**:
- ✅ Unique geometry (not generic lambda)
- ✅ Lambda as **cognitive artifact**
- ✅ Constellation motif integration
- ✅ Scalable from 16px to print
- ✅ Dark-first design (primary)
- ✅ High-contrast assistive variant

---

## Concept 1: Constellation Lambda

**Status**: Recommended for primary brand identity

**Concept**: Lambda built from three connected nodes and arcs, suggesting networked cognitive operations and provenance

**File**: `branding/assets/logos/lambda-constellation-dark.svg`

### Visual Description

The lambda is **implied by arcs & node geometry** rather than drawn as a single glyph. Reads as **network + lambda**, tying traceable cognitive nodes to the brand symbol.

**Elements**:
- 3 nodes (gradient fill) representing Memory-Attention-Thought
- Connecting arcs form lambda shape
- Subtle halo for depth
- 2 orbiting micro-stars for constellation feel
- Gradient: #7A3BFF (purple) → #0EA5A4 (teal)

### SVG Code

```svg
<!-- lambda-constellation-dark.svg: dark-first primary -->
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" width="512" height="512" role="img" aria-label="LUKHAS constellation lambda symbol">
  <defs>
    <linearGradient id="cgrad" x1="0" x2="1" y1="0" y2="1">
      <stop offset="0" stop-color="#7A3BFF"/>
      <stop offset="1" stop-color="#0EA5A4"/>
    </linearGradient>
  </defs>

  <!-- subtle dark radial background -->
  <rect width="100%" height="100%" fill="#0B0F1A" />

  <!-- outer halo (very subtle) -->
  <g opacity="0.08">
    <circle cx="256" cy="220" r="160" fill="url(#cgrad)"/>
  </g>

  <!-- nodes -->
  <g fill="url(#cgrad)" stroke="#E6EEF6" stroke-width="3">
    <circle cx="200" cy="340" r="14"/>
    <circle cx="312" cy="340" r="14"/>
    <circle cx="256" cy="160" r="14"/>
  </g>

  <!-- connecting arcs (stylized lambda) -->
  <g fill="none" stroke="url(#cgrad)" stroke-width="10" stroke-linecap="round" stroke-linejoin="round">
    <path d="M200 340 C230 260, 282 260, 312 340" />
    <path d="M200 340 L256 160 L312 340" />
  </g>

  <!-- small orbiting star accents -->
  <g fill="#7A3BFF" opacity="0.85">
    <circle cx="128" cy="200" r="4"/>
    <circle cx="396" cy="110" r="5" fill="#0EA5A4"/>
  </g>
</svg>
```

### Variants

**Light Variant**:
- Background: `#FFFFFF`
- Stroke: `#0B0F1A`
- Keep gradient colors

**Assistive Variant** (High Contrast):
- Fill nodes and arcs with `#FFFFFF`
- Dark background `#0B0F1A`
- Remove halo (noise reduction)
- Increase node radius: 20px (from 14px)
- Increase stroke width: 16px (from 10px)
- Better hit-target and visibility

### Use Cases
- Primary logo for lukhas.ai
- App icons (512x512, 256x256, 128x128)
- Social media avatars
- Favicon (with simplified version)

---

## Concept 2: Trinity Crystal Lambda

**Concept**: A faceted triangular (trinity) crystal where the **negative space** forms a lambda. Reads as structure, craft, and the Trinity idea (Memory, Attention, Thought).

**File**: `branding/assets/logos/lambda-crystal-dark.svg`

### Visual Description

**Why Unique**: Jewel-like crystal metaphor—structural, crafted. The lambda sits in **negative space**, making it clever and less like typical lambda logos.

**Elements**:
- Outer triangular gem shape
- Internal facets carving lambda in negative space
- Gradient: #0EA5A4 (teal) → #7A3BFF (purple)
- Geometric precision

### SVG Code

```svg
<!-- lambda-crystal-dark.svg -->
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" width="512" height="512" role="img" aria-label="LUKHAS trinity crystal symbol">
  <rect width="100%" height="100%" fill="#0B0F1A"/>
  <defs>
    <linearGradient id="g2" x1="0" x2="1" y1="0" y2="1">
      <stop offset="0" stop-color="#0EA5A4"/>
      <stop offset="1" stop-color="#7A3BFF"/>
    </linearGradient>
  </defs>

  <!-- outer triangular gem -->
  <g transform="translate(56,48)">
    <!-- big triangle -->
    <path d="M200 16 L392 388 L8 388 Z" fill="url(#g2)" stroke="#E6EEF6" stroke-width="4" stroke-linejoin="round"/>
    <!-- internal facets that carve a lambda negative space -->
    <path d="M200 58 L130 330 L200 330 L270 330 Z" fill="#0B1220" opacity="0.12"/>
    <path d="M160 120 L200 58 L240 120 L200 120 Z" fill="#E6EEF6" opacity="0.06"/>
    <!-- negative-space lambda (thin) -->
    <path d="M200 58 L180 188 L220 188 L200 58 Z" fill="#0B0F1A"/>
  </g>
</svg>
```

### Variants

**Light Variant**:
- Background: `#FFFFFF`
- Triangle stroke: `#0B0F1A`
- Adjust gradient slightly darker

**Assistive Variant**:
- Remove subtle opacity layers
- Increase stroke width to 8px
- Add bold white inner lambda on dark background
- Higher contrast

### Use Cases
- Secondary brand mark
- Premium product branding
- Print materials
- High-end presentations

---

## Concept 3: Cognitive Helix Lambda

**Concept**: Lambda integrated with a **double-helix / spiral**, representing sequential thinking and layered memory.

**File**: `branding/assets/logos/lambda-helix-dark.svg`

### Visual Description

**Why Unique**: Helix implies sequential cognitive processing. Gives the brand a biological/DNA metaphor applied to **cognition** (not biology). Use careful wording: "consciousness-inspired, not bio-mimetic."

**Elements**:
- Double helix curves
- Bold lambda strokes crossing helix
- Micro nodes on helix curves
- Gradient: #7A3BFF (purple) → #06B6D4 (cyan)

### SVG Code

```svg
<!-- lambda-helix-dark.svg -->
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" width="512" height="512" role="img" aria-label="LUKHAS helix lambda symbol">
  <rect width="100%" height="100%" fill="#0B0F1A"/>
  <defs>
    <linearGradient id="g3" x1="0" x2="1">
      <stop offset="0" stop-color="#7A3BFF"/>
      <stop offset="1" stop-color="#06B6D4"/>
    </linearGradient>
  </defs>

  <!-- helix -->
  <g fill="none" stroke="url(#g3)" stroke-width="10" stroke-linecap="round">
    <path d="M120 420 C190 240, 322 240, 392 420" />
    <path d="M140 420 C210 260, 302 260, 372 420" stroke-opacity="0.8" />
  </g>

  <!-- lambda formed by two bold strokes crossing the helix -->
  <g>
    <path d="M192 320 L256 120 L320 320" fill="none" stroke="#E6EEF6" stroke-width="14" stroke-linecap="round" stroke-linejoin="round"/>
    <path d="M220 320 L292 320" stroke="#E6EEF6" stroke-width="14" stroke-linecap="round"/>
  </g>

  <!-- micro nodes on helix -->
  <g fill="#7A3BFF">
    <circle cx="160" cy="300" r="6"/>
    <circle cx="360" cy="300" r="6" fill="#06B6D4"/>
  </g>
</svg>
```

### Variants

**Light Variant**:
- Invert colors
- Stroke: `#0B0F1A`
- Adjust gradient

**Assistive Variant**:
- Thicker lambda strokes: 20px (from 14px)
- Larger helix lines: 16px (from 10px)
- White lambda on dark
- Remove subtle opacity

### Use Cases
- Research/academic branding
- Technical documentation headers
- Conference materials
- MATRIZ-specific branding

---

## Wordmark Guidelines

### Typography

**Recommended Font**: Inter (primary) or Source Serif Pro (formal)

**Wordmark Compositions**:
1. **Horizontal**: Symbol left + wordmark right (most common)
2. **Stacked**: Symbol top + wordmark bottom (narrow spaces)
3. **Symbol Only**: For favicons, small sizes (<64px)

### Text Specifications

```css
/* Primary Wordmark */
font-family: 'Inter', sans-serif;
font-weight: 600;
font-size: 48px; /* scale to symbol height */
letter-spacing: -0.02em;
color: #E6EEF6; /* dark theme */
color: #0B0F1A; /* light theme */

/* Tagline (optional) */
font-family: 'Inter', sans-serif;
font-weight: 400;
font-size: 16px;
letter-spacing: 0.01em;
opacity: 0.8;
text: "Conscious by Design" or "Traceable Cognition"
```

### Spacing

- **Minimum Clear Space**: 1x symbol width on all sides
- **Symbol-to-Wordmark Gap**: 0.5x symbol width (horizontal layout)
- **Vertical Stack Gap**: 0.3x symbol height

---

## Production Guidelines

### Export Sizes

**For Web**:
- favicon.ico: 16x16, 32x32, 48x48
- apple-touch-icon: 180x180
- og:image: 1200x630
- App icons: 512x512, 256x256, 192x192, 128x128

**For Print**:
- Vector SVG (preferred)
- PNG at 300dpi: 2000x2000px minimum
- PDF with embedded fonts (if using wordmark)

### File Naming Convention

```
lukhas-logo-[concept]-[variant]-[size].svg

Examples:
lukhas-logo-constellation-dark-512.svg
lukhas-logo-constellation-light-512.svg
lukhas-logo-constellation-assistive-512.svg
lukhas-logo-crystal-dark-1024.svg
lukhas-logo-helix-light-512.svg
```

### Color Specifications

| Color Name | Hex | Usage |
|------------|-----|-------|
| **Primary Purple** | #7A3BFF | Gradients, accents |
| **Primary Teal** | #0EA5A4 | Gradients, identity |
| **Cyan** | #06B6D4 | Helix variant |
| **Dark BG** | #0B0F1A | Dark theme background |
| **Light Text** | #E6EEF6 | Dark theme text/strokes |
| **Light BG** | #FFFFFF | Light theme background |
| **Dark Text** | #0B0F1A | Light theme text/strokes |

---

## Finalization Process

### Phase 1: Selection (W1)
- [ ] Review all 3 concepts with design team
- [ ] User test with 10 external viewers (preference + recall)
- [ ] Select primary concept

### Phase 2: Refinement (W2)
- [ ] Create 3 variations of selected concept (color, minor geometry)
- [ ] Test at multiple sizes (16px to print)
- [ ] Get feedback from stakeholders

### Phase 3: Production (W3)
- [ ] Convert text to paths (if using wordmark)
- [ ] Export all required sizes and formats
- [ ] Create brand guidelines document
- [ ] Validate with `tools/svg_validator.py`

### Phase 4: Deployment (W4)
- [ ] Update all domains (lukhas.ai, lukhas.dev, etc.)
- [ ] Update social media profiles
- [ ] Create press kit with logo assets
- [ ] Document usage guidelines

---

## Design Rationale

### Constellation Lambda (Recommended)

**Strengths**:
- ✅ Unique: Network + lambda hybrid not seen elsewhere
- ✅ Scalable: Clear at 16px, detailed at 512px
- ✅ Cognitive: Nodes = cognitive operations
- ✅ Brand Story: Visual representation of provenance/traceability
- ✅ Accessible: High contrast assistive variant works well

**Considerations**:
- Complexity at very small sizes (16px) - may need simplified favicon
- Gradient requires careful optimization for print

### Trinity Crystal Lambda

**Strengths**:
- ✅ Clever: Negative space lambda is sophisticated
- ✅ Geometric: Precise, crafted, trustworthy
- ✅ Memorable: Crystal metaphor is distinctive

**Considerations**:
- More abstract - may require explanation
- Negative space less clear at small sizes

### Cognitive Helix Lambda

**Strengths**:
- ✅ Sequential: Helix implies processing over time
- ✅ Research-friendly: Academic/scientific feel

**Considerations**:
- Bio-inspired aesthetic may confuse positioning
- Requires careful messaging: "consciousness-inspired, not bio-mimetic"

---

## Related Documents

- **Design Themes**: [LUKHAS_THEMES.md](./LUKHAS_THEMES.md) - Color palette and design tokens
- **Visual Motifs**: [visuals/INTERACTIVE_MOTIFS.md](./visuals/INTERACTIVE_MOTIFS.md) - Animation patterns
- **SVG Validator**: [../../tools/svg_validator.py](../../tools/svg_validator.py) - Quality checks

---

**Document Owner**: @design-lead + @brand-manager
**Review Cycle**: Weekly during selection phase (W1-W4)
**Last Updated**: 2025-11-06
