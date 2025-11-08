## LUKHAS Branding Deliverables Proposal


---

## A — Three bespoke LUKHAS logo concepts (SVGs)

**Design goals:** unique geometry, lambda as a *cognitive artifact*, constellation motif, scalable, dark-first, high-contrast assistive variant. Each concept includes:

* Primary symbol SVG (optimized for dark background)
* Light variant notes (simple invert)
* Assistive-high-contrast variant (white fill on dark stroke or vice versa)

> Save each SVG to `branding/assets/logos/` and review. For wordmarks use the symbol + Inter or Source Serif for headings; convert text to paths before production if necessary.

---

### Concept 1 — **Constellation Lambda**

Lambda built from three connected nodes and arcs — suggests networked cognitive operations and provenance.

**`branding/assets/logos/lambda-constellation-dark.svg`**

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

**Light variant:** invert background to white, stroke to `#0B0F1A`, keep gradient.
**Assistive variant:** fill nodes and arcs with `#FFFFFF` on dark bg and remove halo; increase node radius to 20px and stroke to 6px to improve hit-target/visibility.

**Why this is unique:** The lambda is implied by arcs & node geometry rather than drawn as a single glyph — it reads as **network + lambda** which ties the idea of traceable cognitive nodes to the brand symbol.

---

### Concept 2 — **Trinity Crystal Lambda**

A faceted triangular (trinity) crystal where the negative space forms a lambda. This reads as structure, craft, and the Trinity idea (Memory, Attention, Thought).

**`branding/assets/logos/lambda-crystal-dark.svg`**

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

**Light variant:** background white, triangle stroke `#0B0F1A`, gradient adjusted slightly darker.
**Assistive variant:** remove subtle opacity layers, increase stroke width and contrast; add bold white inner lambda on dark bg.

**Why unique:** jewel-like crystal metaphor — structural, crafted, and the trinity idea rendered visually; lambda sits in *negative space*, making the mark clever and less like typical lambda logos.

---

### Concept 3 — **Cognitive Helix Lambda**

Lambda integrated with a double-helix / spiral, representing sequential thinking and layered memory.

**`branding/assets/logos/lambda-helix-dark.svg`**

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

**Light variant:** invert colors, stroke `#0B0F1A`, gradient tweaked.
**Assistive variant:** thicker lambda strokes, larger helix lines, white lambda on dark.

**Why unique:** helix implies sequential cognitive processing and gives the brand a biological / DNA metaphor but applied to *cognition*, not biology — careful wording must be used (consciousness-inspired).

---

### How to use & finalize logos

* For **wordmark**, pair any of the symbols with a clean Inter-based wordmark. Use the symbol left + wordmark right for horizontal; stacked for narrow spaces.
* For final production, convert any text to paths (SVG) to avoid font licensing or fallback issues, and export required sizes.
* I recommend selecting one concept then iterate 3 directions (color & minor shape) with a designer. I can produce three variants per concept if you want.

---

## B — Six SEO pillar articles + starter visuals (SVG + Markdown)

I created six pillar topics that map to LUKHAS strengths and buyer/researcher intents. For each: title, slug, meta description, H1 and subheadings, keywords, short intro paragraph, and a starter SVG (simple icon-like visual) that you can use as a hero or section thumbnail.

Save the MD files to `branding/content/pillars/` and SVGs to `branding/assets/visuals/pillars/`.

---

### 1) Pillar — *Explainable Reasoning: What is a Reasoning Graph?*

**Slug:** `explainable-reasoning-what-is-a-reasoning-graph`
**Meta description:** `What is a reasoning graph? Learn how LUKHAS MΛTRIZ builds traceable decision chains, why they matter for explainability, and how auditors verify them.`
**Keywords:** reasoning graph, explainable AI, MATRIZ, provenance
**H1:** What is a Reasoning Graph? How Explainable AI Works in MΛTRIZ

**Outline**

* H2: Executive summary — 3 bullet benefits
* H2: Anatomy of a reasoning graph — nodes, edges, provenance
* H2: From Memory to Awareness — the six MΛTRIZ stages
* H2: How this enables auditability & the “Why?” affordance
* H2: Example trace (illustrated) + evidence page link
* H2: Implications for enterprise & regulators

**Intro paragraph (sample)**

```md
Reasoning graphs are the backbone of explainable AI — they let systems not just produce answers, but also show why those answers were reached. LUKHAS MΛTRIZ models thinking as a sequence of traceable operations: Memory, Attention, Thought, Action, Decision and Awareness. This article unpacks the structure of a reasoning graph, how it supports auditability, and what enterprises should ask for when evaluating transparent AI.
```

