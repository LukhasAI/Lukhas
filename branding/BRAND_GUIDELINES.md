# LUKHAS Brand Guidelines

> **📌 CANONICAL SOURCE OF TRUTH**
> *LUKHAS — Where consciousness meets craft.*
> This document is the **single authoritative source** for how LUKHAS looks, speaks, and publishes across the λWecosystem. Use it. Enforce it.

**Document Status**: ✅ Canonical
**Version**: 2.0
**Last Updated**: 2025-11-06
**Supersedes**: All previous branding documentation
**Location**: `branding/BRAND_GUIDELINES.md`

---

## 🔗 Multi-Domain Branding System

This guideline works in conjunction with the **LUKHAS Multi-Domain Branding System**:

- **Domain-Specific Brand Guides**: See [`branding/domains/`](domains/) for detailed guides for each domain:
  - [lukhas.ai](domains/lukhas.ai/BRAND_GUIDE.md) - Flagship platform
  - [lukhas.id](domains/lukhas.id/BRAND_GUIDE.md) - Identity portal
  - [lukhas.dev](domains/lukhas.dev/BRAND_GUIDE.md) - Developer platform
  - [lukhas.team](domains/lukhas.team/BRAND_GUIDE.md) - Collaboration hub
  - [lukhas.store](domains/lukhas.store/BRAND_GUIDE.md) - Marketplace
  - [lukhas.io](domains/lukhas.io/BRAND_GUIDE.md) - Infrastructure
  - [lukhas.cloud](domains/lukhas.cloud/BRAND_GUIDE.md) - Cloud services
  - [lukhas.com](domains/lukhas.com/BRAND_GUIDE.md) - Corporate hub
  - [lukhas.eu](domains/lukhas.eu/BRAND_GUIDE.md) / [lukhas.us](domains/lukhas.us/BRAND_GUIDE.md) - Compliance
  - [lukhas.xyz](domains/lukhas.xyz/BRAND_GUIDE.md) - Experimental

- **Domain Registry**: [`config/domain_registry.yaml`](config/domain_registry.yaml) - Central configuration
- **Color System**: [`design/colors/MASTER_PALETTE.yaml`](design/colors/MASTER_PALETTE.yaml) - Complete color specifications
- **Interactive Motifs**: [`design/visuals/INTERACTIVE_MOTIFS.md`](design/visuals/INTERACTIVE_MOTIFS.md) - Visual language
- **Theme System**: [`design/LUKHAS_THEMES.md`](design/LUKHAS_THEMES.md) - Dark/Light/Assistive modes
- **Tone Configurations**: [`tone/configs/`](tone/configs/) - Domain-specific tone rules
- **SSO Integration**: [`integration/SSO_CROSS_DOMAIN_GUIDE.md`](integration/SSO_CROSS_DOMAIN_GUIDE.md) - Authentication flows

**This document provides the foundation**; domain-specific guides extend and adapt these principles.

---

## Table of contents

1. Visual identity  
   1.1 Logo system & usage  
   1.2 Color palette & tokens  
   1.3 Typography system  
   1.4 Iconography & illustration language  
   1.5 UI components & layout system  
   1.6 Motion & particle system guidance  
   1.7 Do / Don’t visual examples  
2. Voice & tone  
   2.1 Tone ratios by domain  
   2.2 Vocabulary: preferred & forbidden terms  
   2.3 Microcopy rules & examples  
   2.4 Naming conventions (Λ usage)  
3. Content patterns & templates (rules + front-matter)  
4. Accessibility, legal & privacy micro-rules  
5. Cross-team workflow & governance  
   5.1 Repo layout and assets  
   5.2 Review & approval gates (claims / evidence)  
   5.3 CI enforcement & sample checks  
6. MATRIZ adoption & UX principles  
7. Appendix: design tokens, CSS variables, sample front-matter

---

## 1. Visual identity

### 1.1 Logo system & usage

**Core elements**
- **Primary wordmark:** `LUKHΛS` (capital LUKHAS with Greek-like lambda `Λ` as the lambda glyph). Use the official wordmark for headers and large branding placements.
- **Symbol / mark:** `Λ` (the lambda glyph or a stylized constellation glyph). Use as favicon, app icon, button badges.
- **Lockups:** wordmark + symbol; horizontal and stacked versions are provided.
- **Inverted/monochrome:** for dark backgrounds or single-color contexts.