**Starter visual SVG — reasoning-graph (`branding/assets/visuals/pillars/reasoning-graph.svg`)**

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 120" width="400" height="240">
  <rect width="100%" height="100%" fill="none"/>
  <circle cx="40" cy="60" r="12" fill="#7A3BFF"/><text x="40" y="60" font-size="7" fill="#fff" text-anchor="middle" dominant-baseline="central">M</text>
  <circle cx="100" cy="28" r="12" fill="#0EA5A4"/><text x="100" y="28" font-size="7" fill="#fff" text-anchor="middle" dominant-baseline="central">A</text>
  <circle cx="100" cy="92" r="12" fill="#7A3BFF"/><text x="100" y="92" font-size="7" fill="#fff" text-anchor="middle" dominant-baseline="central">T</text>
  <circle cx="160" cy="60" r="12" fill="#06B6D4"/><text x="160" y="60" font-size="7" fill="#fff" text-anchor="middle" dominant-baseline="central">D</text>
  <path d="M52 52 Q76 44 92 32" stroke="#E6EEF6" stroke-width="2" fill="none" stroke-linecap="round"/>
  <path d="M92 98 Q106 84 148 68" stroke="#E6EEF6" stroke-width="2" fill="none" stroke-linecap="round"/>
</svg>
```

---

### 2) Pillar — *MΛTRIZ: Architecting Traceable Cognition*

**Slug:** `matriz-architecting-traceable-cognition`
**Meta:** `MΛTRIZ is LUKHAS' cognitive architecture. Learn its core stages, design principles and why traceability is engineered in.`
**Keywords:** Matriz architecture, traceability, cognitive architecture
**H1:** MΛTRIZ — The Architecture of Traceable Cognition

**Outline**

* Summary of Trinity/6 stages
* Design principles: modularity, provenance, governance
* Data flows & privacy (how memory folds work)
* Performance considerations & scaling
* Research & reproducibility

**Starter visual SVG — `matriz-architecture.svg`**
Simple stacked blocks with arrows and labels Memory/Attention/Thought/Action/Decision/Awareness.

---

### 3) Pillar — *Guardian: Ethics, Policies and Constitutional AI*

**Slug:** `guardian-ethics-policies-constitutional-ai`
**Meta:** `The LUKHAS Guardian ensures policies, fairness and constitutional compliance. Read how Guardian works and how it prevents drift.`
**Keywords:** Guardian, constitutional AI, safety, bias mitigation
**H1:** Guardian — Policy, Safety and Constitutional AI at LUKHAS

**Outline**

* Guardian overview & core principles
* Policy enforcement model & runtime check
* Constitutional alignment & audit trails
* Case study: Guardian in action
* How enterprises integrate Guardian

**Starter visual SVG — `guardian-shield.svg`** (use earlier icon scaled up)

---

### 4) Pillar — *Reasoning Lab: Hands-on Explainability*

**Slug:** `reasoning-lab-hands-on-explainability`
**Meta:** `Try the Reasoning Lab: an interactive environment to explore MΛTRIZ traces. Learn modes, redaction, and how auditors validate results.`
**Keywords:** Reasoning Lab, interactive demo, explainability demo
**H1:** Reasoning Lab — Hands-on Explainability for MΛTRIZ

**Outline**

* How to use the Lab (public/dev/enterprise)
* Redaction and privacy controls explained
* Walkthrough: reading a trace
* Export & auditing features
* Tutorials and reproducible demo links

**Starter visual:** small graph + side panel (use node SVG earlier).

---

### 5) Pillar — *Enterprise Trust: Audits, Evidence & Onboarding*

**Slug:** `enterprise-trust-audits-evidence-onboarding`
**Meta:** `Enterprise trust is the foundation for deploying explainable AI. Read about audit packs, SLAs and onboarding for regulated industries.`
**Keywords:** audit pack, enterprise onboarding, DPA
**H1:** Enterprise Trust — Audits, Evidence and Getting Onboard with LUKHAS

**Outline**

* Audit pack anatomy & SLAs
* Compliance (GDPR, EU AI Act mapping)
* Onboarding checklist & timelines
* Sandbox & reproducible demos for procurement
* Pricing & support tiers (high level)

**Starter visual:** shield + document icon.

---

### 6) Pillar — *Developer Playbook: Quickstarts, SDKs and Patterns*

**Slug:** `developer-playbook-quickstarts-sdk-patterns`
**Meta:** `Everything developers need: quickstarts, SDK docs, production patterns and testing strategies for MΛTRIZ.`
**Keywords:** MΛTRIZ SDK, quickstart, production patterns
**H1:** Developer Playbook — Quickstarts, SDKs and Production Patterns

**Outline**

* 5-minute quickstart (Python/Node)
* SDK reference & design patterns (auth, observability)
* Testing & CI patterns for reasoning graphs
* Production patterns and scalability tips
* Community & open-source integrations

**Starter visual:** dev brackets icon + quickstart bullets.

---

**How I’ll deliver these:**

* I’ll create `branding/content/pillars/<slug>.md` for each, with proper front-matter and `evidence_links` placeholder.
* Also create `branding/assets/visuals/pillars/*.svg` with the starter visuals above.
* If you want, I’ll generate the full 6 Markdown files now (each ~800–1200 words with subheaders and a short SEO intro). Say “Generate full pillar content” and I’ll produce each file in full.

---

## C — SVG auto-validator script (contrast, sizing, stroke width)

This script reads your design tokens (e.g., `branding/tokens/lukhas-tokens.json`) and validates an SVG file against constraints:

* **Checks**

  * `viewBox` present and parseable
  * Minimum recommended width/height from viewBox (>= 24 px at 24x scale)
  * No embedded raster `<image>` tags
  * Stroke widths present and within recommended range (0.6px - 4px scaled to 24px grid)
  * Contrast: for icons with fill/stroke color, compute contrast ratio against theme background color (dark/light/assistive); must meet threshold (≥4.5:1 for strokes/fills)
  * Color usage: if color hex used, check against token palette (warn if not using a palette color)
* **Outputs**: pass/fail, and a JSON report with details.

Save as `tools/svg_validator.py`.