**Clear space & minimum size**
- Minimum clear space: 1x the height of the `Λ` glyph on all sides (where `x` = height of Λ in final rendering). This ensures clarity near other visual elements.
- Minimum display sizes:  
  - Wordmark (horizontal): 34 px height (web) / 10 mm print  
  - Symbol: 16 px (favicon), 24 px minimum when used in UI

**Usage rules**
- Always use vector formats (SVG/AI) for logos; export PNG only when raster required.
- Use the **display** form `LUKHΛS` in hero/headline contexts and `Lukhas` (sentence case) for body text where needed. Use `LUKHAS AI` for product name references (caps for brand product). See vocabulary rules below.
- NEVER manipulate letter spacing, stretch, skew or rotate the wordmark.
- NEVER replace `Λ` with the ASCII caret or any other glyph.
- **Monochrome / reversed**: when on dark backgrounds use inverted white mark; for single-color prints use black or brand neutral.

**Bad usages (DON’Ts)**
- Do not place the logo on cluttered backgrounds. If the background is complex, use a solid or gradient safe area behind logo (8–12% opacity overlay).
- Do not apply drop shadows, inner shadows or blend modes to the official logo.
- Do not translate, abbreviate, or redesign the `Λ` glyph.

---

### 1.2 Color palette & tokens

We use a single system of tokens so code/design share exactly the same values.

**Primary palette**
- `--lukhas-primary-1: #0B0F1A` (Deep Night — primary background)  
- `--lukhas-accent-matriz: #7A3BFF` (MΛTRIZ accent — vivid purple)  
- `--lukhas-accent-identity: #0EA5A4` (ΛiD teal)  
- `--lukhas-accent-dev: #06B6D4` (developer cyan)  
- `--lukhas-accent-enterprise: #1E3A8A` (enterprise blue)

**Support / semantic**
- `--lukhas-success: #10B981`  
- `--lukhas-warning: #F59E0B`  
- `--lukhas-danger: #EF4444`  
- `--lukhas-surface: #ffffff`  
- `--lukhas-muted: #6B7280` (text-muted)

**Grayscale scale**
- `--lukhas-gray-900: #0B0F1A`  
- `--lukhas-gray-700: #374151`  
- `--lukhas-gray-500: #6B7280`  
- `--lukhas-gray-300: #D1D5DB`  
- `--lukhas-gray-100: #F3F4F6`

**Token file (example JSON)** — see Appendix.

**Accessibility requirement**
- Ensure contrast ratio >= 4.5:1 for body text, >= 3:1 for large text (18pt+ or 14pt bold). Provide alternate color combinations if the primary accent fails contrast.

**Usage guidance**
- Accent colors used sparingly — hero accents, CTAs, key highlights. Backgrounds should primarily be `--lukhas-surface` or `--lukhas-primary-1` depending on theme (dark/light).
- Domain-highlight: each domain has a recommended accent color (e.g., `lukhas.dev` cyan). Use that color as a subtle accent in domain’s hero and CTA. Do not change core primary colors.

---

### 1.3 Typography system

**Fonts (recommended)**
- **UI / body:** Inter (variable) — for on-screen body and UI. Inter is modern, highly legible, variable weights.  
- **Display / headings (optional):** Source Serif 4 or IBM Plex Serif — for poetic headings in marketing contexts. Keep headings friendly to accessibility.  
- **Monospace (code):** Fira Code or JetBrains Mono — for code blocks, CLI, and dev console.

**Scale (CSS-ready)**
- `--font-size-xs: 12px`  
- `--font-size-sm: 14px`  
- `--font-size-base: 16px`  
- `--font-size-lg: 20px`  
- `--font-size-xl: 28px`  
- `--font-size-2xl: 36px`  
- `--font-size-3xl: 48px`  
- Line-height: 1.4–1.6 for body; 1.1–1.25 for headings.

**Weights**
- Light 300, Regular 400, Medium 500, Semibold 600, Bold 700

**Accessibility**
- Use font-size > 16px for body on desktop by default; respect user scaling. Ensure 4.5:1 contrast ratio for body text.

**Usage**
- Marketing heroes: Display font (serif) at large scale with Inter fallback.  
- Documentation & UI: Inter at base scale.  
- Code & CLI: Fira Code with syntax highlighting consistent with site theme.

---

### 1.4 Iconography & illustration language

**Icon rules**
- Line-based icons: 2 px stroke at 24 px grid, rounded caps.  
- Use one consistent style: either filled or stroke. Avoid mixing within a single UI context.  
- Icons should be built on a 24 x 24 grid, multiples allowed.

**Illustrations**
- Use geometric constellations, particle metaphors and small abstract neural/constellation diagrams. Illustrations should be simplified and use brand palette accents.

**Do**
- Use icons for affordances only (not to convey full meaning). Always pair with text labels.

---

### 1.5 UI components & layout system

**Design tokens** (see Appendix). Use CSS variables for tokens.

**Grid & spacing**
- 12-column grid for desktop, 8-column for tablet, single column for mobile.  
- Base spacing unit: 8px. Multiples used for padding/margin (8, 16, 24, 32, 48).

**Core components**
- **Hero:** full-width, optional particle canvas, headline, subhead, 2 CTAs.  
- **Performance banner:** structured metric tiles with numeric typography and small caption.  
- **Evidence block:** collapsible list of evidence items with nested links and approvals.  
- **Case study card:** problem, metric, quote, CTA.  
- **CTA:** Primary (filled accent), Secondary (outline), Tertiary (plain). Primary CTA uses the domain accent.

**Buttons**
- Corner radius: 8px (pill buttons only for small CTAs).  
- Elevation: simple 1px shadow for emphasized buttons on light backgrounds. Avoid heavy blur.

---

### 1.6 Motion & particle system guidance

**Principles**
- Motion is optional: it should enhance understanding and not distract.  
- For heavy effects (particles, WebGL), provide lightweight CSS fallback and an option to disable motion (prefers-reduced-motion).  
- Maintain 60fps target for interactions; limit particle count on mobile.

**Accessibility**
- Provide “Reduce motion” toggle in settings. Respect `prefers-reduced-motion` CSS media query.

---

### 1.7 Do / Don’t visual examples

**DO**
- Place logo on plain background or a low-contrast overlay.  
- Provide 24 px padding clear space.  
- Use domain accent on key CTAs.

**DON’T**
- Don’t place logo over a busy image without a solid overlay.  
- Don’t rotate, recolor outside palette, or compress logo proportions.  
- Don’t use low-contrast text on backgrounds.

---

## 2. Voice & tone

### 2.1 Tone ratios by domain

(Use these as target guides for every page. Tweak minorly per page.)

- **lukhas.ai** — Poetic 40% / User-friendly 40% / Academic 20% (inspire + explain)  
- **lukhas.dev** — Poetic 15% / User-friendly 25% / Academic 60% (direct & technical)  
- **lukhas.id** — Poetic 10% / User-friendly 40% / Academic 50% (precise & trustworthy)  
- **lukhas.team** — Poetic 15% / User-friendly 50% / Academic 35% (collaborative & clear)  
- **lukhas.com** — Poetic 20% / User-friendly 50% / Academic 30% (executive & credible)  
- **lukhas.store** — Poetic 30% / User-friendly 50% / Academic 20% (product-friendly)  
- **lukhas.cloud / .io** — Poetic 10% / User-friendly 45% / Academic 45% (infrastructure clarity)  
- **lukhas.eu / .us** — Poetic 5% / User-friendly 45% / Academic 50% (regulatory & factual)  
- **lukhas.xyz** — Poetic 35% / User-friendly 25% / Academic 40% (experimental)

### 2.2 Vocabulary: preferred & forbidden phrases

**Preferred**
- `LUKHAS AI` (brand product)  
- `MΛTRIZ` (display), `Matriz` (plain text)  
- `ΛiD` (display for identity)  
- `consciousness-inspired reasoning` (instead of “true consciousness”)  
- `reasoning graph`, `cognitive DNA`, `Guardian`, `Constellation Framework`