```python
#!/usr/bin/env python3
"""
tools/svg_validator.py

Usage:
  python3 tools/svg_validator.py --svg path/to/icon.svg --tokens branding/tokens/lukhas-tokens.json --theme dark

Checks:
- viewBox presence
- min dimension recommended (>=24)
- no <image> raster tags
- stroke-width values reasonable for 24px grid
- contrast ratio for fills/strokes against background per theme tokens
- color usage check against tokens (warn)
"""

import argparse, json, re, sys
from xml.etree import ElementTree as ET
from pathlib import Path
import math

def hex_to_rgb(hexc):
    hexc = hexc.strip()
    if hexc.startswith('#'): hexc = hexc[1:]
    if len(hexc) == 3:
        hexc = ''.join([c*2 for c in hexc])
    r = int(hexc[0:2],16)/255.0
    g = int(hexc[2:4],16)/255.0
    b = int(hexc[4:6],16)/255.0
    return (r,g,b)

def lum(r,g,b):
    # relative luminance per WCAG
    def channel(c):
        if c <= 0.03928:
            return c/12.92
        return ((c + 0.055)/1.055)**2.4
    return 0.2126*channel(r) + 0.7152*channel(g) + 0.0722*channel(b)

def contrast_ratio(hex1, hex2):
    r1,g1,b1 = hex_to_rgb(hex1)
    r2,g2,b2 = hex_to_rgb(hex2)
    L1 = lum(r1,g1,b1)
    L2 = lum(r2,g2,b2)
    if L1 < L2:
        L1, L2 = L2, L1
    return (L1 + 0.05) / (L2 + 0.05)

def get_theme_bg(tokens, theme):
    theme_data = tokens.get('theme', {}).get(theme)
    if not theme_data:
        raise ValueError(f"Theme {theme} not found in tokens.")
    return theme_data.get('bg')

def parse_svg(svg_path):
    tree = ET.parse(svg_path)
    root = tree.getroot()
    return root

def find_elements(root, tag):
    ns = {'svg': 'http://www.w3.org/2000/svg'}
    return root.findall('.//{%s}%s' % (ns['svg'], tag))

def attr(elem, name, default=None):
    return elem.get(name) if elem.get(name) is not None else default

def hex_from_style(style_str, prop):
    # style string like "fill:#fff;stroke:#000"
    if not style_str:
        return None
    parts = style_str.split(';')
    for p in parts:
        if ':' in p:
            k,v = p.split(':',1)
            if k.strip()==prop:
                return v.strip()
    return None

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--svg', required=True)
    p.add_argument('--tokens', required=True)
    p.add_argument('--theme', choices=['dark','light','assistive'], default='dark')
    p.add_argument('--minsize', type=int, default=24, help='min recommended icon dimension')
    p.add_argument('--stroke-min', type=float, default=0.6, help='min stroke width for 24px grid')
    p.add_argument('--stroke-max', type=float, default=4.0, help='max stroke width for 24px grid')
    args = p.parse_args()

    svg_path = Path(args.svg)
    tokens = json.loads(Path(args.tokens).read_text(encoding='utf-8'))
    bg = get_theme_bg(tokens, args.theme)
    root = parse_svg(svg_path)

    issues = []
    # viewBox
    vb = root.get('viewBox')
    width = root.get('width')
    height = root.get('height')
    if not vb:
        issues.append("Missing viewBox attribute.")
    else:
        parts = list(map(float, vb.strip().split()))
        vw = parts[2]; vh = parts[3]
        if vw < args.minsize or vh < args.minsize:
            issues.append(f"viewBox dimensions {vw}x{vh} < min recommended {args.minsize}px.")

    # raster <image>
    images = root.findall('.//{http://www.w3.org/2000/svg}image')
    if images:
        issues.append("SVG contains raster <image> elements; avoid embedding raster.")

    # strokes & fills
    # examine common shape tags
    shape_tags = ['path','circle','rect','ellipse','line','polyline','polygon']
    ns = {'svg':'http://www.w3.org/2000/svg'}
    for tag in shape_tags:
        for el in root.findall('.//{%s}%s' % (ns['svg'], tag)):
            # check stroke-width
            sw = el.get('stroke-width')
            style = el.get('style')
            if sw is None and style:
                sw = hex_from_style(style, 'stroke-width')
            if sw is not None:
                try:
                    swv = float(sw)
                    if swv < args.stroke_min or swv > args.stroke_max:
                        issues.append(f"Element <{tag}> stroke-width={swv} outside recommended [{args.stroke_min},{args.stroke_max}].")
                except:
                    # stroke width might be like '2px' => strip
                    m = re.match(r'([\d.]+)', str(sw))
                    if m:
                        swv = float(m.group(1))
                        if swv < args.stroke_min or swv > args.stroke_max:
                            issues.append(f"Element <{tag}> stroke-width={swv} outside recommended.")
            # check fill/stroke color contrast
            fill = el.get('fill')
            stroke = el.get('stroke')
            # check style attr too
            if style:
                if not fill:
                    fill = hex_from_style(style, 'fill')
                if not stroke:
                    stroke = hex_from_style(style, 'stroke')
            # evaluate contrast for fill and stroke if present and not 'none'
            for ctype, col in [('fill', fill), ('stroke', stroke)]:
                if col and col.lower() not in ('none', 'currentColor'):
                    # normalize hex or rgb
                    hexcol = None
                    if col.startswith('#'):
                        hexcol = col
                    else:
                        # try rgb(r,g,b)
                        m = re.match(r'rgb\((\d+),\s*(\d+),\s*(\d+)\)', col)
                        if m:
                            r,g,b = map(int, m.groups())
                            hexcol = '#%02x%02x%02x' % (r,g,b)
                    if hexcol:
                        try:
                            cr = contrast_ratio(hexcol, bg)
                            if cr < 4.5:
                                issues.append(f"{tag} {ctype} color {hexcol} has contrast {cr:.2f} vs background {bg} < 4.5.")
                        except Exception as e:
                            issues.append(f"Color contrast check error for {hexcol}: {e}")

    # color token usage: if any fill colors present, warn if not in token palette
    palette = []
    th = tokens.get('theme', {}).get(args.theme) or {}
    for k,v in th.items():
        if k in ('bg','surface','matriz','identity','dev','enterprise','success','warning','danger','text'):
            palette.append(v)
    # collect fills
    fills = set()
    for el in root.findall('.//{%s}*' % ns['svg']):
        f = el.get('fill')
        style = el.get('style')
        if style and not f:
            f = hex_from_style(style, 'fill')
        if f and f.lower() not in ('none','currentcolor'):
            if f.startswith('#'):
                fills.add(f.upper())

    for f in fills:
        if f not in [c.upper() for c in palette]:
            issues.append(f"Fill color {f} not found in theme palette for {args.theme} (warn).")

    # Final result
    if issues:
        print("SVG Validation Issues:")
        for i in issues:
            print(" -", i)
        sys.exit(2)
    else:
        print("SVG Validation passed.")
        sys.exit(0)

if __name__ == "__main__":
    main()
```

**How to run**

```bash
python3 tools/svg_validator.py --svg branding/assets/logos/lambda-constellation-dark.svg --tokens branding/tokens/lukhas-tokens.json --theme dark
```

**Notes**

* The contrast checker expects hex colors; if you use `currentColor` or CSS variables in SVG, expand them before validation (or pass the rendered SVG with CSS inlined).
* You can extend the script to check stroke width scaled to viewBox size (normalize for icons with different viewBoxes).

---
This proposal outlines the deliverables for LUKHAS branding, including three unique logo concepts, six SEO pillar articles with starter visuals, and an SVG auto-validator script to ensure design consistency and accessibility. Each logo concept is designed to reflect LUKHAS' core values and cognitive architecture, while the pillar articles aim to establish thought leadership in explainable AI and enterprise trust. The SVG validator script will help maintain quality across all visual assets by checking for key design parameters.