**Forbidden / blocked**
- `true consciousness`, `sentient AI`, `sentience`, `revolutionary` (as a raw claim), `perfect`, `production-ready` (unless signed-off). See also `CONTENT_MANAGEMENT_GUIDE.md` rules.  [oai_citation:0‡VOCABULARY_STANDARDS_QUICK_REFERENCE.md](https://github.com/LukhasAI/Lukhas/blob/ff68c52e48560991463eda090837b3d3da7a7781/docs/web/content/shared/vocabulary-usage/VOCABULARY_STANDARDS_QUICK_REFERENCE.md)

**Symbols**
- Use constellation emoji/symbols only in poetic layer and sparingly (≤1 per 200 words). See `CONTENT_MANAGEMENT_GUIDE.md` for exact rules.  [oai_citation:1‡VOCABULARY_STANDARDS_QUICK_REFERENCE.md](https://github.com/LukhasAI/Lukhas/blob/ff68c52e48560991463eda090837b3d3da7a7781/docs/web/content/shared/vocabulary-usage/VOCABULARY_STANDARDS_QUICK_REFERENCE.md)

---

### 2.3 Sentence style & microcopy rules

**Sentence length**
- Marketing: moderate sentences (12–22 words). Keep poetic hooks short (≤40 words).  
- Docs: concise and imperative where applicable.

**Voice features**
- Use active voice. Favor clarity over cleverness except in the hero or Poetic layer.  
- Use double-line breaks between major sections in Markdown for readability.  
- CTAs: use verbs (`Try MATRIZ`, `Start a trial`, `Request audit`).

**Error / empty state copy**
- Be human, specific, and offer next steps. Example: “No results yet — try broadening your query, or visit the Reasoning Lab for examples.”

---

### 2.4 Naming conventions (Λ usage)

**Display rules**
- `Λ` is reserved for display contexts: hero, product names, logos. Use `ΛiD` for the identity product display name.  
- Plain text within paragraphs: use `Matriz` or `Lukhas` (sentence case) for readability and accessibility.

**Product naming**
- LUKHAS Core (capital), LUKHAS AI (product), MΛTRIZ (display), Matriz (plain text), Λpp / Λpp’s for marketplace items.

**Do**
- Use `ΛiD` in titles & headers (visual). In body copy, `ΛiD` is acceptable if it's a product name but for accessibility provide `Lambda-i-d` or `LUKHAS iD` as ARIA label.

---

## 3. Content patterns & templates

### 3.1 Reusable blocks

- **Hero block**: Title, subtitle, 2 CTAs, 1–3 visual elements (particle canvas optional), trust badges.  
- **Feature grid**: short headline (5–7 words), 1-line description, small visual/icon.  
- **Evidence block** (MANDATORY where claims exist): claim → proof snippet → link to artifact → approval badge.  
- **Case study**: Problem → MATRIZ Approach → Metrics → Evidence → Quote → CTA.

### 3.2 Front-matter schema (REQUIRED)

All content pages **must** include the following YAML front-matter (CI-enforced):

```yaml
---
title: "..."
domain: "lukhas.ai" # or lukhas.dev etc.
owner: "@handle"
audience: "general|developers|enterprise|regulators"
tone:
  poetic: 0.40
  user_friendly: 0.40
  academic: 0.20
canonical: true | false
source: "branding/shared/..."
evidence_links:
  - url: "release_artifacts/..."
claims_verified_by: ["@web-architect"]
claims_verified_date: "2025-11-05"  # or null
claims_approval: false  # must be true for numeric claims
seo:
  title: "..."
  description: "..."
  keywords:
    - "explainable AI"
    - "Matriz"
hreflang: ["en-US", "en-GB"]
last_reviewed: "YYYY-MM-DD"
tags: ["product", "matriz"]
---
```

**Rules**
- Any page with `p95`, `%`, `production-ready`, or numeric operational claims must have `claims_approval: true` and at least one `evidence_link` pointing to a valid artifact. CI will block PRs violating this.

---

### 3.3 Templates (summary)
I’ll produce full markdown templates in the next step (B). For now, enforce that every template includes:
- front-matter
- evidence block placeholder
- contact/owner field
- suggested image/thumbnail alt-text

---

## 4. Accessibility, legal & privacy micro-rules

**Accessibility**
- Must conform to WCAG 2.1 AA. Key checks: color contrast, keyboard navigation, logical heading order, alt text for images, semantic HTML, `aria` attributes on complex components, and `prefers-reduced-motion` support.
- Provide text alternatives for particle / WebGL visuals. A short paragraph describing what the visual demonstrates must always be present.

**Privacy & legal**
- For pages that mention customers or production metrics, link to a consented case-study artifact. Do not publish raw PII. All customer quotes must have written consent and legal approval.
- `lukhas.eu` and `lukhas.us` must contain localized legal packs (DPA, data residency, contact for DPO or privacy officer).

---

## 5. Cross-team workflow & governance

### 5.1 Repo layout & assets (recommended)
```
/branding/
  /assets/
    logo.svg
    favicon.svg
    mascots/
  /tokens/
    design-tokens.json
  /components/
    hero.md
    performance-banner.md
  BRAND_GUIDELINES.md
  /templates/
    homepage.md
    case-study.md
/branding/websites/<domain>/
  /images/
  homepage.md
  architecture.md
/docs/
  /web/
    content...
/release_artifacts/
  evidence_registry.md
```

### 5.2 Review & approval gates

**Roles**
- `content-author` — writes & opens PR  
- `content-reviewer` — editorial reviewer for tone & clarity  
- `web-architect` — technical, performance & architecture reviewer  
- `legal` — claim/contract compliance  
- `brand-owner` — approves visual & tone compliance

**PR template (must include)**
- link to evidence for claims  
- `front-matter` check passed  
- `a11y` test shown  
- `vocab-lint` results  
- assigned reviewers

**CODEOWNERS**: map directories to owners (e.g., `branding/websites/lukhas.ai/ @content-lead @brand-owner`).

---

### 5.3 CI enforcement (recommended checks)
- `content/front-matter-lint` — ensures required fields exist  
- `content/vocab-lint` — blocks forbidden terms (`true consciousness`, `production-ready` without approval)  
- `content/evidence-check` — verifies any numeric claim is listed in `release_artifacts/claims_registry.md`  
- `content/a11y` — axe-core report must show no critical violations  
- `content/link-check` — no broken links

I will provide a sample GitHub Actions YAML in step C.

---

## 6. MATRIZ adoption & UX principles

**Communicating MATRIZ**
- Always present MATRIZ as a *cognitive architecture*, not mystical intelligence. Use metaphors (cognitive DNA), but pair each metaphor with a concrete explanation (stages: Memory, Attention, Thought, Action, Decision, Awareness).
- Any interactive demo of MATRIZ must show: input → reasoning graph → nodes with brief labels → evidence links for any output claim.

**UX**
- **Progressive disclosure**: show a high-level result first; allow users to drill down into reasoning graphs and the provenance of each node.  
- **Traceability**: every decision / output should have a “Why?” affordance linking to the reasoning path and data sources.  
- **Modes**: public / dev / enterprise modes for the Reasoning Lab — each has different data exposure and controls.

---

## 7. Appendix & assets

### 7.1 Design tokens (sample)
```json
{
  "color": {
    "primary": "#0B0F1A",
    "matriz": "#7A3BFF",
    "identity": "#0EA5A4",
    "dev": "#06B6D4",
    "enterprise": "#1E3A8A",
    "success": "#10B981",
    "danger": "#EF4444"
  },
  "space": {
    "xs": "4px",
    "sm": "8px",
    "md": "16px",
    "lg": "24px",
    "xl": "32px"
  },
  "font": {
    "body": "Inter, system-ui, -apple-system, 'Segoe UI', Roboto, 'Helvetica Neue', Arial",
    "display": "Source Serif 4, Georgia, 'Times New Roman', serif",
    "mono": "Fira Code, 'Courier New', monospace"
  }
}
```

### 7.2 CSS variables (sample)
```css
:root{
  --lukhas-primary-1: #0B0F1A;
  --lukhas-matriz: #7A3BFF;
  --lukhas-identity: #0EA5A4;
  --lukhas-dev: #06B6D4;
  --space-md: 16px;
  --font-body: 16px;
}
```

### 7.3 Sample microcopy for heroes
- `lukhas.ai`: “Where digital minds learn to explain themselves. Experience MΛTRIZ — cognitive DNA for explainable AI.”  
- `lukhas.dev`: “Build a reasoning chain in 5 minutes. Try the Quickstart.”  
- `lukhas.com`: “Transparent AI. Trusted in production. Request an enterprise audit pack.”

### 7.4 Sample evidence block (markdown)
```md
## Evidence
- **Claim:** P95 reasoning latency < 250ms  
  **Proof:** release_artifacts/perf/2025-10-26-matriz-smoke.json (signed, hashed) — verified by @web-architect (2025-10-27)
- **Claim:** Guardian Compliance 99.7%  
  **Proof:** release_artifacts/audit/guardian-compliance-2025-Q3.pdf
```

---

## Final notes — enforcement culture

- **Treat the brand doc as code** — version it, require PRs for changes, and attach design-token diffs to code PRs.  
- **Make evidence discoverable** — keep `release_artifacts` organized, auditable, and small (explainers + raw data + signed stamp).  
- **Iterate** — the Brand Guidelines are living. Schedule quarterly review and maintain changelog.

---

